"""The on-device error log keeps failures, keeps nothing else, and sends nothing.

Requirement X04. The helpers run in Node; the event wiring runs in a Node
`vm` sandbox with a fake window whose network functions fail the test if
anything calls them. The browser half (a real thrown error shown in the home
page footer) is in scripts/browser_release_qa.py.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "assets/diagnostics.js"
HOSTED = ROOT / "dist/canon6d_sota_hosted"


def scripted_pages() -> list[Path]:
    """Every shipped page that runs a script, hosted and at the repository root."""
    hosted = [page for page in sorted(HOSTED.rglob("*.html")) if "<script" in page.read_text(encoding="utf-8")]
    root = [ROOT / page.relative_to(HOSTED) for page in hosted if page.name != "FocalRuta_STANDALONE.html"]
    return hosted + root


def node(script: str):
    completed = subprocess.run(["node", "-"], input=script, check=True, capture_output=True, text=True)
    return json.loads(completed.stdout)


def helpers(body: str):
    return node(f"const d=require({json.dumps(str(SOURCE))});\nprocess.stdout.write(JSON.stringify((()=>{{{body}}})()));")


HOSTED_PAGE = ("{protocol:'https:',pathname:'/focalruta/plans/plan_a.html',search:'?secreto=1',hash:'#x',"
               "href:'https://pillb.github.io/focalruta/plans/plan_a.html?secreto=1#x'}")


def sandbox(events: str, location: str = HOSTED_PAGE):
    """Run the browser half against a fake window; return what it stored and any network use."""
    return node(f"""
const vm=require('vm'),fs=require('fs');
const store={{}},calls=[],listeners={{}};
const deny=name=>function(){{calls.push(name);throw new Error(name+' called')}};
const win={{
  localStorage:{{getItem:k=>k in store?store[k]:null,setItem:(k,v)=>{{store[k]=String(v)}}}},
  location:{location},
  navigator:{{userAgent:'Mozilla/5.0 (iPhone) Prueba/1.0',sendBeacon:deny('sendBeacon')}},
  fetch:deny('fetch'),XMLHttpRequest:deny('XMLHttpRequest'),WebSocket:deny('WebSocket'),EventSource:deny('EventSource'),Image:deny('Image'),
  addEventListener:(type,fn)=>{{(listeners[type]=listeners[type]||[]).push(fn)}},
}};
win.window=win;
vm.runInNewContext(fs.readFileSync({json.dumps(str(SOURCE))},'utf8'),{{window:win}});
const fire=(type,event)=>(listeners[type]||[]).forEach(fn=>fn(event));
{events}
process.stdout.write(JSON.stringify({{stored:JSON.parse(store['focalruta-errores-v1']||'[]'),calls,raw:store['focalruta-errores-v1']||''}}));
""")


def test_x04_an_error_is_kept_with_only_what_locates_it():
    out = sandbox("fire('error',{target:win,message:'TypeError: x is undefined',"
                  "filename:'https://pillb.github.io/focalruta/plans/plan_a.html?secreto=1#x',lineno:12,colno:3});")
    assert len(out["stored"]) == 1
    item = out["stored"][0]
    assert set(item) == {"kind", "message", "where", "page", "count", "first", "last"}
    assert item["message"] == "TypeError: x is undefined"
    assert item["where"] == "plan_a.html:12:3"
    assert item["page"] == "/focalruta/plans/plan_a.html"
    assert "secreto" not in out["raw"] and "iPhone" not in out["raw"] and "Prueba" not in out["raw"]
    assert out["calls"] == []


def test_x04_query_strings_fragments_and_markup_never_reach_storage():
    out = sandbox("""fire('unhandledrejection',{reason:new Error('Falló https://x.example/a.js?token=abc#frag <img src=x onerror=alert(1)> '+'z'.repeat(400))});""")
    message = out["stored"][0]["message"]
    assert "https://x.example/a.js" in message
    assert not re.search(r"token|abc|frag|[<>]", message), message
    assert len(message) <= 160
    assert out["stored"][0]["kind"] == "promesa"


def test_x04_a_page_opened_from_a_file_is_kept_by_its_name_only():
    """Red team on PR #21, F2: the offline copy opened from a file has the reader's folders,
    username included, in its path; the log is copied and can go into a public issue."""
    standalone = "file:///home/maria.perez/Descargas/FocalRuta_STANDALONE.html"
    out = sandbox(f"""fire('error',{{target:win,message:'Failed to load {standalone[:-24]}diagramas/plan_a_1.webp',
filename:'{standalone}',lineno:3,colno:1}});
fire('error',{{target:{{tagName:'IMG',src:'file:///C:/Users/Maria%20Perez/Downloads/plan_b_2.webp'}}}});""",
                  location=f"{{protocol:'file:',pathname:'/home/maria.perez/Descargas/FocalRuta_STANDALONE.html',href:'{standalone}'}}")
    image, error = out["stored"]
    assert error["page"] == image["page"] == "FocalRuta_STANDALONE.html"
    assert error["where"] == "FocalRuta_STANDALONE.html:3:1"
    assert error["message"] == "Failed to load file://…/plan_a_1.webp"
    assert image["message"] == "IMG plan_b_2.webp"
    assert not re.search(r"maria|perez|home|Descargas|Users", out["raw"], re.I), out["raw"]


def test_x04_what_the_reader_typed_is_not_kept():
    """Red team on PR #21, F2: Chrome's JSON.parse error quotes the text it could not read,
    which can be what the reader typed. Quoted text is dropped; a one-character token and
    a web address stay, since they locate the failure and name no one."""
    out = sandbox("""for(const m of [`SyntaxError: Unexpected token 'M', "Mi equipo Pablo 85mm" is not valid JSON`,
  'JSON Parse error: Unexpected identifier "Pablo"', 'No se leyó «Pablo Pérez» ni “Pablo” ni ‘Pablo’ ni \\'Pablo\\'',
  `Unterminated "Pablo Pérez y su 85mm`, "Failed to load 'https://pillb.github.io/focalruta/assets/hosted.css?v=1'"])
  fire('unhandledrejection',{reason:new Error(m)});""")
    messages = [item["message"] for item in reversed(out["stored"])]
    assert "Pablo" not in out["raw"] and "Pérez" not in out["raw"], out["raw"]
    assert messages[0].startswith("SyntaxError: Unexpected token 'M', ") and messages[0].endswith("is not valid JSON")
    assert messages[4] == "Failed to load 'https://pillb.github.io/focalruta/assets/hosted.css'"


def test_x04_a_failed_image_is_named_by_its_file():
    out = sandbox("fire('error',{target:{tagName:'IMG',src:'https://pillb.github.io/focalruta/diagrams-webp/plan_a_A01_human.webp?v=2'}});")
    assert out["stored"][0]["kind"] == "recurso"
    assert out["stored"][0]["message"] == "IMG plan_a_A01_human.webp"


def test_x04_repeats_are_counted_and_the_log_is_capped():
    result = helpers("""
let list=[];const now=i=>new Date(Date.UTC(2026,9,17,10,i));
list=d.add(list,d.entry('error','A','a.js',1,1,'/p',now(0)));
list=d.add(list,d.entry('error','B','b.js',1,1,'/p',now(1)));
list=d.add(list,d.entry('error','A','a.js',1,1,'/p',now(2)));
const twice=list.map(e=>[e.message,e.count,e.first,e.last]);
for(let i=0;i<30;i++)list=d.add(list,d.entry('error','E'+i,'e.js',i,0,'/p',now(10+i)));
return {twice,size:list.length,newest:list[0].message,oldest:list[list.length-1].message,limit:d.LIMIT};
""")
    assert result["twice"] == [["A", 2, "2026-10-17T10:00Z", "2026-10-17T10:02Z"], ["B", 1, "2026-10-17T10:01Z", "2026-10-17T10:01Z"]]
    assert result["size"] == result["limit"] == 20
    assert result["newest"] == "E29" and result["oldest"] == "E10"


def test_x04_a_broken_storage_never_turns_the_log_into_an_error():
    out = node(f"""
const vm=require('vm'),fs=require('fs');const listeners={{}};
const win={{localStorage:{{getItem:()=>{{throw new Error('denied')}},setItem:()=>{{throw new Error('denied')}}}},
  location:{{pathname:'/'}},navigator:{{}},addEventListener:(t,f)=>{{(listeners[t]=listeners[t]||[]).push(f)}}}};
win.window=win;vm.runInNewContext(fs.readFileSync({json.dumps(str(SOURCE))},'utf8'),{{window:win}});
let thrown=null;try{{listeners.error.forEach(f=>f({{target:win,message:'x'}}))}}catch(e){{thrown=String(e)}}
process.stdout.write(JSON.stringify({{thrown,loaded:win.FocalRutaDiagnostico.load()}}));
""")
    assert out == {"thrown": None, "loaded": []}


def test_x04_the_report_is_spanish_and_fits_a_github_link():
    result = helpers("""
let list=[];for(let i=0;i<20;i++)list=d.add(list,d.entry('error','x'.repeat(200)+i,'a.js',i,0,'/focalruta/',new Date(Date.UTC(2026,9,17))));
return {empty:d.text([]),url:d.issueUrl(list),one:d.text(list.slice(0,1))};
""")
    assert result["empty"] == "Ningún error registrado en este dispositivo."
    assert result["url"].startswith("https://github.com/PillB/focalruta/issues/new?title=Error+en+FocalRuta&body=Registro+de+errores")
    assert len(result["url"]) < 8000
    assert result["one"].startswith("1 vez · 2026-10-17 00:00Z · Error · ")


def test_x04_the_source_has_no_way_to_send_anything():
    source = re.sub(r"/\*.*?\*/|//[^\n]*", "", SOURCE.read_text(encoding="utf-8"), flags=re.S)
    for api in ("fetch(", "XMLHttpRequest", "sendBeacon", "WebSocket", "EventSource", "new Image", "import(", ".src ="):
        assert api not in source, api


def test_x04_every_scripted_page_records_from_its_first_script():
    source = SOURCE.read_text(encoding="utf-8")
    missing, late = [], []
    pages = scripted_pages()
    assert len(pages) >= 19, "the home page, the field card, six plans and the challenge, hosted and at the root"
    for page in pages:
        html = page.read_text(encoding="utf-8")
        block = re.search(r'<script id="diagnostics-js">\n(.*?)</script>', html, re.S)
        name = page.relative_to(ROOT).as_posix()
        if not block or block.group(1) != source:
            missing.append(name)
        elif html.find("<script") != block.start():
            late.append(name)
    assert not missing, f"pages without the same assets/diagnostics.js: {missing}"
    assert not late, f"pages where another script runs before the log: {late}"


def test_x04_the_home_page_shows_the_log_in_spanish():
    html = (ROOT / "index.html").read_text(encoding="utf-8")
    panel = re.search(r'<details id="diag".*?</details>', html, re.S)
    assert panel, "no error log panel on the home page"
    for element in ('id="diag-list"', 'id="diag-empty"', 'id="diag-copy"', 'id="diag-clear"', 'id="diag-report"', 'id="diag-count"'):
        assert element in panel.group(0)
    words = re.sub(r"<[^>]+>", " ", panel.group(0))
    assert "Registro de errores" in words and "no envía nada" in words
