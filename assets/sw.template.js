/* FocalRuta service worker. scripts/service_worker.py fills in FILES, every
   file the worker may keep, each with the first 12 hex digits of its SHA-256,
   and CORE, the files kept on install.
   Every copy is stored under its revision (path?__rev=…) and its bytes are
   checked against FILES when it arrives, so:
   - a page is never served a copy from another build: not one the HTTP cache
     kept (Pages sends max-age=600), not one a CDN node still had, and not an
     older worker's;
   - an upgrade keeps what the reader already has: files that did not change
     are not fetched again, and an older copy stays as the offline fallback
     until its replacement has arrived whole;
   - the files the reader kept for the field (requirement V07) are brought up
     to date on install, and the field card can ask how current they are.
   SHELL    kept on install: home page, field card and architecture guide.
   PACK     what the reader chose to keep for the field: plans and diagrams.
   RUNTIME  whatever else the reader opened.
   Caches of older FocalRuta workers are adopted on install and deleted on
   activate; other sites on this origin (pillb.github.io) are never touched. */
const VERSION='__CACHE_VERSION__';
const FILES=__FILES__;
const CORE=__CORE__;
const SHELL='focalruta-shell',PACK='focalruta-pack',RUNTIME='focalruta-runtime',OURS=[SHELL,PACK,RUNTIME];
const LEGACY=/^(?:focalruta-[0-9a-f]{12}|canon6d-sota-v\d+)-(?:shell|runtime|pack)$/;
const PACK_LIMIT=300,PARALLEL=4,PACK_BUDGET_MS=90000,ANY={ignoreVary:true};
const SCOPE=self.registration.scope,opened={};
const open=name=>opened[name]||(opened[name]=caches.open(name));

function pathOf(url){
  try{
    const u=new URL(url,SCOPE);u.search='';u.hash='';
    if(!u.href.startsWith(SCOPE))return null;
    const path=u.href.slice(SCOPE.length);
    return path===''||path.endsWith('/')?path+'index.html':path;
  }catch(_){return null}
}
const known=path=>path!==null&&Object.prototype.hasOwnProperty.call(FILES,path);
const keyOf=(path,rev)=>SCOPE+path+'?__rev='+rev;
const revOf=key=>new URL(key).searchParams.get('__rev');

async function digest(res){
  const bytes=new Uint8Array(await crypto.subtle.digest('SHA-256',await res.clone().arrayBuffer()));
  return Array.from(bytes.slice(0,6),b=>b.toString(16).padStart(2,'0')).join('');
}
async function pool(items,job){
  const queue=items.slice();
  await Promise.all(Array.from({length:PARALLEL},async()=>{while(queue.length)await job(queue.shift());}));
}

// This build's copy of a file, from whichever of our caches has it.
async function current(path,rev=FILES[path]){
  for(const name of OURS){const hit=await (await open(name)).match(keyOf(path,rev),ANY);if(hit)return hit;}
}
// Any copy of the file, for when the network is gone.
async function older(path){
  for(const name of [PACK,SHELL,RUNTIME]){const hit=await (await open(name)).match(SCOPE+path,{ignoreSearch:true,ignoreVary:true});if(hit)return hit;}
}
// This build's bytes from the server, or nothing. no-cache revalidates past the HTTP cache.
async function download(path){
  try{const res=await fetch(SCOPE+path,{cache:'no-cache'});if(res.ok&&await digest(res)===FILES[path])return res;}catch(_){}
}
// Make sure cache `name` holds this build's copy: copied from another cache, or downloaded.
async function keep(name,path){
  const cache=await open(name),key=keyOf(path,FILES[path]);
  if(await cache.match(key,ANY))return true;
  const res=await current(path)||await download(path);
  if(!res)return false;
  await cache.put(key,res);return true;
}
// Store a response the page fetched anyway, when it is this build's file and we lack it.
async function remember(path,res){
  if(await current(path)||await digest(res)!==FILES[path])return;
  await (await open(RUNTIME)).put(keyOf(path,FILES[path]),res);
}

async function adopt(){
  for(const name of (await caches.keys()).filter(n=>LEGACY.test(n))){
    const old=await caches.open(name),into=await open(name.endsWith('-pack')?PACK:name.endsWith('-shell')?SHELL:RUNTIME);
    for(const request of await old.keys()){
      const path=pathOf(request.url),res=known(path)&&await old.match(request,ANY);
      if(res&&res.ok)await into.put(keyOf(path,await digest(res)),res);
    }
  }
}
async function refreshPack(){
  const pack=await open(PACK);
  const paths=[...new Set((await pack.keys()).map(r=>pathOf(r.url)).filter(known))];
  await pool(paths,path=>keep(PACK,path));
}
async function install(){
  await adopt();
  const kept=await Promise.all(CORE.map(path=>keep(SHELL,path)));
  // Without the whole shell, stay on the current worker and try again on the next visit.
  if(kept.includes(false))throw new Error('FocalRuta '+VERSION+': the shell did not arrive whole');
  let timer;
  await Promise.race([refreshPack(),new Promise(done=>{timer=setTimeout(done,PACK_BUDGET_MS)})]);
  clearTimeout(timer);
}
async function prune(){
  await Promise.all((await caches.keys()).filter(n=>LEGACY.test(n)).map(n=>caches.delete(n)));
  const entries=[];
  for(const name of OURS){const cache=await open(name);for(const r of await cache.keys())entries.push({name,cache,r,path:pathOf(r.url),rev:revOf(r.url)});}
  const isFresh=x=>known(x.path)&&x.rev===FILES[x.path];
  const fresh=new Set(entries.filter(isFresh).map(x=>x.path)),fallback=new Set();
  const held=new Set(entries.filter(x=>isFresh(x)&&x.name!==RUNTIME).map(x=>x.path));
  for(const x of entries){
    // A page the reader opened and then kept for the field needs one copy, not two.
    if(isFresh(x)&&!(x.name===RUNTIME&&held.has(x.path)))continue;
    // Keep one older copy of a file this build has not stored yet: offline, it beats nothing.
    if(known(x.path)&&x.rev&&!fresh.has(x.path)&&!fallback.has(x.path)){fallback.add(x.path);continue;}
    await x.cache.delete(x.r,ANY);
  }
}

async function pack(paths,client){
  let done=0,failed=0;
  const report=()=>client&&client.postMessage({type:'pack-progress',done,failed,total:paths.length});
  await pool(paths,async path=>{
    if(!await keep(PACK,path).catch(()=>false))failed++;
    done++;if(done%10===0||done===paths.length)report();
  });
}
async function packStatus(paths,client){
  let fresh=0,stale=0;
  for(const path of paths){if(await current(path))fresh++;else if(await older(path))stale++;}
  if(client)client.postMessage({type:'pack-status',total:paths.length,current:fresh,older:stale,missing:paths.length-fresh-stale});
}
async function warm(paths){
  await pool(paths,async path=>{if(!await current(path)){const res=await download(path);if(res)await (await open(RUNTIME)).put(keyOf(path,FILES[path]),res);}});
}

// The copy kept for `path`, this build's or an older one.
async function kept(path){return await current(path)||await older(path);}

async function navigate(e,r,path){
  try{
    // no-cache: revalidate with the server, so the HTTP cache cannot answer with the last build's page.
    const res=await fetch(r,{cache:'no-cache'});
    // A 404 or 5xx from a CDN node that has not caught up loses to the copy the reader kept.
    if(!res.ok)return (known(path)&&await kept(path))||res;
    if(known(path))e.waitUntil(remember(path,res.clone()).catch(()=>{}));
    return res;
  }catch(_){
    const hit=known(path)&&await kept(path);
    if(hit)return hit;
    // A page never kept here: send the reader to the home page, which says which one it was.
    // The home page's bytes under this URL would resolve its stylesheet, images and links
    // under this page's folder (live check of 56a6e97, M7).
    if(path!=='index.html'&&await kept('index.html'))return Response.redirect(SCOPE+'index.html?sin-conexion='+encodeURIComponent(path),302);
    return Response.error();
  }
}
async function asset(e,r,path){
  // A page from another build (an HTML copy the HTTP cache kept) names its own revision: give it that one.
  const wanted=new URL(r.url).searchParams.get('v')||FILES[path],ours=wanted===FILES[path];
  const hit=await current(path,wanted);
  if(hit)return hit;
  try{
    // This build's file is revalidated like a page; another build's is left to the HTTP cache, which may still hold it.
    const res=await fetch(r,ours?{cache:'no-cache'}:{});
    if(!res.ok)return await older(path)||res;
    if(ours)e.waitUntil(remember(path,res.clone()).catch(()=>{}));
    return res;
  }catch(_){
    return await older(path)||Response.error();
  }
}

self.addEventListener('install',e=>e.waitUntil(install().then(()=>self.skipWaiting())));
self.addEventListener('activate',e=>e.waitUntil(prune().then(()=>self.clients.claim())));
self.addEventListener('message',e=>{
  const d=e.data;
  if(!d||!Array.isArray(d.urls))return;
  const paths=[...new Set(d.urls.map(pathOf).filter(known))];
  if(d.type==='warm')e.waitUntil(warm(paths.slice(0,40)));
  if(d.type==='pack')e.waitUntil(pack(paths.slice(0,PACK_LIMIT),e.source));
  if(d.type==='pack-status')e.waitUntil(packStatus(paths.slice(0,PACK_LIMIT),e.source));
});
self.addEventListener('fetch',e=>{
  const r=e.request,path=r.method==='GET'?pathOf(r.url):null;
  // Other origins, other sites on this origin and anything not in this build go to the network untouched.
  if(path===null)return;
  if(r.mode==='navigate')e.respondWith(navigate(e,r,path));
  else if(known(path))e.respondWith(asset(e,r,path));
});
