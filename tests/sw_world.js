// A small world for the service worker tests (tests/test_service_worker.py):
// Cache Storage shared by every worker loaded into it, a server whose files can
// be redeployed, a browser HTTP cache that answers `default` requests with
// whatever it kept, and a switch to take the network away. Workers run in a
// vm context with only what a worker gets.
'use strict';
const vm = require('vm'), fs = require('fs'), crypto = require('crypto');

const SCOPE = 'https://pillb.github.io/focalruta/';
const rev = bytes => crypto.createHash('sha256').update(bytes).digest('hex').slice(0, 12);
const pathOfKey = url => { const u = new URL(url); return u.pathname.slice(new URL(SCOPE).pathname.length) || 'index.html'; };

class FakeCache {
  constructor(world) { this.world = world; this.entries = []; }
  find(request, options = {}) {
    const url = new URL(typeof request === 'string' ? request : request.url, SCOPE);
    if (options.ignoreSearch) url.search = '';
    url.hash = '';
    return this.entries.filter(e => {
      const stored = new URL(e.url); stored.hash = '';
      if (options.ignoreSearch) stored.search = '';
      return stored.href === url.href;
    });
  }
  async match(request, options) { const hit = this.find(request, options)[0]; return hit ? new Response(hit.body, hit.init) : undefined; }
  async put(request, response) {
    const url = new URL(typeof request === 'string' ? request : request.url, SCOPE).href;
    const body = Buffer.from(await response.arrayBuffer());
    this.entries = this.entries.filter(e => e.url !== url);
    this.entries.push({ url, body, init: { status: response.status, headers: { 'content-type': response.headers.get('content-type') || '' } } });
  }
  // Like the real addAll: plain requests, which the HTTP cache may answer.
  async addAll(urls) { for (const u of urls) { const res = await this.world.fetch(u); if (!res.ok) throw new TypeError('addAll: ' + res.status); await this.put(u, res); } }
  async keys() { return this.entries.map(e => new Request(e.url)); }
  async delete(request, options) { const before = this.entries.length; const gone = new Set(this.find(request, options)); this.entries = this.entries.filter(e => !gone.has(e)); return this.entries.length < before; }
}

class World {
  constructor() { this.stores = new Map(); this.server = {}; this.httpCache = {}; this.online = true; this.requests = []; }
  // Put `files` ({path: text}) on the server, as a deploy does; returns their revisions.
  deploy(files) { this.server = Object.fromEntries(Object.entries(files).map(([p, t]) => [p, Buffer.from(t)])); return this.revisions(); }
  revisions() { return Object.fromEntries(Object.entries(this.server).map(([p, b]) => [p, rev(b)])); }
  // What the browser's HTTP cache keeps from the files on the server now (max-age=600).
  rememberHttp() { for (const [p, b] of Object.entries(this.server)) this.httpCache[SCOPE + p] = b; this.httpCache[SCOPE] = this.server['index.html']; }
  get caches() {
    const w = this;
    return {
      async open(name) { if (!w.stores.has(name)) w.stores.set(name, new FakeCache(w)); return w.stores.get(name); },
      async keys() { return [...w.stores.keys()]; },
      async delete(name) { return w.stores.delete(name); },
      async has(name) { return w.stores.has(name); },
      async match(request, options) { for (const c of w.stores.values()) { const hit = await c.match(request, options); if (hit) return hit; } },
    };
  }
  async fetch(input, init = {}) {
    const request = typeof input === 'string' ? new Request(new URL(input, SCOPE)) : input;
    const mode = init.cache || 'default', url = new URL(request.url); url.hash = '';
    this.requests.push({ url: url.href, mode });
    if (!this.online) throw new TypeError('Failed to fetch');
    const bare = url.origin + url.pathname;
    const stale = mode === 'default' && this.httpCache[url.href];
    const path = pathOfKey(bare);
    const body = stale || this.server[path.endsWith('/') ? path + 'index.html' : path];
    if (!body) return new Response('not found', { status: 404 });
    return new Response(body, { status: 200, headers: { 'content-type': 'application/octet-stream' } });
  }
  // Load a worker: either a filled-in sw.js, or the template filled with this world's files.
  load(source) {
    const listeners = {}, world = this;
    const self = {
      registration: { scope: SCOPE },
      addEventListener: (type, fn) => { (listeners[type] = listeners[type] || []).push(fn); },
      skipWaiting: async () => {}, clients: { claim: async () => {} },
      location: new URL(SCOPE + 'sw.js'),
    };
    const context = { self, caches: world.caches, fetch: (i, o) => world.fetch(i, o), crypto: globalThis.crypto, URL, Request, Response,
      setTimeout, clearTimeout, console, location: self.location };
    vm.createContext(context);
    vm.runInContext(source, context);
    const dispatch = async (type, event) => {
      const waits = [];
      let response;
      Object.assign(event, { waitUntil: p => waits.push(p), respondWith: p => { response = p; } });
      for (const fn of listeners[type] || []) fn(event);
      const answer = response ? await response : undefined;
      await Promise.all(waits);
      return answer;
    };
    return {
      install: () => dispatch('install', {}),
      activate: () => dispatch('activate', {}),
      async upgrade() { await this.install(); await this.activate(); },
      // A request a page makes; resolves to {from, body} where from is 'worker' or 'network'.
      async request(path, mode = 'no-cors') {
        const request = new Request(new URL(path, SCOPE));
        Object.defineProperty(request, 'mode', { value: mode });
        const before = world.requests.length;
        const answer = await dispatch('fetch', { request });
        let res = answer;
        // A request the worker leaves alone goes to the network, which may be gone.
        if (!res) try { res = await world.fetch(request); } catch (e) { return { error: String(e) }; }
        if (res.type === 'error') return { error: 'the worker answered with a network error' };
        const location = res.headers.get('location');
        return { body: Buffer.from(await res.arrayBuffer()).toString(), status: res.status, network: world.requests.length > before,
          ...(location ? { location } : {}) };
      },
      async message(data) {
        const posted = [];
        await dispatch('message', { data, source: { postMessage: m => posted.push(m) } });
        return posted;
      },
    };
  }
  // The worker template filled with `files` ({path: text}); FOCALRUTA_SW_TEMPLATE
  // points at another template, e.g. an older one, to show what it got wrong.
  template(files, core) {
    const revisions = Object.fromEntries(Object.entries(files).map(([p, t]) => [p, rev(Buffer.from(t))]));
    const source = process.env.FOCALRUTA_SW_TEMPLATE || require('path').join(__dirname, '..', 'assets', 'sw.template.js');
    return fs.readFileSync(source, 'utf8').replace('__CACHE_VERSION__', 'focalruta-' + rev(JSON.stringify(revisions)))
      .replace('__FILES__', JSON.stringify(revisions)).replace('__CORE__', JSON.stringify(core));
  }
  cacheReport() {
    const out = {};
    for (const [name, cache] of this.stores) out[name] = cache.entries.map(e => new URL(e.url).pathname.replace(new URL(SCOPE).pathname, '') + new URL(e.url).search).sort();
    return out;
  }
}

module.exports = { World, SCOPE, rev };
