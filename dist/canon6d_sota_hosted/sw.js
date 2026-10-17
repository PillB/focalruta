/* FocalRuta service worker. build_dual_release.py fills in the version, which
   changes whenever anything the site serves changes.
   SHELL   precached on install: the first visit leaves the home page, the field
           card and the architecture guide usable offline.
   RUNTIME whatever the reader opened, served from cache and refreshed online.
   PACK    what the reader chose to keep for the field (requirement V07): the six
           plan pages and every diagram. A new version copies the previous pack
           before deleting old caches, so a deploy never empties a phone that was
           prepared for a session without signal. */
const VERSION='focalruta-30f2ba107b11';
const SHELL=VERSION+'-shell',RUNTIME=VERSION+'-runtime',PACK=VERSION+'-pack';
const CORE=['./','./index.html','./assets/hosted.css','./data/plans_embedded.js','./manifest.webmanifest','./field_card.html','./challenges/arquitectura-en-foco/index.html','./challenges/arquitectura-en-foco/iphone-maps.html','./data/architecture/learning.json','./data/architecture/ranking.json','./data/architecture/routes.json','./assets/icon-192.png','./assets/icon-512.png','./assets/icon-maskable-192.png','./assets/icon-maskable-512.png','./assets/app-icon.svg'];
const PACK_LIMIT=300,PACK_PARALLEL=4;

function sameOrigin(url){try{return new URL(url,self.location.href).origin===self.location.origin}catch(_){return false}}

async function fromCache(request){
  for(const name of [RUNTIME,PACK,SHELL]){const hit=await (await caches.open(name)).match(request);if(hit)return hit;}
  return undefined;
}

async function carryPacks(){
  const names=await caches.keys(),pack=await caches.open(PACK);
  for(const name of names.filter(n=>n.endsWith('-pack')&&n!==PACK)){
    const old=await caches.open(name);
    for(const request of await old.keys()){const kept=await old.match(request);if(kept)await pack.put(request,kept);}
  }
  await Promise.all(names.filter(n=>![SHELL,RUNTIME,PACK].includes(n)).map(n=>caches.delete(n)));
}

async function warm(urls){
  const cache=await caches.open(RUNTIME);
  await Promise.all(urls.map(u=>cache.match(u).then(hit=>hit||fetch(u).then(x=>{if(x.ok)return cache.put(u,x)}).catch(()=>{}))));
}

async function pack(urls,client){
  const cache=await caches.open(PACK),queue=urls.slice();let done=0,failed=0;
  const report=()=>client&&client.postMessage({type:'pack-progress',done,failed,total:urls.length});
  async function worker(){
    while(queue.length){
      const url=queue.shift();
      try{const res=await fetch(url,{cache:'no-cache'});if(res.ok)await cache.put(url,res);else failed++;}catch(_){failed++;}
      done++;if(done%10===0||done===urls.length)report();
    }
  }
  await Promise.all(Array.from({length:PACK_PARALLEL},worker));
}

self.addEventListener('install',e=>e.waitUntil(caches.open(SHELL).then(c=>c.addAll(CORE)).then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(carryPacks().then(()=>self.clients.claim())));
self.addEventListener('message',e=>{
  const d=e.data;
  if(!d||!Array.isArray(d.urls))return;
  const urls=d.urls.filter(sameOrigin).map(u=>new URL(u,self.location.href).href);
  if(d.type==='warm')e.waitUntil(warm(urls.filter(u=>/\.(?:webp|html)$/.test(new URL(u).pathname)).slice(0,40)));
  if(d.type==='pack')e.waitUntil(pack(urls.slice(0,PACK_LIMIT),e.source));
});
self.addEventListener('fetch',e=>{
  const r=e.request;
  if(r.method!=='GET'||!sameOrigin(r.url))return;
  const u=new URL(r.url);
  if(r.mode==='navigate'){
    e.respondWith(fetch(r).then(x=>{if(x.ok){const copy=x.clone();caches.open(RUNTIME).then(c=>c.put(r,copy));}return x})
      .catch(async()=>await fromCache(r)||await fromCache(new URL(u.pathname.endsWith('/')?u.pathname+'index.html':u.pathname,self.location.origin).href)||await fromCache('./index.html')));
    return;
  }
  if(/\.(?:webp|png|svg|css|js|json|html)$/.test(u.pathname)){
    e.respondWith(fromCache(r).then(cached=>{
      const fresh=fetch(r).then(x=>{if(x.ok){const copy=x.clone();caches.open(RUNTIME).then(c=>c.put(r,copy));}return x}).catch(()=>cached);
      return cached||fresh;
    }));
  }
});
