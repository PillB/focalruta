"""W05-W07 in the browser: the session dialog's shot review, as a reader uses it.

The advice a failed check gives is held to the field card's own «Cuando la foto no sale»
panel on the same page, and the saved review to what a reload, an old tick and a store
that refuses writes leave behind.
"""
from __future__ import annotations

import json

KEY = "canon6d-run-plan_a-human"
READ = """()=>({tally:document.getElementById('run-tally')?.textContent,verdict:document.getElementById('run-verdict')?.textContent,
done:document.getElementById('run-done')?.textContent,title:document.getElementById('run-title')?.textContent,
focus:document.activeElement?.id||document.activeElement?.name||document.activeElement?.tagName,
checked:[...document.querySelectorAll('#run-content input[name^="run-"]:checked')].map(i=>i.name+'='+i.value)})"""
# The field card's rescue advice for a background that will not blur, first sentence.
RESCUE = """()=>{const li=[...document.querySelectorAll('#field-card-modal .fc-rescue')].find(x=>x.querySelector('b')?.textContent==='El fondo no se desenfoca');
return li?li.querySelector('p').textContent.split('. ')[0]:null}"""


def answer(page, key: str, value: str) -> None:
    page.locator(f'label.run-opt:has(input[name="run-{key}"][value="{value}"])').click()


def open_at(page, shot: int) -> None:
    page.evaluate("([n])=>{selectPlan('plan_a');setVariant('human');setTime('day');runIndex=n;openSessionRun()}", [shot])


def first_shot_of(page, technique: str) -> int:
    return page.evaluate("t=>PLANS_DATA.plans.find(p=>p.id==='plan_a').shots.findIndex(s=>s.technique===t)", technique)


def review_flow(page, record, name: str) -> None:
    page.evaluate(f"localStorage.removeItem({json.dumps(KEY)})")
    blur = first_shot_of(page, "poca_pdc")
    open_at(page, blur)
    start = page.evaluate(READ)
    record(f"{name} a new shot waits for its three checks", start["verdict"] == "Responde las tres para cerrar la toma." and start["checked"] == [], start)
    answer(page, "s", "ok")
    answer(page, "e", "ok")
    answer(page, "i", "no")
    failed = page.evaluate(READ)
    rescue = page.evaluate(RESCUE)
    record(f"{name} a failed intent gives the field card's own advice", bool(rescue) and rescue in failed["verdict"] and "Repite" in failed["verdict"], [rescue, failed["verdict"]])
    record(f"{name} the tally counts the shot to repeat", failed["tally"].endswith("0 de 10 aprobadas · 1 por repetir") or failed["tally"] == "0 de 10 aprobadas · 1 por repetir", failed["tally"])
    record(f"{name} answering keeps focus on the answer", failed["focus"] == "run-i", failed["focus"])
    page.keyboard.press("ArrowLeft")  # back to «Sí» in the same group, by keyboard alone
    fixed = page.evaluate(READ)
    record(f"{name} the keyboard changes an answer and the verdict follows", "✓ Aprobada" in fixed["verdict"] and fixed["done"] == "✓ Aprobada", fixed)
    page.keyboard.press("Escape")
    page.reload(wait_until="load")
    open_at(page, blur)
    kept = page.evaluate(READ)
    record(f"{name} each answer survives a reload", kept["checked"] == ["run-s=ok", "run-e=ok", "run-i=ok"] and kept["tally"] == "1 de 10 aprobadas · 0 por repetir", kept)
    page.click("#run-next")
    page.click("#run-done")
    quick = page.evaluate(READ)
    record(f"{name} «Todo bien» passes a shot in one tap", "✓ Aprobada" in quick["verdict"] and len(quick["checked"]) == 3 and quick["tally"] == "2 de 10 aprobadas · 0 por repetir", quick)
    page.keyboard.press("Escape")


def summary_flow(page, record, name: str) -> None:
    page.evaluate(f"localStorage.setItem({json.dumps(KEY)}, JSON.stringify([true,{{s:'no',e:'ok',i:'ok'}},{{s:'ok',e:'over',i:'ok'}},{{s:'no',e:'ok',i:'no'}}]))")
    page.reload(wait_until="load")
    open_at(page, 0)
    old = page.evaluate(READ)
    record(f"{name} an old tick counts as passed", "antes de que existiera la revisión" in old["verdict"] and old["tally"] == "1 de 10 aprobadas · 3 por repetir", old)
    page.click("#run-summary-open")
    text = page.locator("#run-content").inner_text()
    record(f"{name} the summary counts the session", "1 de 10 aprobadas · 3 por repetir · 6 sin revisar." in text and "Lo que más falló: nitidez" in text, text[:300])
    page.locator('#run-content [data-run-go="3"]').click()
    went = page.evaluate(READ)
    record(f"{name} a shot to repeat opens from the summary with focus on its title", " 4/10 " in went["title"] and went["focus"] == "run-title" and "run-s=no" in went["checked"], went)
    page.click("#run-summary-open")
    page.once("dialog", lambda dialog: dialog.accept())
    page.click("#run-reset")
    cleared = page.evaluate(READ)
    stored = page.evaluate(f"localStorage.getItem({json.dumps(KEY)})")
    record(f"{name} clearing the review empties this plan's store", cleared["tally"] == "0 de 10 aprobadas · 0 por repetir" and json.loads(stored) == [None] * 10, [cleared["tally"], stored])
    page.keyboard.press("Escape")


def refused_store(browser, url: str, record, name: str) -> None:
    """A browser that refuses writes (Safari private mode, a full quota): answers still count."""
    context = browser.new_context(viewport={"width": 390, "height": 844})
    context.add_init_script("Storage.prototype.setItem=function(){throw new DOMException('quota','QuotaExceededError')}")
    page = context.new_page()
    errors = []
    page.on("pageerror", lambda error: errors.append(str(error)))
    page.goto(url, wait_until="load", timeout=60000)
    open_at(page, 0)
    page.click("#run-done")
    page.click("#run-next")
    page.click("#run-prev")
    state = page.evaluate(READ)
    record(f"{name} with storage refused the review is kept for the session", "✓ Aprobada" in state["verdict"] and not errors, [state, errors])
    context.close()


def check(browser, url: str, record, name: str) -> None:
    for width in (320, 1280):
        page = browser.new_page(viewport={"width": width, "height": 900})
        errors = []
        page.on("pageerror", lambda error: errors.append(str(error)))
        page.goto(url, wait_until="load", timeout=60000)
        if not page.evaluate("!!window.FocalRutaRevision"):
            record(f"{name} {width} shot review on the page", False, "no FocalRutaRevision")
        review_flow(page, record, f"{name} {width}")
        summary_flow(page, record, f"{name} {width}")
        record(f"{name} {width} shot review errors", not errors, errors)
        page.close()
    refused_store(browser, url, record, name)
