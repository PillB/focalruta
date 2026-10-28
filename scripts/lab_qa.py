"""Y01–Y04: the home page's labs show what a camera can do and say what each control does.

The red team on PR #24 found four labs that drew correctly but taught the wrong thing:

- Y01: every intent preset of the optics lab left the photo 1 to 3 stops off the scene it set,
  and the page opened on «Fondo cremoso» with a shutter speed that preset does not use;
- Y02: the motion lab's slider printed speeds no camera has (1/2275 s, 0.37 s), each effect
  opened beside its reference rather than on it, and «riesgo de trepidación» came from how far
  the subject moved, which is not what makes a camera shake;
- Y03: the composition lab wrote «espacio negativo» in the top right corner wherever the
  subject stood, over the subject when it stood there;
- Y04: the motion, composition and pose buttons are toggles that never said which one is on.

Each check reads what the page shows and holds it to an independent reckoning here: the
exposure from the f-number, time and ISO on the controls, the camera's third-stop shutter
scale from Canon's dial, and the label's box against the subject's box.
"""
from __future__ import annotations

import math

# The third-stop speeds a Canon EOS 6D dial offers, 1/4000 s to 30 s (Canon EOS 6D
# instruction manual, «Tv: shutter-priority AE»), written as the site writes them.
CAMERA_SHUTTERS = (
    "1/4000 s", "1/3200 s", "1/2500 s", "1/2000 s", "1/1600 s", "1/1250 s", "1/1000 s", "1/800 s", "1/640 s",
    "1/500 s", "1/400 s", "1/320 s", "1/250 s", "1/200 s", "1/160 s", "1/125 s", "1/100 s", "1/80 s", "1/60 s",
    "1/50 s", "1/40 s", "1/30 s", "1/25 s", "1/20 s", "1/15 s", "1/13 s", "1/10 s", "1/8 s", "1/6 s", "1/5 s",
    "1/4 s", "0.3 s", "0.4 s", "0.5 s", "0.6 s", "0.8 s", "1 s", "1.3 s", "1.6 s", "2 s", "2.5 s", "3.2 s", "4 s",
    "5 s", "6 s", "8 s", "10 s", "13 s", "15 s", "20 s", "25 s", "30 s",
)
# What each motion effect is shot at in the plans (data/plans.json), by the lab's button.
MOTION_REFERENCE = {"freeze": "1/2000 s", "pan": "1/40 s", "ghost": "1 s", "paint": "10 s", "zoom": "2 s"}
# Trails are 5 to 15 s in the plans: the lab may open anywhere in that span.
TRAILS = ("5 s", "6 s", "8 s", "10 s", "13 s", "15 s")
# Within this, a third of a stop, the lab must call the exposure balanced.
BALANCED_EV = 0.35


def seconds(text: str) -> float:
    value = text.removesuffix(" s")
    if value.startswith("1/"):
        return 1 / float(value[2:])
    return float(value)


READ_OPTICS = """()=>{const q=s=>document.querySelector(s);return{n:+q('#opt-ap').value,
t:+q('#opt-shutter').value,shutter:q('#opt-shutter').selectedOptions[0]?.textContent,iso:+q('#opt-iso').value,
ev:+q('#opt-light').value,exposure:q('#opt-exposure').textContent,desc:q('#opt-svg-desc').textContent,
shutters:[...q('#opt-shutter').options].map(o=>o.textContent),
pressed:[...document.querySelectorAll('[data-opt-preset][aria-pressed="true"]')].map(b=>b.dataset.optPreset)}}"""


def scene_offset(state: dict) -> float:
    """Stops of light more than the settings need: positive means overexposed."""
    camera = math.log2(state["n"] ** 2 / state["t"]) - math.log2(state["iso"] / 100)
    return state["ev"] - camera


def presets(page, record, name: str) -> None:
    opened = page.evaluate(READ_OPTICS)
    record(f"{name} Y01 the optics lab offers every speed of the camera's dial",
           tuple(opened["shutters"]) == CAMERA_SHUTTERS, opened["shutters"])
    pressed = opened["pressed"]
    record(f"{name} Y01 one intent is pressed when the lab opens", len(pressed) == 1, pressed)
    if pressed:
        page.locator(f'[data-opt-preset="{pressed[0]}"]').click()
        again = page.evaluate(READ_OPTICS)
        record(f"{name} Y01 the lab opens on the settings of the intent it shows pressed",
               again["desc"] == opened["desc"] and again["shutter"] == opened["shutter"],
               {"opened": [opened["shutter"], opened["desc"]], "preset": [again["shutter"], again["desc"]]})
    for preset in ("deep", "portrait", "action", "zoom"):
        page.locator(f'[data-opt-preset="{preset}"]').click()
        state = page.evaluate(READ_OPTICS)
        off = scene_offset(state)
        record(f"{name} Y01 the «{preset}» intent exposes the scene it sets",
               abs(off) <= BALANCED_EV and "equilibrada" in state["exposure"],
               {"f": state["n"], "t": state["shutter"], "iso": state["iso"], "ev": state["ev"], "off": round(off, 2),
                "says": state["exposure"][:80]})


SWEEP_MOTION = """()=>{const q=s=>document.querySelector(s),sh=q('#motion-shutter'),out=[];
for(let v=+sh.min;v<=+sh.max;v+=+(sh.step||1)){sh.value=v;sh.dispatchEvent(new Event('input',{bubbles:true}));
out.push([q('#motion-shutter-v').textContent,sh.getAttribute('aria-valuetext')])}return out}"""
READ_MOTION = """()=>{const q=s=>document.querySelector(s);return{shutter:q('#motion-shutter-v').textContent,
risk:q('#motion-risk').textContent,span:q('#motion-span').textContent}}"""


def set_range(page, element: str, to: str) -> None:
    page.evaluate("([id,to])=>{const e=document.getElementById(id);e.value=to==='min'?e.min:to==='max'?e.max:to;"
                  "e.dispatchEvent(new Event('input',{bubbles:true}))}", [element, to])


def motion(page, record, name: str) -> None:
    shown = page.evaluate(SWEEP_MOTION)
    texts = [text for text, _ in shown]
    record(f"{name} Y02 the motion lab shows only speeds the camera's dial has, each one of them",
           set(texts) == set(CAMERA_SHUTTERS) and len(texts) == len(CAMERA_SHUTTERS),
           sorted(set(texts) ^ set(CAMERA_SHUTTERS), key=lambda t: CAMERA_SHUTTERS.index(t) if t in CAMERA_SHUTTERS else -1)[:8])
    record(f"{name} Y02 the shutter slider speaks the speed it shows",
           all(spoken == text for text, spoken in shown), [pair for pair in shown if pair[0] != pair[1]][:3])
    opened = {}
    for mode in ("freeze", "pan", "ghost", "trails", "paint", "zoom"):
        page.locator(f'[data-motion="{mode}"]').click()
        opened[mode] = page.evaluate(READ_MOTION)["shutter"]
    wrong = {mode: shown_at for mode, shown_at in opened.items()
             if shown_at != MOTION_REFERENCE.get(mode, shown_at) or (mode == "trails" and shown_at not in TRAILS)}
    record(f"{name} Y02 each effect opens on the speed the plans shoot it at", not wrong, wrong)
    # Camera shake comes from the time the shutter is open and the hands, not from the subject.
    page.locator('[data-motion="freeze"]').click()
    set_range(page, "motion-speed", "min")
    slow = page.evaluate(READ_MOTION)
    set_range(page, "motion-speed", "max")
    fast = page.evaluate(READ_MOTION)
    record(f"{name} Y02 how fast the subject moves changes its trace, not the camera's shake",
           slow["risk"] == fast["risk"] and slow["span"] != fast["span"], [slow, fast])
    set_range(page, "motion-shutter", "max")
    long = page.evaluate(READ_MOTION)
    set_range(page, "motion-shutter", "min")
    short = page.evaluate(READ_MOTION)
    record(f"{name} Y02 a long exposure asks for a tripod and a short one does not",
           "trípode" in long["risk"] and "trípode" not in short["risk"], [long, short])


def boxes(page) -> dict:
    return page.evaluate("""()=>{const r=e=>{const b=e.getBoundingClientRect();return{l:b.left,r:b.right,t:b.top,b:b.bottom}};
    return{stage:r(document.getElementById('comp-stage')),subject:r(document.getElementById('comp-subject')),
    label:r(document.querySelector('#comp-stage .comp-neg'))}}""")


def composition(page, record, name: str) -> None:
    stage = page.locator("#comp-stage")
    stage.scroll_into_view_if_needed()
    bad = []
    for fx, fy in ((0.33, 0.66), (0.67, 0.66), (0.9, 0.12), (0.1, 0.88), (0.5, 0.5), (0.88, 0.5)):
        box = stage.bounding_box()
        page.mouse.click(box["x"] + fx * box["width"], box["y"] + fy * box["height"])
        b = boxes(page)
        s, lab, st = b["subject"], b["label"], b["stage"]
        overlap = not (lab["r"] <= s["l"] or lab["l"] >= s["r"] or lab["b"] <= s["t"] or lab["t"] >= s["b"])
        middle = (st["l"] + st["r"]) / 2
        subject_x, label_x = (s["l"] + s["r"]) / 2, (lab["l"] + lab["r"]) / 2
        wrong_side = abs(subject_x - middle) > 0.1 * (st["r"] - st["l"]) and (subject_x - middle) * (label_x - middle) > 0
        inside = lab["l"] >= st["l"] - 0.5 and lab["r"] <= st["r"] + 0.5 and lab["t"] >= st["t"] - 0.5 and lab["b"] <= st["b"] + 0.5
        if overlap or wrong_side or not inside:
            bad.append({"at": (fx, fy), "overlap": overlap, "wrong_side": wrong_side, "inside": inside})
    record(f"{name} Y03 «espacio negativo» sits in the emptier side of the frame, clear of the subject", not bad, bad)


PRESSED = "sel=>[...document.querySelectorAll(sel)].map(b=>b.getAttribute('aria-pressed'))"


def toggles(page, record, name: str) -> None:
    for group, selector in (("motion", "[data-motion]"), ("pose", "#pose-coach-buttons button[data-pose]")):
        count = page.locator(selector).count()
        wrong = []
        for i in range(count):
            page.locator(selector).nth(i).click()
            states = page.evaluate(PRESSED, selector)
            if states != ["true" if j == i else "false" for j in range(count)]:
                wrong.append((i, states))
        record(f"{name} Y04 the {group} buttons say which one is on", count > 1 and not wrong, wrong[:3])
    guide = page.locator('[data-comp="center"]')
    before = guide.get_attribute("aria-pressed")
    guide.click()
    on = guide.get_attribute("aria-pressed")
    guide.click()
    off = guide.get_attribute("aria-pressed")
    thirds = page.locator('[data-comp="third"]').get_attribute("aria-pressed")
    record(f"{name} Y04 each composition guide says whether it is shown",
           (before, on, off, thirds) == ("false", "true", "false", "true"), (before, on, off, thirds))
    spoken = page.evaluate("""()=>({comp:document.getElementById('comp-reading').getAttribute('aria-live'),
      stage:(document.getElementById('comp-stage').getAttribute('aria-describedby')||'').split(' '),
      pose:document.getElementById('pose-coach-title').getAttribute('aria-live'),
      motion:document.getElementById('motion-caption').getAttribute('aria-live')})""")
    record(f"{name} Y04 what the composition, pose and motion labs change is read out",
           spoken["comp"] == "polite" and "comp-reading" in spoken["stage"] and spoken["pose"] == "polite"
           and spoken["motion"] == "polite", spoken)


def check(browser, url: str, record, name: str) -> None:
    for width, height in ((320, 640), (1280, 900)):
        page = browser.new_page(viewport={"width": width, "height": height})
        errors: list[str] = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url, wait_until="load")
        tag = f"{name} {width}px"
        presets(page, record, tag)
        motion(page, record, tag)
        composition(page, record, tag)
        toggles(page, record, tag)
        record(f"{tag} Y01-Y04 labs ran without script errors", not errors, errors[:3])
        page.close()
