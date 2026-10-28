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
const VERSION='focalruta-857b65af3349';
const FILES={"404.html":"c9e6e0690f38","assets/app-icon.svg":"6c706d09c51c","assets/hosted.css":"0b2ccfdbb5ce","assets/icon-192.png":"6ccd0d22a9f8","assets/icon-512.png":"b0089189bd88","assets/icon-maskable-192.png":"1d97339252be","assets/icon-maskable-512.png":"ca2821b508c7","challenges/arquitectura-en-foco/field-card.html":"986b21b3e98a","challenges/arquitectura-en-foco/index.html":"f8204b380b8d","challenges/arquitectura-en-foco/iphone-maps.html":"3af624a6bf96","challenges/arquitectura-en-foco/maps/barranco-tour-1.geojson":"8eb8bf0ce285","challenges/arquitectura-en-foco/maps/barranco-tour-1.html":"7c75f80f02bf","challenges/arquitectura-en-foco/maps/barranco-tour-1.kml":"1ec0eb8380c3","challenges/arquitectura-en-foco/maps/barranco-tour-2.geojson":"9ac1b94d578d","challenges/arquitectura-en-foco/maps/barranco-tour-2.html":"088fa7b5e66c","challenges/arquitectura-en-foco/maps/barranco-tour-2.kml":"c5030a608ade","challenges/arquitectura-en-foco/maps/barranco-tour-3.geojson":"c631cf89a252","challenges/arquitectura-en-foco/maps/barranco-tour-3.html":"df7cf71ac5c5","challenges/arquitectura-en-foco/maps/barranco-tour-3.kml":"f61a985b4f0d","challenges/arquitectura-en-foco/maps/jesus-maria.geojson":"99fec02d468f","challenges/arquitectura-en-foco/maps/jesus-maria.html":"145f27854a2c","challenges/arquitectura-en-foco/maps/jesus-maria.kml":"ecaa6d2d4c63","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.geojson":"2a1086530c8a","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.html":"30335aabaefb","challenges/arquitectura-en-foco/maps/la-victoria-tour-1.kml":"36eaa14112f4","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.geojson":"1eafde54186c","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.html":"8b8708a0f138","challenges/arquitectura-en-foco/maps/la-victoria-tour-2.kml":"9614d52ef075","challenges/arquitectura-en-foco/maps/lima-tour-1.geojson":"1caed483014e","challenges/arquitectura-en-foco/maps/lima-tour-1.html":"a5010bcefe78","challenges/arquitectura-en-foco/maps/lima-tour-1.kml":"ab67e93a405b","challenges/arquitectura-en-foco/maps/lima-tour-2.geojson":"80acd60926e4","challenges/arquitectura-en-foco/maps/lima-tour-2.html":"862b1dc9fcbf","challenges/arquitectura-en-foco/maps/lima-tour-2.kml":"5aca494779b1","challenges/arquitectura-en-foco/maps/lima-tour-3.geojson":"561799ef58f8","challenges/arquitectura-en-foco/maps/lima-tour-3.html":"c24e4034a294","challenges/arquitectura-en-foco/maps/lima-tour-3.kml":"d7b720e12dab","challenges/arquitectura-en-foco/maps/miraflores-tour-1.geojson":"acc4038a7b07","challenges/arquitectura-en-foco/maps/miraflores-tour-1.html":"63af330db45f","challenges/arquitectura-en-foco/maps/miraflores-tour-1.kml":"a5d4af426b7d","challenges/arquitectura-en-foco/maps/miraflores-tour-2.geojson":"f1fb7c3d5e10","challenges/arquitectura-en-foco/maps/miraflores-tour-2.html":"c3d24cbe3838","challenges/arquitectura-en-foco/maps/miraflores-tour-2.kml":"8357fe8822c6","challenges/arquitectura-en-foco/maps/miraflores-tour-3.geojson":"37b085c5fa91","challenges/arquitectura-en-foco/maps/miraflores-tour-3.html":"549587942b0b","challenges/arquitectura-en-foco/maps/miraflores-tour-3.kml":"0e7786a51a72","challenges/arquitectura-en-foco/maps/miraflores-tour-4.geojson":"09045d831213","challenges/arquitectura-en-foco/maps/miraflores-tour-4.html":"3d5df49052b6","challenges/arquitectura-en-foco/maps/miraflores-tour-4.kml":"21085e0883ab","challenges/arquitectura-en-foco/maps/miraflores-tour-5.geojson":"37da8cf4a0ff","challenges/arquitectura-en-foco/maps/miraflores-tour-5.html":"a32326bd1017","challenges/arquitectura-en-foco/maps/miraflores-tour-5.kml":"b376e74a517c","challenges/arquitectura-en-foco/maps/miraflores-tour-6.geojson":"187e48e77445","challenges/arquitectura-en-foco/maps/miraflores-tour-6.html":"10e43c7ee50b","challenges/arquitectura-en-foco/maps/miraflores-tour-6.kml":"b2da352d8d75","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.geojson":"20cd78546b98","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.html":"13424bdfcb4b","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-1.kml":"3c2aa33ea5cf","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.geojson":"c637e069d6c3","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.html":"b8e046431ae9","challenges/arquitectura-en-foco/maps/pueblo-libre-tour-2.kml":"f937f846d6ef","challenges/arquitectura-en-foco/maps/rimac.geojson":"14d1a9f8c663","challenges/arquitectura-en-foco/maps/rimac.html":"ec5aafac6afb","challenges/arquitectura-en-foco/maps/rimac.kml":"dc557d969285","challenges/arquitectura-en-foco/maps/san-borja-tour-1.geojson":"da2a4064ac6f","challenges/arquitectura-en-foco/maps/san-borja-tour-1.html":"67fcb388dd04","challenges/arquitectura-en-foco/maps/san-borja-tour-1.kml":"085bebf9c27d","challenges/arquitectura-en-foco/maps/san-borja-tour-2.geojson":"752162a2f6ea","challenges/arquitectura-en-foco/maps/san-borja-tour-2.html":"572401afffe6","challenges/arquitectura-en-foco/maps/san-borja-tour-2.kml":"c2947f4b5562","challenges/arquitectura-en-foco/maps/san-borja-tour-3.geojson":"84a5f067b619","challenges/arquitectura-en-foco/maps/san-borja-tour-3.html":"840efe165865","challenges/arquitectura-en-foco/maps/san-borja-tour-3.kml":"e394e9a33b1f","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.geojson":"96cf34cd1e6a","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.html":"d1bd893b7da2","challenges/arquitectura-en-foco/maps/san-isidro-tour-1.kml":"b4f4271bc001","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.geojson":"eea9cab37739","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.html":"7e4e75be13f4","challenges/arquitectura-en-foco/maps/san-isidro-tour-2.kml":"a36eebfa5f70","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.geojson":"bf2eb2b8e969","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.html":"fef1da007529","challenges/arquitectura-en-foco/maps/san-isidro-tour-3.kml":"cdfceee39be5","challenges/arquitectura-en-foco/maps/santiago-de-surco.geojson":"091dec8ccade","challenges/arquitectura-en-foco/maps/santiago-de-surco.html":"ee1783c83918","challenges/arquitectura-en-foco/maps/santiago-de-surco.kml":"09b3799dcf50","challenges/arquitectura-en-foco/wiki-tecnicas.html":"3ebce15997a8","data/architecture/candidates.json":"becdd116bd62","data/architecture/geography.json":"e3e74f6c4e4b","data/architecture/learning.json":"001856d9270a","data/architecture/photographers.json":"e2d950a587c3","data/architecture/ranking.json":"b5c3070750fb","data/architecture/routes.json":"9f545c1f74af","data/architecture/scene_dossier_schema.json":"0a76f5fd2108","data/architecture/sources.json":"288fb255cbe6","data/architecture/style_discoveries.json":"ddd327123b32","data/plans.json":"d0dc65861714","data/plans_embedded.js":"760318475bf5","diagrams-webp/composition_capas.webp":"b590343634b3","diagrams-webp/composition_enmarcado.webp":"a79c7caf7348","diagrams-webp/composition_espacio_neg.webp":"8246608cb0e5","diagrams-webp/composition_minimalismo.webp":"123cfb5af991","diagrams-webp/composition_perspectiva.webp":"be657fb9b963","diagrams-webp/composition_punto_interes.webp":"3ee865720627","diagrams-webp/composition_simetria.webp":"43a54f948030","diagrams-webp/composition_tercios.webp":"4ec04562d13d","diagrams-webp/lens_comparison_25cm.webp":"09fda4abf91b","diagrams-webp/lens_comparison_40cm.webp":"d04998859db0","diagrams-webp/lens_comparison_60cm.webp":"0ff0f2dd7726","diagrams-webp/plan_a_A01_dog.webp":"b8229b32e921","diagrams-webp/plan_a_A01_human.webp":"fb98430cea1e","diagrams-webp/plan_a_A02_dog.webp":"64d7134bd38b","diagrams-webp/plan_a_A02_human.webp":"0f68e746130f","diagrams-webp/plan_a_A03_dog.webp":"e8a04793e4bf","diagrams-webp/plan_a_A03_human.webp":"c1a1c1602c03","diagrams-webp/plan_a_A04_dog.webp":"aa87d4701891","diagrams-webp/plan_a_A04_human.webp":"910a282ad659","diagrams-webp/plan_a_A05_dog.webp":"c193937eebe6","diagrams-webp/plan_a_A05_human.webp":"7d02c9fcb329","diagrams-webp/plan_a_A06_dog.webp":"bf24720c8882","diagrams-webp/plan_a_A06_human.webp":"c75b00a173fe","diagrams-webp/plan_a_A07_dog.webp":"8e0eb706d811","diagrams-webp/plan_a_A07_human.webp":"7c168d76afbe","diagrams-webp/plan_a_A08_dog.webp":"91d2dd6c2672","diagrams-webp/plan_a_A08_human.webp":"9c32dd41f496","diagrams-webp/plan_a_A09_dog.webp":"44c9378fa0f3","diagrams-webp/plan_a_A09_human.webp":"43428686a989","diagrams-webp/plan_a_A10_dog.webp":"6fd9915380de","diagrams-webp/plan_a_A10_human.webp":"1c61b0db42e0","diagrams-webp/plan_b_B01_dog.webp":"2dd6285433f0","diagrams-webp/plan_b_B01_human.webp":"669b843df095","diagrams-webp/plan_b_B02_dog.webp":"8e310639b00c","diagrams-webp/plan_b_B02_human.webp":"b3ed48d6599d","diagrams-webp/plan_b_B03_dog.webp":"ab2685f91725","diagrams-webp/plan_b_B03_human.webp":"04f70b8341d0","diagrams-webp/plan_b_B04_dog.webp":"2227e213745e","diagrams-webp/plan_b_B04_human.webp":"a006f71fc1d5","diagrams-webp/plan_b_B05_dog.webp":"e8b814842aff","diagrams-webp/plan_b_B05_human.webp":"aa806f51d855","diagrams-webp/plan_b_B06_dog.webp":"288ed812730a","diagrams-webp/plan_b_B06_human.webp":"c4868e33f714","diagrams-webp/plan_b_B07_dog.webp":"be9046df5770","diagrams-webp/plan_b_B07_human.webp":"733c5f7e8286","diagrams-webp/plan_b_B08_dog.webp":"f79fc347fb91","diagrams-webp/plan_b_B08_human.webp":"c04642f44acd","diagrams-webp/plan_b_B09_dog.webp":"b8ca34f6daf8","diagrams-webp/plan_b_B09_human.webp":"219edaf8b851","diagrams-webp/plan_b_B10_dog.webp":"681af5cba982","diagrams-webp/plan_b_B10_human.webp":"9ebfd714967c","diagrams-webp/plan_c_C01_dog.webp":"0d55e71bf141","diagrams-webp/plan_c_C01_human.webp":"a8f7733f9333","diagrams-webp/plan_c_C02_dog.webp":"aab5f25398d7","diagrams-webp/plan_c_C02_human.webp":"c6bc48ad279c","diagrams-webp/plan_c_C03_dog.webp":"5b4652240518","diagrams-webp/plan_c_C03_human.webp":"8f12e1f5604f","diagrams-webp/plan_c_C04_dog.webp":"35a106b50b05","diagrams-webp/plan_c_C04_human.webp":"5a34f55635e2","diagrams-webp/plan_c_C05_dog.webp":"bf09df2c1613","diagrams-webp/plan_c_C05_human.webp":"2356dd352320","diagrams-webp/plan_c_C06_dog.webp":"c1e4399956e7","diagrams-webp/plan_c_C06_human.webp":"373d43255f94","diagrams-webp/plan_c_C07_dog.webp":"bf4f4a4fe1fa","diagrams-webp/plan_c_C07_human.webp":"66de88e3c27a","diagrams-webp/plan_c_C08_dog.webp":"c9043534b1f7","diagrams-webp/plan_c_C08_human.webp":"b42490baab97","diagrams-webp/plan_c_C09_dog.webp":"2209a10882da","diagrams-webp/plan_c_C09_human.webp":"950b6f6e77b3","diagrams-webp/plan_c_C10_dog.webp":"51d41a4553de","diagrams-webp/plan_c_C10_human.webp":"11437bcbdcf4","diagrams-webp/plan_d_D01_dog.webp":"29e168f49386","diagrams-webp/plan_d_D01_human.webp":"59351db1e58c","diagrams-webp/plan_d_D02_dog.webp":"5e53361336cc","diagrams-webp/plan_d_D02_human.webp":"dd8d71ece420","diagrams-webp/plan_d_D03_dog.webp":"5bf4013d7ef5","diagrams-webp/plan_d_D03_human.webp":"6e707be68f37","diagrams-webp/plan_d_D04_dog.webp":"e164b1edc964","diagrams-webp/plan_d_D04_human.webp":"840c47629e68","diagrams-webp/plan_d_D05_dog.webp":"3bc2d5fd4e20","diagrams-webp/plan_d_D05_human.webp":"a06f749ce2b3","diagrams-webp/plan_d_D06_dog.webp":"77992d37f1f7","diagrams-webp/plan_d_D06_human.webp":"89c364db0720","diagrams-webp/plan_d_D07_dog.webp":"8cc7f3528e34","diagrams-webp/plan_d_D07_human.webp":"44199260b63c","diagrams-webp/plan_d_D08_dog.webp":"1e3e62125325","diagrams-webp/plan_d_D08_human.webp":"dfcdaa8045ec","diagrams-webp/plan_d_D09_dog.webp":"1cf4a42157c6","diagrams-webp/plan_d_D09_human.webp":"0fcaa08037bf","diagrams-webp/plan_d_D10_dog.webp":"5364440fd574","diagrams-webp/plan_d_D10_human.webp":"19b8d4d0fbcb","diagrams-webp/plan_e_E01_dog.webp":"410e30190d39","diagrams-webp/plan_e_E01_human.webp":"8d6c78f56b48","diagrams-webp/plan_e_E02_dog.webp":"63d9cfd119c8","diagrams-webp/plan_e_E02_human.webp":"fd20e468ddb4","diagrams-webp/plan_e_E03_dog.webp":"dcc154c7f66f","diagrams-webp/plan_e_E03_human.webp":"555bdeaa6e26","diagrams-webp/plan_e_E04_dog.webp":"c38dc43795d3","diagrams-webp/plan_e_E04_human.webp":"9af38232f30c","diagrams-webp/plan_e_E05_dog.webp":"87808bd82c86","diagrams-webp/plan_e_E05_human.webp":"6702edd00ae3","diagrams-webp/plan_e_E06_dog.webp":"6a3349dd0e2c","diagrams-webp/plan_e_E06_human.webp":"5903ae9ae05c","diagrams-webp/plan_e_E07_dog.webp":"ec61dff7afee","diagrams-webp/plan_e_E07_human.webp":"04da271683ac","diagrams-webp/plan_e_E08_dog.webp":"120ddfe6b223","diagrams-webp/plan_e_E08_human.webp":"6ec3693fa337","diagrams-webp/plan_e_E09_dog.webp":"41cdb1fe8461","diagrams-webp/plan_e_E09_human.webp":"1ecb9e458761","diagrams-webp/plan_e_E10_dog.webp":"94846680e884","diagrams-webp/plan_e_E10_human.webp":"798e1d5c1442","diagrams-webp/plan_f_F01_dog.webp":"5cdae739daef","diagrams-webp/plan_f_F01_human.webp":"df96b78be8f6","diagrams-webp/plan_f_F02_dog.webp":"4fc112f48365","diagrams-webp/plan_f_F02_human.webp":"2f99ef28321c","diagrams-webp/plan_f_F03_dog.webp":"873caf4b76d2","diagrams-webp/plan_f_F03_human.webp":"84850b01ac6c","diagrams-webp/plan_f_F04_dog.webp":"21309835a9d6","diagrams-webp/plan_f_F04_human.webp":"791444493d1d","diagrams-webp/plan_f_F05_dog.webp":"6ca103b6f5d1","diagrams-webp/plan_f_F05_human.webp":"d75fd185558d","diagrams-webp/plan_f_F06_dog.webp":"39858b705223","diagrams-webp/plan_f_F06_human.webp":"1c2130c69cb1","diagrams-webp/plan_f_F07_dog.webp":"cc54f3357655","diagrams-webp/plan_f_F07_human.webp":"aeb37accb58f","diagrams-webp/plan_f_F08_dog.webp":"0f167a56c2a8","diagrams-webp/plan_f_F08_human.webp":"b285ec3a1c26","diagrams-webp/plan_f_F09_dog.webp":"7cae0481258f","diagrams-webp/plan_f_F09_human.webp":"d5376badca1a","diagrams-webp/plan_f_F10_dog.webp":"6b50749584a7","diagrams-webp/plan_f_F10_human.webp":"e69c03ce2ad1","field_card.html":"58b40dce6639","index.html":"9371439d1279","manifest.webmanifest":"dbfa3ff2167b","plans/plan_a.html":"db4f2fcf3758","plans/plan_b.html":"92e8e7d8030d","plans/plan_c.html":"143e79f5bb44","plans/plan_d.html":"90027101c90a","plans/plan_e.html":"b73f4b6e1f3c","plans/plan_f.html":"bdf64d12d037"};
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
