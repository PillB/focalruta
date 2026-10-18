#!/usr/bin/env python3
"""The reading floor every page holds to: requirements V10 to V12.

V10 no text a reader sees is smaller than 12 px.
V11 every control is at least 44 × 44 px, so it can be hit with a thumb in the
    field (Apple's 44 pt and WCAG 2.5.5). Links inside a sentence are exempt,
    as WCAG 2.5.8 allows; a sentence cannot grow to fit them.
V12 the interface is in Spanish. Camera labels stay as the 6D prints them, and
    the titles of cited English sources stay as published.

V18 nothing a reader needs is cut off, from a 320 px screen up (WCAG 1.4.10
    Reflow): no text or control runs past the edge of the screen, where
    `body{overflow-x:hidden}` would hide it, unless it sits in a strip that
    scrolls sideways, no control's label is clipped or runs out of it, no text
    is cut with an ellipsis, and no control is squeezed on top of another.

The checks live here so the static tests and the browser QA measure the same
thing.
"""
from __future__ import annotations

import re

MIN_TEXT_PX = 12
MIN_TARGET_PX = 44

# English a reader met on the home page, the plan pages or the old field card.
# Matched without case, on whole words.
ENGLISH_UI = re.compile(
    r"\b(?:field card|eye-level|pre-?flight|shutter|dof|fov|mfd|burst|streak|blue hour|light ?painting"
    r"|zooming|freeze|background|foreground|panning|reset|human|building lab|session run|tips?"
    r"|settings|back|download|close|next|previous|print|share|save)\b",
    re.I,
)

# Every visible text node under the floor, outside `skip`. SVG text is measured
# as drawn: its font size times the scale the SVG is shown at.
TEXT_UNDER_FLOOR = """([skip,floor])=>{const out=[];const w=document.createTreeWalker(document.body,NodeFilter.SHOW_TEXT);let n;
while((n=w.nextNode())){if(!n.textContent.trim())continue;const el=n.parentElement;if(!el||(skip&&el.closest(skip))||el.closest('script,style,noscript'))continue;
const r=el.getBoundingClientRect();if(!el.getClientRects().length||r.width<=1||r.height<=1||getComputedStyle(el).visibility==='hidden')continue;
let fs=parseFloat(getComputedStyle(el).fontSize);
if(el instanceof SVGElement&&el.getScreenCTM()){const m=el.getScreenCTM();fs*=Math.sqrt(Math.abs(m.a*m.d-m.b*m.c))}
fs=Math.round(fs*10)/10;if(fs<floor)out.push(fs+'px '+n.textContent.trim().slice(0,32))}return [...new Set(out)]}"""

# Every visible control under the floor. A radio or checkbox is measured by its
# label, which is what the thumb hits; a link inside running text is exempt.
TARGETS_UNDER_FLOOR = """([skip,floor])=>{const out=[];
const inSentence=a=>a.tagName==='A'&&getComputedStyle(a).display==='inline'&&a.parentElement.textContent.trim().length>a.textContent.trim().length+8;
for(const el of document.querySelectorAll('a[href],button,input:not([type=hidden]),select,textarea,summary,[role=button],[role=tab]')){
if(skip&&el.closest(skip))continue;let t=el;
if(el.tagName==='INPUT'&&(el.type==='radio'||el.type==='checkbox')){t=el.closest('label')||(el.id&&document.querySelector('label[for="'+el.id+'"]'))||el}
const r=t.getBoundingClientRect();if(!t.getClientRects().length||r.width<=1||r.height<=1||getComputedStyle(t).visibility==='hidden'||inSentence(el))continue;
if(r.width<floor-.5||r.height<floor-.5)out.push((el.textContent||el.getAttribute('aria-label')||el.value||'').trim().slice(0,24)+' '+Math.round(r.width)+'x'+Math.round(r.height))}
return [...new Set(out)]}"""

# Rendered text plus the labels a screen reader announces, outside `skip`.
SHOWN_WORDS = """(skip)=>{const c=document.body.cloneNode(true);c.querySelectorAll('script,style,noscript'+(skip?','+skip:'')).forEach(e=>e.remove());
const labels=[...c.querySelectorAll('[alt],[title],[aria-label],[placeholder]')].map(e=>['alt','title','aria-label','placeholder'].map(a=>e.getAttribute(a)||'').join(' '));
return c.textContent+' '+labels.join(' ')}"""


# V18: elements past either edge of the screen, outside a strip that scrolls sideways,
# controls whose label is clipped or runs out of them, text cut with an ellipsis (a title as
# much as a label), and controls squeezed on top of each other.
# Measured as a reader sees each part, drawn: content-visibility:auto leaves the sections off
# screen at a placeholder height, so their controls would seem to spill onto the next section.
CUT_OFF = """(skip)=>{const drawn=document.createElement('style');drawn.textContent='*{content-visibility:visible!important}';document.head.append(drawn);
const W=document.documentElement.clientWidth,out=[];
const strip=el=>{for(let p=el.parentElement;p&&p!==document.body;p=p.parentElement){const o=getComputedStyle(p).overflowX;if(o==='auto'||o==='scroll')return true}return false};
const name=el=>el.tagName.toLowerCase()+(el.id?'#'+el.id:'')+(el.classList[0]?'.'+el.classList[0]:'')+' «'+(el.textContent||el.value||'').trim().slice(0,24)+'»';
for(const el of document.body.querySelectorAll('*')){if(skip&&el.closest(skip))continue;if(!el.checkVisibility({visibilityProperty:true}))continue;
const r=el.getBoundingClientRect(),cs=getComputedStyle(el);if(r.width<2||r.height<2||cs.visibility==='hidden'||cs.position==='fixed')continue;
if((r.right>W+1||r.left<-1)&&!strip(el))out.push(name(el)+' '+Math.round(r.left)+'–'+Math.round(r.right)+' px');
else if((el.matches('button,a,summary,select,label,legend')||cs.textOverflow==='ellipsis')&&el.scrollWidth>el.clientWidth+1&&el.clientWidth>1)
out.push(name(el)+(cs.textOverflow==='ellipsis'?' text cut with an ellipsis ':cs.overflowX==='visible'?' label runs out ':' label clipped ')+el.scrollWidth+'>'+el.clientWidth)}
// A sticky header over the content scrolled under it is not an overlap: compare controls in the same layer.
const layer=el=>{for(let p=el;p;p=p.parentElement){const s=getComputedStyle(p).position;if(s==='sticky'||s==='fixed')return p}return null};
const ctl=[...document.body.querySelectorAll('a[href],button,input,select,textarea,summary')].filter(el=>!(skip&&el.closest(skip))&&el.checkVisibility({visibilityProperty:true})),box=ctl.map(el=>el.getBoundingClientRect()),on=ctl.map(layer);
for(let i=0;i<ctl.length;i++)for(let j=i+1;j<ctl.length;j++){if(on[i]!==on[j]||ctl[i].contains(ctl[j])||ctl[j].contains(ctl[i]))continue;const a=box[i],b=box[j];
if(Math.min(a.right,b.right)-Math.max(a.left,b.left)>2&&Math.min(a.bottom,b.bottom)-Math.max(a.top,b.top)>2)out.push(name(ctl[i])+' overlaps '+name(ctl[j]))}
drawn.remove();return out}"""


def english_in(text: str) -> list[str]:
    """English interface words in `text`, each once, in order of appearance."""
    return list(dict.fromkeys(m.group(0) for m in ENGLISH_UI.finditer(text)))


# The field card dialog has its own suite (scripts/field_card_qa.py); cited
# sources keep their published titles.
HOME_SKIP = "#field-card-modal"
HOME_SPANISH_SKIP = "#field-card-modal,#sources,cite"
PLANS = [f"plan_{letter}" for letter in "abcdef"]
MOTION_MODES = ("freeze", "pan", "ghost", "trails", "paint", "zoom")


def audit_home(page) -> dict:
    """Walk the home page through the states a reader reaches and collect V10-V12 findings.

    States: as loaded; every plan with the dog at night (the longest notes);
    every motion lab mode; every <details> open; the session dialog; a shot dialog.
    `unreached` names the dialogs that did not open.
    """
    small, tiny, words, unreached, cut = set(), set(), [], [], set()

    def measure(state: str, shown: str = "") -> None:
        # A state that never opens would be measured as the page behind it and pass.
        if shown and not page.evaluate("(s)=>!!document.querySelector(s)?.open", shown):
            unreached.append(state)
        cut.update(f"{state}: {x}" for x in page.evaluate(CUT_OFF, HOME_SKIP))
        small.update(f"{state}: {x}" for x in page.evaluate(TEXT_UNDER_FLOOR, [HOME_SKIP, MIN_TEXT_PX]))
        tiny.update(f"{state}: {x}" for x in page.evaluate(TARGETS_UNDER_FLOOR, [HOME_SKIP, MIN_TARGET_PX]))
        words.append(page.evaluate(SHOWN_WORDS, HOME_SPANISH_SKIP))

    measure("loaded")
    for plan in PLANS:
        page.evaluate("([p])=>{selectPlan(p);setVariant('dog');setTime('night')}", [plan])
        measure(plan)
    page.evaluate("()=>{selectPlan('plan_a');setVariant('human');setTime('day')}")
    for mode in MOTION_MODES:
        page.locator(f'[data-motion="{mode}"]').click()
        measure(f"motion {mode}")
    page.evaluate("()=>document.querySelectorAll('details').forEach(d=>{if(!d.closest('#field-card-modal'))d.open=true})")
    measure("details open")
    page.evaluate("openSessionRun()")
    measure("session dialog", "#session-run-dialog")
    page.keyboard.press("Escape")
    page.evaluate("openModal('plan_c','C08')")
    measure("shot dialog", "#shot-modal")
    page.keyboard.press("Escape")
    return {"small": sorted(small), "tiny": sorted(tiny), "english": english_in(" ".join(words)), "unreached": unreached,
            "cut": sorted(cut)}


def audit_plan_page(page) -> dict:
    """V10-V12 on a plan page, for both subjects in every light, with its details open."""
    small, tiny, words, cut = set(), set(), [], set()
    for subject in ("human", "dog"):
        for slot in ("day", "afternoon", "night"):
            page.evaluate("([s,t])=>{setVariant(s);setTime(t);document.querySelectorAll('details').forEach(d=>d.open=true)}", [subject, slot])
            cut.update(f"{subject}/{slot}: {x}" for x in page.evaluate(CUT_OFF, ""))
            small.update(f"{subject}/{slot}: {x}" for x in page.evaluate(TEXT_UNDER_FLOOR, ["", MIN_TEXT_PX]))
            tiny.update(f"{subject}/{slot}: {x}" for x in page.evaluate(TARGETS_UNDER_FLOOR, ["", MIN_TARGET_PX]))
            words.append(page.evaluate(SHOWN_WORDS, "cite"))
    return {"small": sorted(small), "tiny": sorted(tiny), "english": english_in(" ".join(words)), "cut": sorted(cut)}
