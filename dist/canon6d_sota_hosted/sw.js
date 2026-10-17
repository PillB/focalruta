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
const VERSION='focalruta-9578ac5178e6';
const FILES={"404.html":"c9e6e0690f38","assets/app-icon.svg":"6c706d09c51c","assets/hosted.css":"d054a93ced80","assets/icon-192.png":"6ccd0d22a9f8","assets/icon-512.png":"b0089189bd88","assets/icon-maskable-192.png":"1d97339252be","assets/icon-maskable-512.png":"ca2821b508c7","challenges/arquitectura-en-foco/field-card.html":"e6dc816c9885","challenges/arquitectura-en-foco/index.html":"210b9862dcea","challenges/arquitectura-en-foco/iphone-maps.html":"dcf00bc64b53","challenges/arquitectura-en-foco/maps/barranco-tour-1.geojson":"8eb8bf0ce285","challenges/arquitectura-en-foco/maps/barranco-tour-1.html":"7c75f80f02bf","challenges/arquitectura-en-foco/maps/barranco-tour-1.kml":"1ec0eb8380c3","challenges/arquitectura-en-foco/maps/barranco-tour-2.geojson":"9ac1b94d578d","challenges/arquitectura-en-foco/maps/barranco-tour-2.html":"088fa7b5e66c","challenges/arquitectura-en-foco/maps/barranco-tour-2.kml":"c5030a608ade","challenges/arquitectura-en-foco/maps/barranco-tour-3.geojson":"c631cf89a252","challenges/arquitectura-en-foco/maps/barranco-tour-3.html":"df7cf71ac5c5","challenges/arquitectura-en-foco/maps/barranco-tour-3.kml":"f61a985b4f0d","challenges/arquitectura-en-foco/maps/jesus-maria.geojson":"99fec02d468f","challenges/arquitectura-en-foco/maps/jesus-maria.html":"145f27854a2c","challenges/arquitectura-en-foco/maps/jesus-maria.kml":"ecaa6d2d4c63","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.geojson":"2a1086530c8a","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.html":"30335aabaefb","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.kml":"36eaa14112f4","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.geojson":"1eafde54186c","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.html":"8b8708a0f138","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.kml":"9614d52ef075","challenges/arquitectura-en-foco/maps/lima-tour-1.geojson":"1caed483014e","challenges/arquitectura-en-foco/maps/lima-tour-1.html":"a5010bcefe78","challenges/arquitectura-en-foco/maps/lima-tour-1.kml":"ab67e93a405b","challenges/arquitectura-en-foco/maps/lima-tour-2.geojson":"80acd60926e4","challenges/arquitectura-en-foco/maps/lima-tour-2.html":"862b1dc9fcbf","challenges/arquitectura-en-foco/maps/lima-tour-2.kml":"5aca494779b1","challenges/arquitectura-en-foco/maps/lima-tour-3.geojson":"561799ef58f8","challenges/arquitectura-en-foco/maps/lima-tour-3.html":"c24e4034a294","challenges/arquitectura-en-foco/maps/lima-tour-3.kml":"d7b720e12dab","challenges/arquitectura-en-foco/maps/miraflores-tour-1.geojson":"acc4038a7b07","challenges/arquitectura-en-foco/maps/miraflores-tour-1.html":"63af330db45f","challenges/arquitectura-en-foco/maps/miraflores-tour-1.kml":"a5d4af426b7d","challenges/arquitectura-en-foco/maps/miraflores-tour-2.geojson":"f1fb7c3d5e10","challenges/arquitectura-en-foco/maps/miraflores-tour-2.html":"c3d24cbe3838","challenges/arquitectura-en-foco/maps/miraflores-tour-2.kml":"8357fe8822c6","challenges/arquitectura-en-foco/maps/miraflores-tour-3.geojson":"37b085c5fa91","challenges/arquitectura-en-foco/maps/miraflores-tour-3.html":"549587942b0b","challenges/arquitectura-en-foco/maps/miraflores-tour-3.kml":"0e7786a51a72","challenges/arquitectura-en-foco/maps/miraflores-tour-4.geojson":"09045d831213","challenges/arquitectura-en-foco/maps/miraflores-tour-4.html":"3d5df49052b6","challenges/arquitectura-en-foco/maps/miraflores-tour-4.kml":"21085e0883ab","challenges/arquitectura-en-foco/maps/miraflores-tour-5.geojson":"37da8cf4a0ff","challenges/arquitectura-en-foco/maps/miraflores-tour-5.html":"a32326bd1017","challenges/arquitectura-en-foco/maps/miraflores-tour-5.kml":"b376e74a517c","challenges/arquitectura-en-foco/maps/miraflores-tour-6.geojson":"187e48e77445","challenges/arquitectura-en-foco/maps/miraflores-tour-6.html":"10e43c7ee50b","challenges/arquitectura-en-foco/maps/miraflores-tour-6.kml":"b2da352d8d75","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.geojson":"20cd78546b98","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.html":"13424bdfcb4b","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.kml":"3c2aa33ea5cf","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.geojson":"c637e069d6c3","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.html":"b8e046431ae9","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.kml":"f937f846d6ef","challenges/arquitectura-en-foco/maps/rimac.geojson":"14d1a9f8c663","challenges/arquitectura-en-foco/maps/rimac.html":"ec5aafac6afb","challenges/arquitectura-en-foco/maps/rimac.kml":"dc557d969285","challenges/arquitectura-en-foco/maps/san-borja-tour-1.geojson":"da2a4064ac6f","challenges/arquitectura-en-foco/maps/san-borja-tour-1.html":"67fcb388dd04","challenges/arquitectura-en-foco/maps/san-borja-tour-1.kml":"085bebf9c27d","challenges/arquitectura-en-foco/maps/san-borja-tour-2.geojson":"752162a2f6ea","challenges/arquitectura-en-foco/maps/san-borja-tour-2.html":"572401afffe6","challenges/arquitectura-en-foco/maps/san-borja-tour-2.kml":"c2947f4b5562","challenges/arquitectura-en-foco/maps/san-borja-tour-3.geojson":"84a5f067b619","challenges/arquitectura-en-foco/maps/san-borja-tour-3.html":"840efe165865","challenges/arquitectura-en-foco/maps/san-borja-tour-3.kml":"e394e9a33b1f","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.geojson":"96cf34cd1e6a","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.html":"d1bd893b7da2","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.kml":"b4f4271bc001","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.geojson":"eea9cab37739","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.html":"7e4e75be13f4","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.kml":"a36eebfa5f70","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.geojson":"bf2eb2b8e969","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.html":"fef1da007529","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.kml":"cdfceee39be5","challenges/arquitectura-en-foco/maps/santiago-de-surco.geojson":"091dec8ccade","challenges/arquitectura-en-foco/maps/santiago-de-surco.html":"ee1783c83918","challenges/arquitectura-en-foco/maps/santiago-de-surco.kml":"09b3799dcf50","challenges/arquitectura-en-foco/wiki-tecnicas.html":"059a7c90cf9c","data/architecture/candidates.json":"becdd116bd62","data/architecture/geography.json":"e3e74f6c4e4b","data/architecture/learning.json":"dd044eb8e252","data/architecture/photographers.json":"e2d950a587c3","data/architecture/ranking.json":"b5c3070750fb","data/architecture/routes.json":"9f545c1f74af","data/architecture/scene_dossier_schema.json":"0a76f5fd2108","data/architecture/sources.json":"288fb255cbe6","data/architecture/style_discoveries.json":"ddd327123b32","data/plans.json":"04ed789b72c2","data/plans_embedded.js":"75d8e47aed72","diagrams-webp/composition_capas.webp":"b590343634b3","diagrams-webp/composition_enmarcado.webp":"a79c7caf7348","diagrams-webp/composition_espacio_neg.webp":"8246608cb0e5","diagrams-webp/composition_minimalismo.webp":"123cfb5af991","diagrams-webp/composition_perspectiva.webp":"be657fb9b963","diagrams-webp/composition_punto_interes.webp":"3ee865720627","diagrams-webp/composition_simetria.webp":"43a54f948030","diagrams-webp/composition_tercios.webp":"4ec04562d13d","diagrams-webp/lens_comparison_25cm.webp":"09fda4abf91b","diagrams-webp/lens_comparison_40cm.webp":"d04998859db0","diagrams-webp/lens_comparison_60cm.webp":"0ff0f2dd7726","diagrams-webp/plan_a_A01_dog.webp":"701c1ef03a7e","diagrams-webp/plan_a_A01_human.webp":"2d8fbeb58c78","diagrams-webp/plan_a_A02_dog.webp":"624d91588b8b","diagrams-webp/plan_a_A02_human.webp":"1df27569c99b","diagrams-webp/plan_a_A03_dog.webp":"440a8beba7d7","diagrams-webp/plan_a_A03_human.webp":"e8598e1f1e58","diagrams-webp/plan_a_A04_dog.webp":"1078c6dcc56b","diagrams-webp/plan_a_A04_human.webp":"aab1c139dfc6","diagrams-webp/plan_a_A05_dog.webp":"f7fbb70e9b52","diagrams-webp/plan_a_A05_human.webp":"7a3cebb3d165","diagrams-webp/plan_a_A06_dog.webp":"12207345003e","diagrams-webp/plan_a_A06_human.webp":"8d4e53001543","diagrams-webp/plan_a_A07_dog.webp":"b95d0530f841","diagrams-webp/plan_a_A07_human.webp":"b77ee5e5d1f3","diagrams-webp/plan_a_A08_dog.webp":"972e586ce35f","diagrams-webp/plan_a_A08_human.webp":"c7cfa999a73b","diagrams-webp/plan_a_A09_dog.webp":"03c8069ee977","diagrams-webp/plan_a_A09_human.webp":"4aa068a6204e","diagrams-webp/plan_a_A10_dog.webp":"0f4ed58e15d6","diagrams-webp/plan_a_A10_human.webp":"ebaf05acf1a0","diagrams-webp/plan_b_B01_dog.webp":"4aa19042744b","diagrams-webp/plan_b_B01_human.webp":"5e1bdde99f18","diagrams-webp/plan_b_B02_dog.webp":"91d7f875b454","diagrams-webp/plan_b_B02_human.webp":"6fd56ed1b838","diagrams-webp/plan_b_B03_dog.webp":"a03e1f73e338","diagrams-webp/plan_b_B03_human.webp":"de0e21f4562e","diagrams-webp/plan_b_B04_dog.webp":"db41711a376d","diagrams-webp/plan_b_B04_human.webp":"66d2e02c8abb","diagrams-webp/plan_b_B05_dog.webp":"eea79ee5b520","diagrams-webp/plan_b_B05_human.webp":"abecedbdd9ff","diagrams-webp/plan_b_B06_dog.webp":"71864e6fc4e4","diagrams-webp/plan_b_B06_human.webp":"e899cd34eeca","diagrams-webp/plan_b_B07_dog.webp":"85e43f3f7765","diagrams-webp/plan_b_B07_human.webp":"aa83e6c887c5","diagrams-webp/plan_b_B08_dog.webp":"c31594cd0f81","diagrams-webp/plan_b_B08_human.webp":"05715763abb8","diagrams-webp/plan_b_B09_dog.webp":"27b00502baa6","diagrams-webp/plan_b_B09_human.webp":"b13f0026ce64","diagrams-webp/plan_b_B10_dog.webp":"d2d63775e831","diagrams-webp/plan_b_B10_human.webp":"c6ab868770d3","diagrams-webp/plan_c_C01_dog.webp":"cf504e083ca0","diagrams-webp/plan_c_C01_human.webp":"ddcc661aceec","diagrams-webp/plan_c_C02_dog.webp":"fc0baca7b74d","diagrams-webp/plan_c_C02_human.webp":"8095fb33af3d","diagrams-webp/plan_c_C03_dog.webp":"7fb62b12beea","diagrams-webp/plan_c_C03_human.webp":"f440339177d5","diagrams-webp/plan_c_C04_dog.webp":"af10b5f446f3","diagrams-webp/plan_c_C04_human.webp":"8c4c3c685285","diagrams-webp/plan_c_C05_dog.webp":"2e3a318aeafe","diagrams-webp/plan_c_C05_human.webp":"691d6997e8da","diagrams-webp/plan_c_C06_dog.webp":"7904a62d87c7","diagrams-webp/plan_c_C06_human.webp":"b9fb4ebf3749","diagrams-webp/plan_c_C07_dog.webp":"2f7c7fba3672","diagrams-webp/plan_c_C07_human.webp":"6187011c7de7","diagrams-webp/plan_c_C08_dog.webp":"a377dceff905","diagrams-webp/plan_c_C08_human.webp":"170dc777bee8","diagrams-webp/plan_c_C09_dog.webp":"86ed1a2a2e52","diagrams-webp/plan_c_C09_human.webp":"5db9d485a1a2","diagrams-webp/plan_c_C10_dog.webp":"ab32c6ef3581","diagrams-webp/plan_c_C10_human.webp":"97584fc37967","diagrams-webp/plan_d_D01_dog.webp":"0ee7ccf8a6b4","diagrams-webp/plan_d_D01_human.webp":"3039fe69d416","diagrams-webp/plan_d_D02_dog.webp":"f9673208f4cb","diagrams-webp/plan_d_D02_human.webp":"a0323d8f6485","diagrams-webp/plan_d_D03_dog.webp":"f75e5e600be2","diagrams-webp/plan_d_D03_human.webp":"d9f059ccad44","diagrams-webp/plan_d_D04_dog.webp":"696032b9e61f","diagrams-webp/plan_d_D04_human.webp":"da08e07d65f4","diagrams-webp/plan_d_D05_dog.webp":"3e636d7ea3a0","diagrams-webp/plan_d_D05_human.webp":"5ee4fb10f9d8","diagrams-webp/plan_d_D06_dog.webp":"0f041fa569a1","diagrams-webp/plan_d_D06_human.webp":"7dc8a0065363","diagrams-webp/plan_d_D07_dog.webp":"fba9408e2dfa","diagrams-webp/plan_d_D07_human.webp":"fd42a4db50ba","diagrams-webp/plan_d_D08_dog.webp":"467f53f9ad85","diagrams-webp/plan_d_D08_human.webp":"c8a4728d0303","diagrams-webp/plan_d_D09_dog.webp":"8b1a2613ecc8","diagrams-webp/plan_d_D09_human.webp":"cfdd01b79d37","diagrams-webp/plan_d_D10_dog.webp":"592628b5e3a4","diagrams-webp/plan_d_D10_human.webp":"4b763b0e86b0","diagrams-webp/plan_e_E01_dog.webp":"cfb5bbdbcaf2","diagrams-webp/plan_e_E01_human.webp":"a618d160852c","diagrams-webp/plan_e_E02_dog.webp":"47367f066af4","diagrams-webp/plan_e_E02_human.webp":"d939b09ebefe","diagrams-webp/plan_e_E03_dog.webp":"8436ac132e0d","diagrams-webp/plan_e_E03_human.webp":"ffd9557a08bc","diagrams-webp/plan_e_E04_dog.webp":"5b98be321b60","diagrams-webp/plan_e_E04_human.webp":"3a55e72479b8","diagrams-webp/plan_e_E05_dog.webp":"e436b3ef0d44","diagrams-webp/plan_e_E05_human.webp":"dd5de1fc5751","diagrams-webp/plan_e_E06_dog.webp":"8deae87b4c91","diagrams-webp/plan_e_E06_human.webp":"1ed0f51c1118","diagrams-webp/plan_e_E07_dog.webp":"6af5b884f80c","diagrams-webp/plan_e_E07_human.webp":"92073b432ded","diagrams-webp/plan_e_E08_dog.webp":"547ce285e426","diagrams-webp/plan_e_E08_human.webp":"60437b5e00d5","diagrams-webp/plan_e_E09_dog.webp":"f5a65b71648f","diagrams-webp/plan_e_E09_human.webp":"1ec6c33b17ff","diagrams-webp/plan_e_E10_dog.webp":"ab633a0bf591","diagrams-webp/plan_e_E10_human.webp":"52c66b55c423","diagrams-webp/plan_f_F01_dog.webp":"bb7fa0de601b","diagrams-webp/plan_f_F01_human.webp":"858110ee1161","diagrams-webp/plan_f_F02_dog.webp":"6df7a759f429","diagrams-webp/plan_f_F02_human.webp":"d3476a267193","diagrams-webp/plan_f_F03_dog.webp":"d98c9bf68c99","diagrams-webp/plan_f_F03_human.webp":"f28d428b76a0","diagrams-webp/plan_f_F04_dog.webp":"605086f6e6a9","diagrams-webp/plan_f_F04_human.webp":"833288de62ab","diagrams-webp/plan_f_F05_dog.webp":"23b5a581787e","diagrams-webp/plan_f_F05_human.webp":"91afc6c548a6","diagrams-webp/plan_f_F06_dog.webp":"2386d2514603","diagrams-webp/plan_f_F06_human.webp":"b5df4051181e","diagrams-webp/plan_f_F07_dog.webp":"8eaa106bedb3","diagrams-webp/plan_f_F07_human.webp":"0a72a7c9526c","diagrams-webp/plan_f_F08_dog.webp":"fa5fdcc36577","diagrams-webp/plan_f_F08_human.webp":"7dc687ae280d","diagrams-webp/plan_f_F09_dog.webp":"ecdf75730c65","diagrams-webp/plan_f_F09_human.webp":"5f937d929d06","diagrams-webp/plan_f_F10_dog.webp":"fc0ad27c2774","diagrams-webp/plan_f_F10_human.webp":"824a4a4f26a9","field_card.html":"32ccf751f41d","index.html":"9447c2f617d4","manifest.webmanifest":"dbfa3ff2167b","plans/plan_a.html":"b25128a39159","plans/plan_b.html":"c71516bfebd8","plans/plan_c.html":"f7eeca3211dd","plans/plan_d.html":"a447941bc966","plans/plan_e.html":"b60a87e6ebe6","plans/plan_f.html":"33d87eb48742"};
const CORE=["index.html","assets/hosted.css","data/plans_embedded.js","manifest.webmanifest","field_card.html","challenges/arquitectura-en-foco/index.html","challenges/arquitectura-en-foco/iphone-maps.html","data/architecture/learning.json","data/architecture/ranking.json","data/architecture/routes.json","assets/icon-192.png","assets/icon-512.png","assets/icon-maskable-192.png","assets/icon-maskable-512.png","assets/app-icon.svg"];
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
    return (known(path)&&await kept(path))||await kept('index.html')||Response.error();
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
