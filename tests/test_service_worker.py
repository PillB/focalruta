"""The service worker never mixes builds and an upgrade keeps what a reader had offline.

Requirements, added after the red team's review of PR #20 and the check of the
live site:
- V16 A page is served this build's files or the network's, never a copy from
  another build: the worker checks the bytes of every copy it keeps against
  the build (so neither the HTTP cache, which Pages sets to 10 minutes, nor a
  CDN node that has not caught up can slip an old file in), the home page
  names its stylesheet and data by revision (so an older worker still in
  control fetches the new ones), and every file it keeps, the web manifest
  included, is served offline. Pages and this build's files are revalidated
  with the server; a page from another build gets the revision it names; a
  404 or 5xx never replaces a kept copy.
- V17 An upgrade, from the worker live at 9cd3044 or from any later one, keeps
  every page and diagram the reader had offline and downloads nothing that did
  not change; the files kept for the field are brought up to date on install,
  and the worker can say how many are current, older or missing. Caches of the
  other sites on pillb.github.io are never touched.

The worker runs in Node against tests/sw_world.js: shared Cache Storage, a
server that can be redeployed, an HTTP cache that answers plain requests, and
no network on demand. scripts/field_card_qa.py rehearses the same upgrade in
Chromium with real builds. FOCALRUTA_SW_TEMPLATE runs these tests against
another template (the RED runs used the one from eb3c101).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

import service_worker  # noqa: E402

WORLD = ROOT / "tests" / "sw_world.js"
LIVE_WORKER = ROOT / "tests" / "fixtures" / "sw_live_9cd3044.js"
DIST = ROOT / "dist" / "canon6d_sota_hosted"
CORE = list(service_worker.CORE)
PLANS = [f"plans/plan_{x}.html" for x in "abcdef"]
DIAGRAMS = [f"diagrams-webp/plan_{x}_{n}.webp" for x in "abcdef" for n in (1, 2)]


def site(build: str, changed: tuple[str, ...] = ()) -> dict[str, str]:
    """A miniature of the shipped site; files in `changed` carry this build's name."""
    files = {path: f"{path} · 1" for path in CORE + PLANS + DIAGRAMS}
    files.update({path: f"{path} · {build}" for path in changed})
    return files


A = site("A")
B = site("B", ("index.html", "assets/hosted.css", "data/plans_embedded.js", "plans/plan_c.html", "diagrams-webp/plan_c_1.webp"))
C = {**B, **site("C", ("plans/plan_c.html", "diagrams-webp/plan_c_2.webp", "assets/hosted.css"))}
C = {path: C[path] for path in B}


def run(scenario: str, **values) -> dict:
    """Run `scenario` (the body of an async function) and return the object it fills in, `out`."""
    constants = "".join(f"const {name}={json.dumps(value)};\n" for name, value in values.items())
    script = (f"const {{World,SCOPE,rev}}=require({json.dumps(str(WORLD))});const fs=require('fs');\n"
              f"const LIVE={json.dumps(str(LIVE_WORKER))};const CORE={json.dumps(CORE)};\n{constants}"
              "const live=w=>w.load(fs.readFileSync(LIVE,'utf8'));\n"
              "const ours=(w,files)=>w.load(w.template(files,CORE));\n"
              "const tryUpgrade=async sw=>{try{await sw.upgrade();return true}catch(e){return String(e.message||e)}};\n"
              "const offline=async(sw,paths,mode)=>{const o={};for(const p of paths)o[p]=(await sw.request(p,mode)).body||null;return o};\n"
              f"const out={{}};(async()=>{{\n{scenario}\n}})().then(()=>process.stdout.write(JSON.stringify(out)),"
              "e=>process.stdout.write(JSON.stringify({crash:String(e&&e.stack||e)})));")
    completed = subprocess.run(["node", "-"], input=script, capture_output=True, text=True, check=True)
    result = json.loads(completed.stdout)
    assert "crash" not in result, result.get("crash")
    return result


def test_v16_install_keeps_this_builds_files_even_when_the_http_cache_still_has_the_last_ones():
    out = run("""
const w=new World();w.deploy(A);w.rememberHttp();w.deploy(B);
const sw=ours(w,B);out.installed=await tryUpgrade(sw);
w.online=false;out.shell=await offline(sw,CORE);
out.home=(await sw.request('',"navigate")).body;
""", A=A, B=B)
    assert out["installed"] is True
    stale = {path: body for path, body in out["shell"].items() if body != B[path]}
    assert not stale, f"kept from the HTTP cache instead of this build: {stale}"
    assert out["home"] == B["index.html"]


def test_v16_a_file_the_server_still_serves_from_the_last_build_stops_the_install():
    out = run("""
const w=new World();w.deploy({...B,'assets/hosted.css':A['assets/hosted.css']});
const sw=ours(w,B);out.installed=await tryUpgrade(sw);
out.kept=[].concat(...Object.values(w.cacheReport())).filter(k=>k.startsWith('assets/hosted.css'));
""", A=A, B=B)
    assert out["installed"] is not True, "the worker took a stylesheet that is not this build's"
    assert out["kept"] == [], out["kept"]


def test_v16_every_kept_file_is_served_offline_including_the_web_manifest():
    out = run("""
const w=new World();w.deploy(B);const sw=ours(w,B);await sw.upgrade();
w.online=false;out.cors=await offline(sw,['manifest.webmanifest','data/architecture/routes.json'],'cors');
out.plain=await offline(sw,CORE);
""", B=B)
    assert out["cors"] == {path: B[path] for path in out["cors"]}
    assert out["plain"] == {path: B[path] for path in CORE}


def test_v16_the_home_page_names_its_stylesheet_and_data_by_revision():
    html = (DIST / "index.html").read_text(encoding="utf-8")
    for asset in ("assets/hosted.css", "data/plans_embedded.js"):
        named = re.findall(rf'(?:href|src)="\./{re.escape(asset)}(\?v=[0-9a-f]+)?"', html)
        assert named, f"the home page does not load {asset}"
        assert named == [f"?v={hashlib.sha256((DIST / asset).read_bytes()).hexdigest()[:12]}"], (asset, named)


def test_v16_a_worker_from_an_older_build_fetches_a_stylesheet_named_by_its_new_revision():
    out = run("""
const w=new World();w.deploy(A);const old=live(w);await old.upgrade();
await old.request('assets/hosted.css');w.deploy(B);
out.bare=(await old.request('assets/hosted.css')).body;
out.named=(await old.request('assets/hosted.css?v='+rev(Buffer.from(B['assets/hosted.css'])))).body;
""", A=A, B=B)
    assert out["bare"] == A["assets/hosted.css"], "the worker live at 9cd3044 answers a known URL from its cache"
    assert out["named"] == B["assets/hosted.css"]


def test_v16_a_page_opened_within_the_http_cache_window_is_this_builds():
    """Pages sends max-age=600: for ten minutes after a deploy the browser's HTTP cache still
    answers a plain request for the site's root with the last build's home page."""
    out = run("""
const w=new World();w.deploy(A);await ours(w,A).upgrade();w.rememberHttp();
w.deploy(B);const b=ours(w,B);await b.upgrade();
out.root=(await b.request('','navigate')).body;
out.page=(await b.request('plans/plan_c.html','navigate')).body;
""", A=A, B=B)
    assert out == {"root": B["index.html"], "page": B["plans/plan_c.html"]}


def test_v16_a_file_opened_within_the_http_cache_window_is_this_builds():
    """The same ten minutes for a file the page names without a revision, such as a diagram
    the reader never kept: it is revalidated, so the last build's copy is not handed back
    (red team, third pass on PR #20)."""
    out = run("""
const w=new World();w.deploy(A);await ours(w,A).upgrade();w.rememberHttp();
w.deploy(B);const b=ours(w,B);await b.upgrade();
out.diagram=(await b.request('diagrams-webp/plan_c_1.webp')).body;
""", A=A, B=B)
    assert out == {"diagram": B["diagrams-webp/plan_c_1.webp"]}


def test_v16_a_page_from_another_build_gets_the_stylesheet_it_names():
    """A home page the HTTP cache kept from the last build names that build's stylesheet; the
    worker must not answer it with this build's, and answers this build's from its cache."""
    out = run("""
const w=new World();w.deploy(A);const css='assets/hosted.css',old=w.revisions()[css];
w.httpCache[SCOPE+css+'?v='+old]=Buffer.from(A[css]);
w.deploy(B);const b=ours(w,B);await b.upgrade();
out.old=(await b.request(css+'?v='+old)).body;
const now=await b.request(css+'?v='+w.revisions()[css]);out.now=now.body;out.network=now.network;
""", A=A, B=B)
    assert out == {"old": A["assets/hosted.css"], "now": B["assets/hosted.css"], "network": False}


def test_v16_an_error_from_the_server_does_not_replace_the_kept_copy():
    """A 404 or 5xx from a CDN node that has not caught up loses to the copy the reader kept."""
    out = run("""
const w=new World();w.deploy(B);const b=ours(w,B);await b.upgrade();
await b.message({type:'pack',urls:['plans/plan_c.html','diagrams-webp/plan_c_2.webp'].map(p=>SCOPE+p)});
// Build C changes both; the server has not caught up on either and answers 404.
const lagging={...C};delete lagging['plans/plan_c.html'];delete lagging['diagrams-webp/plan_c_2.webp'];
w.deploy(lagging);const c=ours(w,C);await tryUpgrade(c);
out.page=await c.request('plans/plan_c.html','navigate');
out.diagram=await c.request('diagrams-webp/plan_c_2.webp');
""", B=B, C=C)
    assert (out["page"]["status"], out["page"]["body"]) == (200, B["plans/plan_c.html"])
    assert (out["diagram"]["status"], out["diagram"]["body"]) == (200, B["diagrams-webp/plan_c_2.webp"])


def test_v17_an_upgrade_from_the_live_worker_keeps_what_the_reader_opened_and_downloads_only_changes():
    out = run("""
const w=new World();w.deploy(A);const old=live(w);await old.upgrade();
await old.request('plans/plan_c.html?desde=inicio','navigate');await old.request('diagrams-webp/plan_c_2.webp');
w.deploy(B);const before=w.requests.length;const sw=ours(w,B);out.installed=await tryUpgrade(sw);
out.downloaded=w.requests.slice(before).map(r=>r.url.replace(SCOPE,''));
out.caches=Object.keys(w.cacheReport());
w.online=false;out.plan=(await sw.request('plans/plan_c.html','navigate')).body;
out.diagram=(await sw.request('diagrams-webp/plan_c_2.webp')).body;out.home=(await sw.request('','navigate')).body;
""", A=A, B=B)
    assert out["installed"] is True
    assert out["plan"] == A["plans/plan_c.html"], "the plan the reader opened before the upgrade is gone offline"
    assert out["diagram"] == A["diagrams-webp/plan_c_2.webp"]
    assert out["home"] == B["index.html"]
    changed_core = sorted(path for path in CORE if A[path] != B[path])
    assert sorted(out["downloaded"]) == changed_core, "an unchanged file was downloaded again, or a changed one was not"
    assert not [name for name in out["caches"] if re.fullmatch(r"focalruta-[0-9a-f]{12}-\w+", name)], out["caches"]


def test_v17_the_files_kept_for_the_field_follow_a_deploy_and_say_how_current_they_are():
    out = run("""
const w=new World();w.deploy(B);const b=ours(w,B);await b.upgrade();
const urls=[...PACKED].map(p=>SCOPE+p);
const progress=await b.message({type:'pack',urls});out.packed=progress[progress.length-1];
w.deploy(C);const before=w.requests.length;const c=ours(w,C);out.installed=await tryUpgrade(c);
out.downloaded=w.requests.slice(before).map(r=>r.url.replace(SCOPE,''));
out.status=(await c.message({type:'pack-status',urls}))[0];
out.pack=w.cacheReport()['focalruta-pack'];
w.online=false;out.offline=await offline(c,PACKED);
""", B=B, C=C, PACKED=PLANS + DIAGRAMS)
    assert out["packed"] == {"type": "pack-progress", "done": 18, "failed": 0, "total": 18}
    assert out["installed"] is True
    changed = sorted(path for path in B if B[path] != C[path])
    assert sorted(out["downloaded"]) == changed, "the install should fetch exactly what changed, kept for the field or not"
    assert out["offline"] == {path: C[path] for path in PLANS + DIAGRAMS}
    assert out["status"] == {"type": "pack-status", "total": 18, "current": 18, "older": 0, "missing": 0}
    assert len(out["pack"]) == 18, "older revisions were left next to the new ones"


def test_v17_a_kept_file_that_could_not_be_refreshed_stays_and_is_reported_as_older():
    out = run("""
const w=new World();w.deploy(B);const b=ours(w,B);await b.upgrade();
const urls=[...PACKED].map(p=>SCOPE+p);await b.message({type:'pack',urls});
w.deploy({...C,'plans/plan_c.html':B['plans/plan_c.html']});
const c=ours(w,C);out.installed=await tryUpgrade(c);
out.status=(await c.message({type:'pack-status',urls}))[0];
w.online=false;out.plan=(await c.request('plans/plan_c.html','navigate')).body;
""", B=B, C=C, PACKED=PLANS + DIAGRAMS)
    assert out["installed"] is True, "a kept plan that could not be refreshed must not block the new shell"
    assert out["status"] == {"type": "pack-status", "total": 18, "current": 17, "older": 1, "missing": 0}
    assert out["plan"] == B["plans/plan_c.html"]


def test_v16_a_guide_opened_by_its_folder_works_offline():
    guide = "challenges/arquitectura-en-foco/index.html"
    out = run("""
const w=new World();w.deploy(B);const sw=ours(w,B);await sw.upgrade();w.online=false;
out.folder=(await sw.request('challenges/arquitectura-en-foco/','navigate')).body;
out.query=(await sw.request('challenges/arquitectura-en-foco/?ruta=barranco#mapa','navigate')).body;
""", B=B)
    assert out == {"folder": B[guide], "query": B[guide]}


def test_v16_offline_a_page_never_kept_sends_the_reader_to_the_home_page_with_its_name():
    """Live check of 56a6e97, M7: the home page's bytes served under plans/plan_c.html resolved
    its stylesheet, images and links under plans/, so the reader got an unstyled page whose
    every link led to another broken copy. The worker now redirects to the home page, which
    says which page was not kept."""
    unkept = ["plans/plan_c.html", "challenges/arquitectura-en-foco/wiki-tecnicas.html", "plans/plan_z.html"]
    out = run("""
const w=new World();w.deploy(B);const sw=ours(w,B);await sw.upgrade();w.online=false;
for(const p of UNKEPT){const r=await sw.request(p,'navigate');out[p]=[r.status,r.location??null,r.body??null]}
out.landing=(await sw.request('index.html?sin-conexion=plans%2Fplan_c.html','navigate')).body;
""", B=B, UNKEPT=unkept)
    scope = "https://pillb.github.io/focalruta/"
    for path in unkept:
        assert out[path] == [302, scope + "index.html?sin-conexion=" + path.replace("/", "%2F"), ""], (path, out[path])
    assert out["landing"] == B["index.html"]


def test_v17_caches_of_other_sites_on_the_origin_survive_an_upgrade():
    out = run("""
const w=new World();for(const name of ['poseart-shell','workbox-precache-v2-https://pillb.github.io/otro/'])await w.caches.open(name);
w.deploy(A);await live(w).install();w.deploy(B);await ours(w,B).upgrade();
out.caches=Object.keys(w.cacheReport());
""", A=A, B=B)
    assert {"poseart-shell", "workbox-precache-v2-https://pillb.github.io/otro/"} <= set(out["caches"]), out["caches"]


def test_v17_requests_outside_this_build_go_to_the_network_untouched():
    out = run("""
const w=new World();w.deploy({...B,'FocalRuta_STANDALONE.html':'15 MB'});const sw=ours(w,B);await sw.upgrade();
out.standalone=(await sw.request('FocalRuta_STANDALONE.html','navigate')).body;
out.kept=[].concat(...Object.values(w.cacheReport())).filter(k=>k.includes('STANDALONE'));
""", B=B)
    assert out["standalone"] == "15 MB"
    assert out["kept"] == []


def test_v17_the_built_worker_carries_every_shipped_file_but_the_downloads():
    worker = (DIST / "sw.js").read_text(encoding="utf-8")
    files = json.loads(re.search(r"const FILES=(\{.*?\});", worker).group(1))
    shipped = {p.relative_to(DIST).as_posix() for p in DIST.rglob("*") if p.is_file()}
    assert set(files) == {p for p in shipped if p not in service_worker.LEFT_OUT and not p.startswith(service_worker.LEFT_OUT_DIRS)}
    wrong = [p for p, revision in files.items() if revision != hashlib.sha256((DIST / p).read_bytes()).hexdigest()[:12]]
    assert not wrong, wrong
    assert set(CORE) <= set(files) and {"plans/plan_a.html", "manifest.webmanifest"} <= set(files)
