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
const VERSION='focalruta-6a17136c714b';
const FILES={"404.html":"c9e6e0690f38","assets/app-icon.svg":"6c706d09c51c","assets/hosted.css":"02f8562a66e7","assets/icon-192.png":"6ccd0d22a9f8","assets/icon-512.png":"b0089189bd88","assets/icon-maskable-192.png":"1d97339252be","assets/icon-maskable-512.png":"ca2821b508c7","challenges/arquitectura-en-foco/field-card.html":"986b21b3e98a","challenges/arquitectura-en-foco/index.html":"38d5949ae7e3","challenges/arquitectura-en-foco/iphone-maps.html":"3af624a6bf96","challenges/arquitectura-en-foco/maps/barranco-tour-1.geojson":"72781bcdeb74","challenges/arquitectura-en-foco/maps/barranco-tour-1.html":"0b184cbf11b0","challenges/arquitectura-en-foco/maps/barranco-tour-1.kml":"1e74f2e6d4bf","challenges/arquitectura-en-foco/maps/barranco-tour-2.geojson":"63634a20a5d5","challenges/arquitectura-en-foco/maps/barranco-tour-2.html":"1f268cdc5a79","challenges/arquitectura-en-foco/maps/barranco-tour-2.kml":"1006958a55bb","challenges/arquitectura-en-foco/maps/barranco-tour-3.geojson":"672410b88a29","challenges/arquitectura-en-foco/maps/barranco-tour-3.html":"8595da9b13bb","challenges/arquitectura-en-foco/maps/barranco-tour-3.kml":"4ef942857e63","challenges/arquitectura-en-foco/maps/jesus-maria.geojson":"99fec02d468f","challenges/arquitectura-en-foco/maps/jesus-maria.html":"8e07988edbea","challenges/arquitectura-en-foco/maps/jesus-maria.kml":"ecaa6d2d4c63","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.geojson":"0abd660e11a1","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.html":"acbc2736cbd2","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.kml":"01b58c91a124","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.geojson":"1eafde54186c","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.html":"bdd088de14e5","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.kml":"9614d52ef075","challenges/arquitectura-en-foco/maps/lima-tour-1.geojson":"c683c76c32ce","challenges/arquitectura-en-foco/maps/lima-tour-1.html":"3b2aa99025f8","challenges/arquitectura-en-foco/maps/lima-tour-1.kml":"16a769fd46bd","challenges/arquitectura-en-foco/maps/lima-tour-2.geojson":"d96d3911ba28","challenges/arquitectura-en-foco/maps/lima-tour-2.html":"6b7e6e04fd02","challenges/arquitectura-en-foco/maps/lima-tour-2.kml":"da40cc119d8c","challenges/arquitectura-en-foco/maps/lima-tour-3.geojson":"59e21874a224","challenges/arquitectura-en-foco/maps/lima-tour-3.html":"1d3c12de9877","challenges/arquitectura-en-foco/maps/lima-tour-3.kml":"6e74e2a856b0","challenges/arquitectura-en-foco/maps/miraflores-tour-1.geojson":"1df0bc5f335a","challenges/arquitectura-en-foco/maps/miraflores-tour-1.html":"948b790e607f","challenges/arquitectura-en-foco/maps/miraflores-tour-1.kml":"2f0fe417c0b5","challenges/arquitectura-en-foco/maps/miraflores-tour-2.geojson":"af83618c4207","challenges/arquitectura-en-foco/maps/miraflores-tour-2.html":"2045a9776d3a","challenges/arquitectura-en-foco/maps/miraflores-tour-2.kml":"c51882ea202b","challenges/arquitectura-en-foco/maps/miraflores-tour-3.geojson":"7862377ed2f5","challenges/arquitectura-en-foco/maps/miraflores-tour-3.html":"188678bf2b91","challenges/arquitectura-en-foco/maps/miraflores-tour-3.kml":"41b37c1919ba","challenges/arquitectura-en-foco/maps/miraflores-tour-4.geojson":"8049d90fcd94","challenges/arquitectura-en-foco/maps/miraflores-tour-4.html":"79beb97ad18d","challenges/arquitectura-en-foco/maps/miraflores-tour-4.kml":"1bb0702bcb52","challenges/arquitectura-en-foco/maps/miraflores-tour-5.geojson":"37da8cf4a0ff","challenges/arquitectura-en-foco/maps/miraflores-tour-5.html":"98cb4f8675a4","challenges/arquitectura-en-foco/maps/miraflores-tour-5.kml":"b376e74a517c","challenges/arquitectura-en-foco/maps/miraflores-tour-6.geojson":"1a71b485432c","challenges/arquitectura-en-foco/maps/miraflores-tour-6.html":"c519a345978e","challenges/arquitectura-en-foco/maps/miraflores-tour-6.kml":"27a41c01797c","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.geojson":"3f43bbdf278c","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.html":"b06019bdf291","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.kml":"b89717c2dab4","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.geojson":"8feaa5605218","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.html":"2bc8ad6180bd","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.kml":"8fa49cf05097","challenges/arquitectura-en-foco/maps/rimac.geojson":"3fa19c71f12b","challenges/arquitectura-en-foco/maps/rimac.html":"c35d7b80e32a","challenges/arquitectura-en-foco/maps/rimac.kml":"864645640c35","challenges/arquitectura-en-foco/maps/san-borja-tour-1.geojson":"247c0749fc89","challenges/arquitectura-en-foco/maps/san-borja-tour-1.html":"b406b7cdf88a","challenges/arquitectura-en-foco/maps/san-borja-tour-1.kml":"5e7e4713e411","challenges/arquitectura-en-foco/maps/san-borja-tour-2.geojson":"20d3a030822f","challenges/arquitectura-en-foco/maps/san-borja-tour-2.html":"c121574708a5","challenges/arquitectura-en-foco/maps/san-borja-tour-2.kml":"4f864d8e4d79","challenges/arquitectura-en-foco/maps/san-borja-tour-3.geojson":"84a5f067b619","challenges/arquitectura-en-foco/maps/san-borja-tour-3.html":"11c55fcff6d3","challenges/arquitectura-en-foco/maps/san-borja-tour-3.kml":"e394e9a33b1f","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.geojson":"fc81fc1019f5","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.html":"f80411660301","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.kml":"a3a40e8c2142","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.geojson":"7c000660f5f5","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.html":"333e269fd1a5","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.kml":"6b054ab16d6a","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.geojson":"bf2eb2b8e969","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.html":"581cbe4cb01c","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.kml":"cdfceee39be5","challenges/arquitectura-en-foco/maps/santiago-de-surco.geojson":"08c1dc242706","challenges/arquitectura-en-foco/maps/santiago-de-surco.html":"a7eddcf8e0a3","challenges/arquitectura-en-foco/maps/santiago-de-surco.kml":"e98493bcc840","challenges/arquitectura-en-foco/wiki-tecnicas.html":"3ebce15997a8","data/architecture/candidates.json":"becdd116bd62","data/architecture/geography.json":"e3e74f6c4e4b","data/architecture/learning.json":"001856d9270a","data/architecture/photographers.json":"e2d950a587c3","data/architecture/ranking.json":"b5c3070750fb","data/architecture/ranking_es.json":"d00d2539afa4","data/architecture/routes.json":"64a5a0af136a","data/architecture/scene_dossier_schema.json":"0a76f5fd2108","data/architecture/sources.json":"288fb255cbe6","data/architecture/style_discoveries.json":"ddd327123b32","data/plans.json":"03029a8656b7","data/plans_embedded.js":"43a7d16094a3","diagrams-webp/composition_capas.webp":"b590343634b3","diagrams-webp/composition_enmarcado.webp":"a79c7caf7348","diagrams-webp/composition_espacio_neg.webp":"8246608cb0e5","diagrams-webp/composition_minimalismo.webp":"123cfb5af991","diagrams-webp/composition_perspectiva.webp":"be657fb9b963","diagrams-webp/composition_punto_interes.webp":"3ee865720627","diagrams-webp/composition_simetria.webp":"43a54f948030","diagrams-webp/composition_tercios.webp":"4ec04562d13d","diagrams-webp/lens_comparison_25cm.webp":"09fda4abf91b","diagrams-webp/lens_comparison_40cm.webp":"d04998859db0","diagrams-webp/lens_comparison_60cm.webp":"0ff0f2dd7726","diagrams-webp/plan_a_A01_dog.webp":"1d6c83d5b09e","diagrams-webp/plan_a_A01_human.webp":"e3ae51e02ccd","diagrams-webp/plan_a_A02_dog.webp":"eb3d84be76d9","diagrams-webp/plan_a_A02_human.webp":"9b7a484e4c5f","diagrams-webp/plan_a_A03_dog.webp":"a80b0b51221d","diagrams-webp/plan_a_A03_human.webp":"2cd5a83ddb5d","diagrams-webp/plan_a_A04_dog.webp":"cbcf76156503","diagrams-webp/plan_a_A04_human.webp":"69e2ac0ad0da","diagrams-webp/plan_a_A05_dog.webp":"b78129683898","diagrams-webp/plan_a_A05_human.webp":"c2f8b0fd74f3","diagrams-webp/plan_a_A06_dog.webp":"737c3a72c6b9","diagrams-webp/plan_a_A06_human.webp":"916979f4c850","diagrams-webp/plan_a_A07_dog.webp":"bca4757dfc54","diagrams-webp/plan_a_A07_human.webp":"7bb2ac25a0e6","diagrams-webp/plan_a_A08_dog.webp":"1aafc479750a","diagrams-webp/plan_a_A08_human.webp":"3f9c9b57d6f8","diagrams-webp/plan_a_A09_dog.webp":"e9ae36f3dd7c","diagrams-webp/plan_a_A09_human.webp":"ee6fb8e09ba5","diagrams-webp/plan_a_A10_dog.webp":"2157eb4db15f","diagrams-webp/plan_a_A10_human.webp":"f23caa0d8386","diagrams-webp/plan_b_B01_dog.webp":"00cbe489ba89","diagrams-webp/plan_b_B01_human.webp":"536ade8aba2f","diagrams-webp/plan_b_B02_dog.webp":"0d9188959a27","diagrams-webp/plan_b_B02_human.webp":"7b05134ef3d8","diagrams-webp/plan_b_B03_dog.webp":"7d935a05813f","diagrams-webp/plan_b_B03_human.webp":"b9938c589996","diagrams-webp/plan_b_B04_dog.webp":"603a6bc73e38","diagrams-webp/plan_b_B04_human.webp":"1121477ddfd5","diagrams-webp/plan_b_B05_dog.webp":"6a4174381d1f","diagrams-webp/plan_b_B05_human.webp":"8abe9ea57e4f","diagrams-webp/plan_b_B06_dog.webp":"2c4797f78d69","diagrams-webp/plan_b_B06_human.webp":"bb8fad6e36ab","diagrams-webp/plan_b_B07_dog.webp":"49503515bd0d","diagrams-webp/plan_b_B07_human.webp":"94681cda3c1e","diagrams-webp/plan_b_B08_dog.webp":"eccb90bb58f4","diagrams-webp/plan_b_B08_human.webp":"3cf03c6ec26a","diagrams-webp/plan_b_B09_dog.webp":"32d7be4b944e","diagrams-webp/plan_b_B09_human.webp":"a783280c97a3","diagrams-webp/plan_b_B10_dog.webp":"033cebf191b8","diagrams-webp/plan_b_B10_human.webp":"e23d5ec3681f","diagrams-webp/plan_c_C01_dog.webp":"36e41c17e183","diagrams-webp/plan_c_C01_human.webp":"d6d8cd74776f","diagrams-webp/plan_c_C02_dog.webp":"32ae143d107b","diagrams-webp/plan_c_C02_human.webp":"c72817272ce3","diagrams-webp/plan_c_C03_dog.webp":"615f11246888","diagrams-webp/plan_c_C03_human.webp":"e1877579b1aa","diagrams-webp/plan_c_C04_dog.webp":"a0c156bd07c5","diagrams-webp/plan_c_C04_human.webp":"efdf00f86e29","diagrams-webp/plan_c_C05_dog.webp":"ed61633037e7","diagrams-webp/plan_c_C05_human.webp":"f5759fc46a76","diagrams-webp/plan_c_C06_dog.webp":"6728ddd59058","diagrams-webp/plan_c_C06_human.webp":"3993f532968f","diagrams-webp/plan_c_C07_dog.webp":"ecc051edd458","diagrams-webp/plan_c_C07_human.webp":"bbc4c16a778c","diagrams-webp/plan_c_C08_dog.webp":"171db338cc45","diagrams-webp/plan_c_C08_human.webp":"8b1e5a254cf1","diagrams-webp/plan_c_C09_dog.webp":"457bc2a161d1","diagrams-webp/plan_c_C09_human.webp":"0f30e770ca87","diagrams-webp/plan_c_C10_dog.webp":"6bc41b42d31e","diagrams-webp/plan_c_C10_human.webp":"83f32b7762b6","diagrams-webp/plan_d_D01_dog.webp":"cb3959ebfeaf","diagrams-webp/plan_d_D01_human.webp":"4fc164de636d","diagrams-webp/plan_d_D02_dog.webp":"9c41f16499d3","diagrams-webp/plan_d_D02_human.webp":"7c997f14e835","diagrams-webp/plan_d_D03_dog.webp":"5020f66d5845","diagrams-webp/plan_d_D03_human.webp":"d4a94873fa0f","diagrams-webp/plan_d_D04_dog.webp":"09073a0efc1f","diagrams-webp/plan_d_D04_human.webp":"a021e9bd71b1","diagrams-webp/plan_d_D05_dog.webp":"51d4c7ef1bfc","diagrams-webp/plan_d_D05_human.webp":"fbd7ec4db060","diagrams-webp/plan_d_D06_dog.webp":"7295c15d5b71","diagrams-webp/plan_d_D06_human.webp":"39f81b94592b","diagrams-webp/plan_d_D07_dog.webp":"70a9e8f63ceb","diagrams-webp/plan_d_D07_human.webp":"f6342506a8cf","diagrams-webp/plan_d_D08_dog.webp":"557188388e15","diagrams-webp/plan_d_D08_human.webp":"a5d6338f642b","diagrams-webp/plan_d_D09_dog.webp":"69abbfc96354","diagrams-webp/plan_d_D09_human.webp":"c16cc0e36002","diagrams-webp/plan_d_D10_dog.webp":"7d907a7e6c77","diagrams-webp/plan_d_D10_human.webp":"b5f8912103e9","diagrams-webp/plan_e_E01_dog.webp":"f84fa3a7b0e0","diagrams-webp/plan_e_E01_human.webp":"ca021c345df4","diagrams-webp/plan_e_E02_dog.webp":"8b7c2b75168c","diagrams-webp/plan_e_E02_human.webp":"5eb08d11da4e","diagrams-webp/plan_e_E03_dog.webp":"ae4a8509db86","diagrams-webp/plan_e_E03_human.webp":"01c2f3e37196","diagrams-webp/plan_e_E04_dog.webp":"46b955d2b3b7","diagrams-webp/plan_e_E04_human.webp":"86b0009ec306","diagrams-webp/plan_e_E05_dog.webp":"9034b42dba2f","diagrams-webp/plan_e_E05_human.webp":"58e75ba77d42","diagrams-webp/plan_e_E06_dog.webp":"c78fa40ac6ff","diagrams-webp/plan_e_E06_human.webp":"87880a9a8d83","diagrams-webp/plan_e_E07_dog.webp":"95e56802072e","diagrams-webp/plan_e_E07_human.webp":"088b12b8ef44","diagrams-webp/plan_e_E08_dog.webp":"4028ba9d59be","diagrams-webp/plan_e_E08_human.webp":"2afe43adf724","diagrams-webp/plan_e_E09_dog.webp":"4dab4f65e5cc","diagrams-webp/plan_e_E09_human.webp":"76a56bb098e1","diagrams-webp/plan_e_E10_dog.webp":"6687eb779410","diagrams-webp/plan_e_E10_human.webp":"beb28e90bbe8","diagrams-webp/plan_f_F01_dog.webp":"90f398985e3b","diagrams-webp/plan_f_F01_human.webp":"af134664c449","diagrams-webp/plan_f_F02_dog.webp":"2f48f1a421b2","diagrams-webp/plan_f_F02_human.webp":"86804667cead","diagrams-webp/plan_f_F03_dog.webp":"37c2f3a67ac9","diagrams-webp/plan_f_F03_human.webp":"3ef8c1ae2957","diagrams-webp/plan_f_F04_dog.webp":"c0c84f3709c7","diagrams-webp/plan_f_F04_human.webp":"b02e9589de12","diagrams-webp/plan_f_F05_dog.webp":"f9d01d3a77cd","diagrams-webp/plan_f_F05_human.webp":"8fd97bb4595f","diagrams-webp/plan_f_F06_dog.webp":"081ea4ab7012","diagrams-webp/plan_f_F06_human.webp":"284e4788db67","diagrams-webp/plan_f_F07_dog.webp":"0f3fcfcc7983","diagrams-webp/plan_f_F07_human.webp":"5104eb355fab","diagrams-webp/plan_f_F08_dog.webp":"fd59b9256936","diagrams-webp/plan_f_F08_human.webp":"ee33ae267396","diagrams-webp/plan_f_F09_dog.webp":"5d20a8348f80","diagrams-webp/plan_f_F09_human.webp":"18b544da9124","diagrams-webp/plan_f_F10_dog.webp":"d9b208372303","diagrams-webp/plan_f_F10_human.webp":"8df38970c037","field_card.html":"a9ece7047c27","index.html":"95e24f4d15d3","manifest.webmanifest":"dbfa3ff2167b","plans/plan_a.html":"e2f507a71f73","plans/plan_b.html":"9ff59fce7420","plans/plan_c.html":"9ea86189d2fa","plans/plan_d.html":"b40a9a552f77","plans/plan_e.html":"260b285a9036","plans/plan_f.html":"1652b821fe02"};
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
  // Which build this worker is, so a check can tell the new worker from the one it replaces.
  if(d&&d.type==='version'&&e.ports[0]){e.ports[0].postMessage({version:VERSION});return}
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
