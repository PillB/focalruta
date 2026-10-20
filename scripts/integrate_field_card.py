#!/usr/bin/env python3
"""Put the generated field card into the home page's dialog.

Requirement V05. generate_field_card.py writes the card's markup, styles and
script to data/; this step replaces the three marker-bounded blocks of
index.html with them, so the home page always shows the same card as
field_card.html. It runs from regenerate_all.py and is idempotent: a second
run leaves index.html byte-identical.
"""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "index.html"

MODAL_CSS = """
#field-card-modal{position:fixed;inset:0;z-index:120;display:none;background:rgba(3,13,22,.72)}
#field-card-modal.fc-modal-open{display:block}
/* The first frame after the tap draws the bar and the card's header; the plans and shots follow
   a frame later, so a slow phone shows the card at once instead of after laying out all of it. */
#field-card-modal.fc-modal-first .fc-panel{content-visibility:hidden}
.fc-modal-card{display:flex;flex-direction:column;width:min(100%,900px);height:100dvh;margin:auto;background:#f4f1e9;box-shadow:0 0 60px rgba(0,0,0,.28)}
.fc-modal-bar{flex:0 0 auto;display:flex;align-items:center;justify-content:space-between;gap:8px;min-height:56px;padding:calc(6px + env(safe-area-inset-top)) 10px 6px;background:#061827;color:#fff}
.fc-modal-bar strong{display:block;font-size:16px}.fc-modal-bar small{display:block;font-size:13px;line-height:1.35;color:#dbeafe}
.fc-modal-bar button,.fc-modal-bar a{display:inline-grid;place-items:center;min-width:44px;min-height:44px;padding:0 10px;border:1px solid #ffffff59;border-radius:10px;background:#ffffff14;color:#fff;font-size:14px;font-weight:800;text-decoration:none}
.fc-modal-scroll{flex:1;min-height:0;overflow:auto;-webkit-overflow-scrolling:touch;overscroll-behavior:contain;background:#f4f1e9}
@media(prefers-color-scheme:dark){.fc-modal-scroll{background:#0b1220}}
.fc-modal-card:has(#fc-night:checked) :is(.fc-modal-scroll,.fc-modal-bar){background:#000}.fc-modal-card:has(#fc-night:checked) .fc-modal-bar{color:#ff6b5e}.fc-modal-card:has(#fc-night:checked) .fc-modal-bar :is(small,button,a){color:#ff6b5e;border-color:#4a1410}
body.fc-modal-lock{overflow:hidden}
.mobile-bottom-nav button{min-width:0;min-height:48px;border:0;background:transparent;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;color:#475569;font-size:12px;font-weight:800;padding:0}.mobile-bottom-nav button .ico{font-size:18px;line-height:1}
@media(min-width:900px){#field-card-modal{padding:22px}.fc-modal-card{height:calc(100dvh - 44px);border-radius:22px;overflow:hidden}.fc-modal-bar{padding-top:6px}}
@media print{#field-card-modal{display:none!important}}
"""

MODAL_JS = """
// The one definition of the card dialog: the rest of the page goes inert while it is
// open, focus moves inside as it opens (as showModal() does) and stays there, and Escape
// or the close button return focus to the opener. The panels wait for the frame after the
// first paint (requestAnimationFrame, then a task), which is what a tap is measured to.
let fcOpener=null,fcInert=[];
function fcDialog(){const m=document.getElementById('field-card-modal');return m&&m.classList.contains('fc-modal-open')?m:null}
function openFieldCard(){const m=document.getElementById('field-card-modal');if(!m||fcDialog())return;fcOpener=document.activeElement;fcInert=[...document.body.children].filter(el=>el!==m&&!el.inert&&!['SCRIPT','STYLE'].includes(el.tagName));fcInert.forEach(el=>el.inert=true);m.classList.add('fc-modal-open','fc-modal-first');m.setAttribute('aria-hidden','false');document.body.classList.add('fc-modal-lock');m.querySelector('.fc-modal-scroll')?.scrollTo({top:0,behavior:'auto'});m.querySelector('.fc-modal-bar button')?.focus();requestAnimationFrame(()=>setTimeout(()=>m.classList.remove('fc-modal-first')));}
function closeFieldCard(){const m=fcDialog();if(!m)return;m.classList.remove('fc-modal-open');m.setAttribute('aria-hidden','true');document.body.classList.remove('fc-modal-lock');fcInert.forEach(el=>el.inert=false);fcInert=[];fcOpener?.focus?.();}
document.addEventListener('keydown',e=>{const m=fcDialog();if(!m)return;if(e.key==='Escape'){e.preventDefault();closeFieldCard();return}if(e.key!=='Tab')return;const f=[...m.querySelectorAll('button,[href],input,select,textarea,[tabindex]:not([tabindex="-1"])')].filter(x=>!x.disabled&&x.offsetParent!==null);if(!f.length)return;const first=f[0],last=f[f.length-1];if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus()}else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus()}});
"""


CSS_START, CSS_END = "/* FIELD CARD CSS START */", "/* FIELD CARD CSS END */"
CSS_BLOCK = r"(?:<!--|/\*) FIELD CARD CSS START (?:-->|\*/).*?(?:<!--|/\*) FIELD CARD CSS END (?:-->|\*/)"


def modal(fragment: str) -> str:
    return (
        '<!-- FIELD CARD INTEGRATED -->\n'
        '<div id="field-card-modal" aria-hidden="true" role="dialog" aria-modal="true" aria-label="Tarjeta de campo">\n'
        '  <div class="fc-modal-card">\n'
        '    <div class="fc-modal-bar"><button type="button" onclick="closeFieldCard()" aria-label="Cerrar la tarjeta de campo">✕</button>'
        '<div><strong>Tarjeta de campo</strong><small>Tu progreso se guarda en este dispositivo</small></div>'
        '<a href="field_card.html">Abrir sola</a></div>\n'
        f'    <div class="fc-modal-scroll">{fragment}</div>\n'
        '  </div>\n</div>\n<!-- FIELD CARD INTEGRATED END -->'
    )


def replace_block(text: str, pattern: str, block: str, label: str) -> str:
    text, count = re.subn(pattern, lambda _m: block, text, count=1, flags=re.S)
    if count != 1:
        raise RuntimeError(f"index.html has no {label} block to replace")
    return text


def only_the_card(text: str) -> None:
    """The dialog block is replaced wholesale, so it may hold nothing but the card.

    The session-run dialog once sat inside it and vanished when the card was
    rebuilt; anything else found there is reported instead of dropped.
    """
    block = re.search(r"<!-- FIELD CARD INTEGRATED -->(.*?)<!-- FIELD CARD INTEGRATED END -->", text, flags=re.S)
    if not block:
        return
    card = re.search(r'<div id="field-card-modal".*', block.group(1), flags=re.S)
    outside = block.group(1)[: card.start()] if card else block.group(1)
    if outside.strip():
        ids = re.findall(r'\bid="([\w-]+)"', outside) or [outside.strip()[:60]]
        raise RuntimeError(f"index.html keeps other markup inside the field card block ({', '.join(ids)}); move it out first")


def patch(text: str) -> str:
    fragment = (ROOT / "data" / "field_card_fragment.html").read_text(encoding="utf-8").strip()
    css = (ROOT / "data" / "field_card.css").read_text(encoding="utf-8").strip()
    js = (ROOT / "data" / "field_card.js").read_text(encoding="utf-8").strip()
    # The markers sit inside a stylesheet, so they are CSS comments: an HTML comment there
    # (`<!-- … -->`, the markers before X05) became part of the next rule's selector and the
    # browser dropped that rule. The old form is still found, so an older index.html heals.
    text = replace_block(text, CSS_BLOCK, f"{CSS_START}\n{css}\n{MODAL_CSS}\n{CSS_END}", "card styles")
    only_the_card(text)
    text = replace_block(text, r"<!-- FIELD CARD INTEGRATED -->.*?<!-- FIELD CARD INTEGRATED END -->", modal(fragment), "card dialog")
    # The dialog comes first: if the card's script ever stops, the button still opens the card
    # (a stored value with a quote once left the dialog's `let` uninitialised, red team 2026-10-20).
    return replace_block(text, r"<!-- FIELD CARD JS START -->.*?<!-- FIELD CARD JS END -->",
                         f"<!-- FIELD CARD JS START -->\n{MODAL_JS.strip()}\n{js}\n<!-- FIELD CARD JS END -->", "card script")


def main() -> None:
    before = INDEX.read_text(encoding="utf-8")
    after = patch(before)
    if after != before:
        INDEX.write_text(after, encoding="utf-8")
    print(f"field card {'updated in' if after != before else 'already current in'} {INDEX.name}")


if __name__ == "__main__":
    main()
