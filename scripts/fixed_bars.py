"""N9: what stays on screen while a page scrolls, and what it may hide.

The home page and every plan page open with two bars: the site's bar and, under it, the
Sujeto/Hora bar. They stay at the top only where the screen has room for them, measured in
the reader's text size: 40.0625 by 31.25 em, which is 641 px wide (no bottom bar) and 500 px
tall (not a phone on its side) at the default 16 px. On a phone they would cover a fifth to
two fifths of the screen, so they scroll away there, and only the home page's bottom bar
stays. Larger text makes the bars taller and the room they need wider, so a reader with
larger text gets them only where the larger bars still fit.

Wherever a bar stays, nothing may end up behind it: not what keyboard focus lands on, going
forward or back (WCAG 2.2 SC 2.4.11, and 2.4.12 for no part of it), and not the start of a
section a link jumps to, the page is opened at, or the address is changed to on the open page,
also going back and forward between two (P1). The page reserves that room with
scroll-padding (technique C43), measured from the bars' whole boxes, and only for what covers
the top now: the Sujeto/Hora bar counts while it is stuck and shows under the top bar. Moving
between the controls of a bar on screen, with Tab or Shift+Tab, must leave the page where it is
(N13), and so must moving onto a control drawn whole just under what stays (N14), also past the
Sujeto/Hora bar's section, where that bar has gone up under the top bar (N14b). A jump holds its
section in place while the page draws around it, but never against a scroll of the reader's own.
"""
from __future__ import annotations

ROOM_EM = (40.0625, 31.25)  # the smallest width and height at which the bars stay, in em
BOTTOM_BAR = 640  # px: the widest screen with the home page's bottom bar
LANDING = 24  # px: a section a link jumps to starts at most this far below what stays
TAB_LIMIT = 400
SETTLE = 300  # ms: after a jump in one go, sections drawn only near the screen take their real size

# The bars by what they are, so the same probe reads a build from before N9.
BARS = """() => {
  const box = e => { const r = e.getBoundingClientRect(); return {top: Math.round(r.top), bottom: Math.round(r.bottom)} };
  const low = document.querySelector('.mobile-bottom-nav');
  return {nav: box(document.querySelector('nav.glass')), bar: box(document.getElementById('toggle-human').closest('section')),
          low: low && getComputedStyle(low).display !== 'none' ? box(low) : null, height: innerHeight};
}"""

# How much of the focused element is behind a bar, in px of its height: what the page draws
# on top at the middle of each 2 px row, so a bar drawn under the element hides nothing.
# The bars span the page's width, so one point per row is enough.
COVERED = """(el) => {
  const covers = [...document.querySelectorAll('nav.glass, .mobile-bottom-nav'), document.getElementById('toggle-human').closest('section')]
    .filter(c => !c.contains(el));
  const r = el.getBoundingClientRect(), top = Math.max(r.top, 0), bottom = Math.min(r.bottom, innerHeight);
  const x = (Math.max(r.left, 0) + Math.min(r.right, innerWidth)) / 2;
  let hidden = 0;
  for (let y = top + 1; y < bottom; y += 2) {
    const hit = document.elementFromPoint(x, y);
    if (hit && !el.contains(hit) && covers.some(c => c.contains(hit))) hidden += 2;
  }
  const taken = covers.filter(c => ['sticky', 'fixed'].includes(getComputedStyle(c).position)).map(c => c.getBoundingClientRect())
    .filter(b => b.bottom > 0 && b.top < innerHeight).reduce((n, b) => n + Math.min(b.bottom, innerHeight) - Math.max(b.top, 0), 0);
  return {hidden: Math.min(hidden, Math.round(r.height)), shown: Math.round(bottom - top), height: Math.round(r.height), free: Math.round(innerHeight - taken)};
}"""

# At the top of the page every bar sits in its place in the flow: nothing it follows or
# precedes is under it. A bar moved by a leftover offset overlaps its neighbour.
IN_PLACE = """() => {
  const bars = [document.querySelector('nav.glass'), document.getElementById('toggle-human').closest('section')];
  const box = e => e.getBoundingClientRect();
  const out = [];
  for (const bar of bars) {
    const b = box(bar);
    let prev = bar.previousElementSibling, next = bar.nextElementSibling;
    while (prev && !prev.getClientRects().length) prev = prev.previousElementSibling;
    while (next && !next.getClientRects().length) next = next.nextElementSibling;
    if (prev && box(prev).bottom > b.top + 1) out.push(`${bar.tagName.toLowerCase()} overlaps the ${prev.tagName.toLowerCase()} before it by ${Math.round(box(prev).bottom - b.top)} px`);
    if (next && box(next).top < b.bottom - 1) out.push(`${bar.tagName.toLowerCase()} overlaps the ${next.tagName.toLowerCase()} after it by ${Math.round(b.bottom - box(next).top)} px`);
  }
  return out;
}"""

# The element keyboard focus is on, named for the report; null when nothing drawn has it.
FOCUSED = """() => {
  const e = document.activeElement;
  if (!e || e === document.body || !e.getClientRects().length) return null;
  if (!e.dataset.n9) e.dataset.n9 = String(window.__n9 = (window.__n9 || 0) + 1);
  return {key: e.dataset.n9, name: (e.getAttribute('aria-label') || e.textContent || e.id || e.tagName).trim().replace(/\\s+/g, ' ').slice(0, 40)};
}"""

# The dialogs a bar that stays opens. Closed, each gives focus back to its button, which must
# not move the page: with scroll-padding the browser counts a button inside that room as out
# of view and scrolls for it (csswg-drafts#7930). "The page" is what the reader sees, the
# element in the middle of the screen: when the page behind the card is drawn again, sizes
# above can change and the browser keeps that element still by changing the scroll position
# (scroll anchoring), which is right, so the scroll position itself is not the measure.
OPENERS = 'nav.glass [onclick="openFieldCard()"], nav.glass [onclick="openSessionRun()"]'
OPEN = """([selector, i]) => {
  const opener = document.querySelectorAll(selector)[i], r = opener.getBoundingClientRect();
  if (!opener.checkVisibility() || r.bottom <= 0 || r.top >= innerHeight) return null;
  const seen = window.__n9seen = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
  opener.focus({preventScroll: true});
  opener.click();
  return {name: (opener.getAttribute('aria-label') || opener.textContent).trim().slice(0, 30), top: Math.round(seen.getBoundingClientRect().top)};
}"""
SEEN = "() => Math.round(window.__n9seen.getBoundingClientRect().top)"
# When to look after closing, in ms from the last look: soon, and once more after a second, so a move
# the page makes a little later is seen too (red team: a scroll 400 ms after closing went unseen).
LOOKS = (300, 900)

# The room kept at the top follows each bar's whole box (N11; red team note): padding counts, as the
# top bar's padding holds a phone's safe area, and a ResizeObserver watches only the content box
# unless told otherwise. Each bar's padding grows and the room must follow within two frames.
ROOM = """async () => {
  const nav = document.querySelector('nav.glass'), bar = document.getElementById('toggle-human').closest('section');
  nav.style.paddingTop = '40px';
  bar.style.paddingBottom = '48px';
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  const css = getComputedStyle(document.documentElement), wrong = [];
  for (const [name, el, room] of [['top bar', nav, '--fr-nav'], ['Sujeto/Hora bar', bar, '--fr-bar']]) {
    const kept = parseFloat(css.getPropertyValue(room)), height = el.getBoundingClientRect().height;
    if (!(Math.abs(kept - height) < 0.5)) wrong.push(`${name}: ${Math.round(height)} px tall, room kept ${Math.round(kept)} px`);
  }
  nav.style.paddingTop = bar.style.paddingBottom = '';
  return wrong;
}"""

# In-page links in the bars and the skip link, with where each one jumps.
JUMPS = """() => [...document.querySelectorAll('nav.glass a[href^="#"], .mobile-bottom-nav a[href^="#"], a.skip-link[href^="#"]')]
  .map(a => a.getAttribute('href')).filter(h => h.length > 1 && document.getElementById(h.slice(1)))"""

# A jump is judged once the page has drawn what it lands on: sections far from the screen take a
# 1000 px estimate (content-visibility:auto) until then, and those drawn just above the section
# can push it down after the jump (red team N12: 673 px down at 390 px wide, 1909 with larger text).
CLICK = """(href) => document.querySelector(`nav.glass a[href="${href}"], .mobile-bottom-nav a[href="${href}"], a.skip-link[href="${href}"]`).click()"""
# The section a link jumps to that sits lowest on the page, with the most estimated above it.
DEEPEST = f"""() => ({JUMPS})().sort((a, b) => document.getElementById(b.slice(1)).getBoundingClientRect().top -
  document.getElementById(a.slice(1)).getBoundingClientRect().top)[0] || null"""
LANDED = """(href) => {
  const box = e => e.getBoundingClientRect(), nav = box(document.querySelector('nav.glass'));
  const bar = box(document.getElementById('toggle-human').closest('section'));
  let floor = nav.top <= 0 && nav.bottom > 0 ? nav.bottom : 0;
  if (bar.top <= floor && bar.bottom > floor) floor = bar.bottom;
  const doc = document.documentElement;
  return {top: Math.round(box(document.getElementById(href.slice(1))).top), floor: Math.round(floor),
          edge: scrollY <= 0 || Math.ceil(scrollY + innerHeight) >= doc.scrollHeight - 1};
}"""

# Tab between the controls of a bar must leave the page still (N13). With scroll-padding, the
# browser counts a control inside the reserved room as out of view, and on every Tab it scrolled
# the page by about half a screen to center a bar that cannot move (csswg-drafts#7930). Each bar
# is tried where a reader meets it: stuck at the top, the Sujeto/Hora bar also just under the top
# bar on its way up, and whole at the bottom of the screen, clear of the room kept there, where
# nothing needs to move either. Each bar is crossed with Tab and with Shift+Tab, then left and
# entered again, with the reader's motion reduced and with it on.
MOTION = ("reduce", "no-preference")  # the reader's setting: motion reduced, or on as most have it
TABS_IN_BARS = (("top bar", "stuck"), ("Sujeto/Hora bar", "stuck"), ("Sujeto/Hora bar", "under the top bar"),
                ("Sujeto/Hora bar", "at the bottom"))
BAR = """(name) => name === 'top bar' ? document.querySelector('nav.glass') : document.getElementById('toggle-human').closest('section')"""
SPOT = """(where) => {
  const bar = document.getElementById('toggle-human').closest('section').getBoundingClientRect();
  const nav = document.querySelector('nav.glass').getBoundingClientRect();
  const floor = innerHeight - (parseFloat(getComputedStyle(document.documentElement).scrollPaddingBottom) || 0);
  return {top: bar.top, want: where === 'under the top bar' ? Math.max(nav.bottom, 0) + 20 : floor - 8 - bar.height};
}"""
WHOLE = f"""(name) => {{
  const r = ({BAR})(name).getBoundingClientRect();
  return r.top >= 0 && r.bottom <= innerHeight - (parseFloat(getComputedStyle(document.documentElement).scrollPaddingBottom) || 0);
}}"""
# Note what is in the middle of the screen, to tell later whether the page moved. With motion on,
# the browser scrolls over many frames, so every scroll event keeps the farthest the page went.
MARK = f"""(name) => {{
  if (!({WHOLE})(name)) return false;
  const seen = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
  window.__n12 = {{seen, top: seen.getBoundingClientRect().top, worst: 0}};
  if (!window.__n12watch) {{
    window.__n12watch = true;
    addEventListener('scroll', () => {{
      const n = window.__n12, d = Math.round(n.seen.getBoundingClientRect().top - n.top);
      if (Math.abs(d) > Math.abs(n.worst)) n.worst = d;
    }}, {{capture: true, passive: true}});
  }}
  return true;
}}"""
# Wait until the page has stopped scrolling: 150 ms without a scroll event, at most 2 s.
QUIET = """() => new Promise(done => {
  let t = setTimeout(end, 150);
  const on = () => { clearTimeout(t); t = setTimeout(end, 150); };
  function end() { removeEventListener('scroll', on, true); done(); }
  addEventListener('scroll', on, true);
  setTimeout(end, 2000);
})"""
# Focus the bar's first control for Tab, its last for Shift+Tab; 0 when there is nothing to try.
FIRST = f"""([name, key]) => {{
  const controls = [...({BAR})(name).querySelectorAll('a[href], button, input, select, [tabindex]')].filter(e => e.tabIndex >= 0 && e.checkVisibility());
  if (controls.length < 2 || !({MARK})(name)) return 0;
  controls[key === 'Tab' ? 0 : controls.length - 1].focus({{preventScroll: true}});
  return controls.length;
}}"""
MOVED = f"""(name) => {{
  const e = document.activeElement, n = window.__n12, now = Math.round(n.seen.getBoundingClientRect().top - n.top);
  return {{inside: ({BAR})(name).contains(e), name: (e.getAttribute('aria-label') || e.textContent || '').trim().replace(/\\s+/g, ' ').slice(0, 30),
          moved: Math.abs(n.worst) > Math.abs(now) ? n.worst : now}};
}}"""


def has_room(width: int, height: int, text: int = 16) -> bool:
    """Whether the bars stay at this size for a reader whose default text is `text` px."""
    return width >= ROOM_EM[0] * text and height >= ROOM_EM[1] * text


def what_stays(page, width: int, height: int, home: bool, text: int = 16) -> list[str]:
    """Scroll well into the page and list what is wrong with what stays on screen."""
    wrong = list(page.evaluate(IN_PLACE))
    page.evaluate("scrollTo({top: document.documentElement.scrollHeight * 0.6, behavior: 'instant'})")
    page.wait_for_timeout(100)
    seen = page.evaluate(BARS)
    nav, bar, low = seen["nav"], seen["bar"], seen["low"]
    if has_room(width, height, text):
        if nav["top"] != 0:
            wrong.append(f"the top bar scrolled away (top {nav['top']})")
        if not nav["bottom"] - 1 <= bar["top"] <= nav["bottom"]:
            wrong.append(f"the Sujeto/Hora bar is not right under it (top {bar['top']}, top bar ends at {nav['bottom']})")
    else:
        if nav["bottom"] > 0 or bar["bottom"] > 0:
            wrong.append(f"a bar stays on a screen without room for it (top bar {nav}, Sujeto/Hora bar {bar})")
        if home and width <= BOTTOM_BAR and (low is None or low["bottom"] != seen["height"]):
            wrong.append(f"the bottom bar is not at the bottom ({low})")
    return wrong


def tab_through(page, key: str) -> list[str]:
    """Press Tab (or Shift+Tab) through the whole page; list what focus lands on behind a bar."""
    wrong, seen, last = [], set(), None
    for _ in range(TAB_LIMIT):
        page.keyboard.press(key)
        focused = page.evaluate(FOCUSED)
        if focused is None or focused["key"] == last:
            if focused is None and seen:
                break
            continue
        if focused["key"] in seen:
            break
        seen.add(focused["key"])
        last = focused["key"]
        cover = page.evaluate_handle("document.activeElement").evaluate(COVERED)
        roomy = cover["height"] <= cover["free"]
        if cover["hidden"] and (roomy or cover["hidden"] >= cover["shown"]):
            wrong.append(f"{focused['name']}: {cover['hidden']} of {cover['height']} px behind a bar")
    return wrong


def room_follows_bars(page) -> list[str]:
    """Grow each bar's padding; list a bar the room kept at the top did not follow."""
    return page.evaluate(ROOM)


def landing(page, href: str) -> str | None:
    """Once the page has settled, what is wrong with where the section `href` names starts, or None.

    A jump that ends at the top or the bottom of the page cannot place its section, so only
    "behind" counts there: at the very top nothing is stuck yet.
    """
    page.wait_for_timeout(SETTLE)
    landed = page.evaluate(LANDED, href)
    if landed["edge"] and page.evaluate("scrollY") <= 0:
        return None
    if landed["top"] < landed["floor"] or (landed["top"] > landed["floor"] + LANDING and not landed["edge"]):
        return f"{href} starts at {landed['top']} px, what stays ends at {landed['floor']} px"
    return None


def jumps(page) -> list[str]:
    """Follow every in-page link in the bars; list the sections that start behind a bar or far below it."""
    wrong = []
    for href in page.evaluate(JUMPS):
        page.evaluate("scrollTo({top: 0, behavior: 'instant'})")
        page.evaluate(CLICK, href)
        problem = landing(page, href)
        if problem:
            wrong.append(problem)
    return wrong


def address(page, url: str) -> list[str]:
    """Open the page at the address of the lowest section its bars link to (page.html#id), as a shared link would."""
    href = page.evaluate(DEEPEST)
    if not href:
        return []
    page.goto(url + href, wait_until="load", timeout=60000)
    problem = landing(page, href)
    return [f"opened at {problem}"] if problem else []


def dialogs_leave_page_still(page) -> list[str]:
    """Open each dialog from its button in a bar on screen, well into the page, and close it with Escape."""
    wrong = []
    for i in range(page.evaluate(f"document.querySelectorAll({OPENERS!r}).length")):
        page.evaluate("scrollTo({top: Math.round(document.documentElement.scrollHeight * 0.6), behavior: 'instant'})")
        page.wait_for_timeout(SETTLE)
        opened = page.evaluate(OPEN, [OPENERS, i])
        if opened is None:
            continue
        page.wait_for_timeout(300)
        page.keyboard.press("Escape")
        for wait in LOOKS:
            page.wait_for_timeout(wait)
            moved = page.evaluate(SEEN) - opened["top"]
            if moved:
                wrong.append(f"{opened['name']}: the page moved {moved} px")
                break
    return wrong


def place(page, where: str) -> bool:
    """Scroll so the Sujeto/Hora bar is `where`; False when the page cannot put it there."""
    if where == "stuck":
        page.evaluate("scrollTo({top: Math.round(document.documentElement.scrollHeight * 0.6), behavior: 'instant'})")
        page.wait_for_timeout(SETTLE)
        return True
    page.evaluate("scrollTo({top: 0, behavior: 'instant'})")  # a stuck bar's place says nothing of how far to go
    for _ in range(6):  # sections drawn only near the screen change size on the way, so aim again
        spot = page.evaluate(SPOT, where)
        if abs(spot["top"] - spot["want"]) < 1:
            return True
        page.evaluate(f"scrollBy({{top: {spot['top'] - spot['want']}, behavior: 'instant'}})")
        page.wait_for_timeout(150)
    return False


def bar_pass(page, name: str, key: str) -> str | None:
    """From one end of a bar whole on screen, press `key` to its other end, once more out of it, and back in.

    Only the press out of the bar may scroll: showing what comes next is the browser's job.
    Returns the first press that moved the page.
    """
    count = page.evaluate(FIRST, [name, key])  # 0 when the bar is not whole on screen
    back = "Shift+Tab" if key == "Tab" else "Tab"
    for i, press in enumerate([key] * count + [back] * bool(count)):
        page.keyboard.press(press)
        page.wait_for_timeout(50)  # three frames: a scroll, smooth or not, has begun
        if i == count - 1:  # out of the bar: look again from wherever the page comes to rest
            page.evaluate(QUIET)
            if not page.evaluate(MARK, name):
                return None
            continue
        after = page.evaluate(MOVED, name)
        if not after["inside"]:
            return None
        if after["moved"]:
            return f"{press} to {after['name']}: the page moved {after['moved']} px"
    return None


def tab_in_bars_leaves_page_still(page, motions=MOTION) -> list[str]:
    """Tab and Shift+Tab across each bar where a reader meets it, and back in, with each of `motions`;
    list each press that moved the page."""
    wrong = []
    for motion in motions:
        page.emulate_media(reduced_motion=motion)
        for name, where in TABS_IN_BARS:
            for key in ("Tab", "Shift+Tab"):
                moved = place(page, where) and bar_pass(page, name, key)
                if moved:
                    wrong.append(f"{name} {where}{', motion on' if motion != 'reduce' else ''}, {moved}")
    page.emulate_media(reduced_motion=MOTION[0])
    return wrong


# Tab onto a control drawn whole below what is stuck must leave the page still too (red team N14).
# The room kept at the top must be what covers the top now: kept for the Sujeto/Hora bar while that
# bar still sits lower down the page, it made the browser count a control just under the top bar as
# out of view and scroll 330 to 420 px for it (csswg-drafts#7930). Past the end of its section the
# bar has gone up under the top bar, and the room must stop counting it there too (N14b: counted,
# the footer's first link moved the page 17 px). Tried on the last control above the Sujeto/Hora
# bar, the first below it and the first past its section, each placed 1.25 rem under what is stuck,
# past the .75 rem the page keeps clear, and reached with Tab from the control before it and with
# Shift+Tab from the one after. A control the page cannot place there (near the end of a page), or
# one the browser's order skips (a radio group), is not tried.
GAP_REM = 1.25
SIDES = {"above": "above the Sujeto/Hora bar", "below": "below the Sujeto/Hora bar", "past": "past the Sujeto/Hora bar's section"}
FOCUSABLE = ("a[href], area[href], button, input:not([type=hidden]), select, textarea, iframe, object, embed, summary, "
             "audio[controls], video[controls], [contenteditable], [tabindex]")
TOP_FLOOR = """() => {
  const nav = document.querySelector('nav.glass').getBoundingClientRect(), bar = document.getElementById('toggle-human').closest('section').getBoundingClientRect();
  let floor = nav.top <= 0 && nav.bottom > 0 ? nav.bottom : 0;
  if (bar.top <= floor + 0.5 && bar.bottom > floor) floor = bar.bottom;
  return floor;
}"""
PLACE_FREE = f"""async ([side, key, gapRem]) => {{
  const nav = document.querySelector('nav.glass'), bar = document.getElementById('toggle-human').closest('section');
  const all = [...document.querySelectorAll({FOCUSABLE!r})].filter(e => e.tabIndex >= 0 && !e.disabled && !e.closest('[inert]') && e.checkVisibility());
  const after = side !== 'above', step = key === 'Tab' ? -1 : 1, plain = e => e && e.type !== 'radio', box = bar.parentElement;
  const follows = (a, e) => Boolean(a.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING);
  const where = e => side === 'past' ? !box.contains(e) && follows(box, e) : follows(bar, e) === after;
  const order = all.map((e, n) => n).filter(n => !nav.contains(all[n]) && !bar.contains(all[n]) && !all[n].closest('.mobile-bottom-nav, dialog') && where(all[n]));
  const i = (after ? order : order.reverse()).find(n => plain(all[n]) && plain(all[n + step]));
  if (i === undefined) return null;
  const target = all[i], gap = parseFloat(getComputedStyle(document.documentElement).fontSize) * gapRem;
  const floor = {TOP_FLOOR}, frames = () => new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  for (let n = 0; n < 6; n++) {{  // sections drawn only near the screen change size on the way, so aim again
    const off = target.getBoundingClientRect().top - floor() - gap;
    if (Math.abs(off) < 1) break;
    scrollTo({{top: scrollY + off, behavior: 'instant'}});
    await frames();
  }}
  const r = target.getBoundingClientRect(), hit = document.elementFromPoint((r.left + r.right) / 2, (r.top + r.bottom) / 2);
  if (Math.abs(r.top - floor() - gap) >= 1 || r.bottom > innerHeight || r.left < 0 || r.right > innerWidth || !hit || !target.contains(hit)) return null;
  all[i + step].focus({{preventScroll: true}});
  const seen = document.elementFromPoint(innerWidth / 2, innerHeight / 2);
  window.__n14 = {{target, seen, top: seen.getBoundingClientRect().top, worst: 0}};
  if (!window.__n14watch) {{
    window.__n14watch = true;
    addEventListener('scroll', () => {{
      const n = window.__n14, d = Math.round(n.seen.getBoundingClientRect().top - n.top);
      if (Math.abs(d) > Math.abs(n.worst)) n.worst = d;
    }}, {{capture: true, passive: true}});
  }}
  return (target.getAttribute('aria-label') || target.textContent || target.id || target.tagName).trim().replace(/\\s+/g, ' ').slice(0, 30);
}}"""
FREE_MOVED = """() => {
  const n = window.__n14, now = Math.round(n.seen.getBoundingClientRect().top - n.top);
  return {on: document.activeElement === n.target, moved: Math.abs(n.worst) > Math.abs(now) ? n.worst : now};
}"""


def free_pass(page, side: str, key: str) -> str | None:
    """Place a control just under what is stuck, press `key` onto it from its neighbour; how far the page moved, or None."""
    name = page.evaluate(PLACE_FREE, [side, key, GAP_REM])
    if name is None:
        return None
    page.keyboard.press(key)
    page.wait_for_timeout(50)  # three frames: a scroll, smooth or not, has begun
    page.evaluate(QUIET)
    after = page.evaluate(FREE_MOVED)
    if after["on"] and after["moved"]:
        return f"{key} onto {name}, {GAP_REM} rem under what stays ({SIDES[side]}): the page moved {after['moved']} px"
    return None


def free_spots_leave_page_still(page) -> list[str]:
    """Tab and Shift+Tab onto controls drawn whole just under what is stuck, above and below the
    Sujeto/Hora bar and past its section; list each press that moved the page."""
    found = (free_pass(page, side, key) for side in SIDES for key in ("Tab", "Shift+Tab"))
    return [moved for moved in found if moved]


# A reader's own scroll during a jump's hold is kept (red team Q1). The hold repeats a long jump
# while the page draws around it and stops on a wheel, touch, pointer or key; a screen reader's
# scroll or find-in-page sends none of those. Here the page is moved half a screen down from
# script, two frames after the jump, into the section it landed on, which is drawn, and what is
# then in the middle of the screen must stay there. (Moved up instead, the page can land in a
# section not drawn yet, which grows when drawn and moves what is under it whatever the hold does.)
KEPT = f"""async () => {{
  const href = ({DEEPEST})();
  if (!href) return null;
  scrollTo({{top: 0, behavior: 'instant'}});
  ({CLICK})(href);
  await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
  await new Promise(r => setTimeout(r));  // a task of its own, as a screen reader's scroll comes
  scrollTo({{top: scrollY + innerHeight / 2, behavior: 'instant'}});
  const seen = document.elementFromPoint(innerWidth / 2, innerHeight / 2), top = seen.getBoundingClientRect().top;
  await new Promise(r => setTimeout(r, 1000));
  return {{href, moved: Math.round(seen.getBoundingClientRect().top - top)}};
}}"""


def reader_scroll_kept(page) -> list[str]:
    """Jump to the lowest section the bars link to, move the page as a screen reader would; list it if the page moved back."""
    kept = page.evaluate(KEPT)
    if kept and abs(kept["moved"]) > 1:
        return [f"after the jump to {kept['href']}, a scroll of the reader's own was undone: the page moved {kept['moved']} px"]
    return []


# P1 (live check of PR #23): the address changes only its #section on the open page (a typed
# #tecnicas, location.hash), or the reader goes back and forward between two such addresses, with
# motion on as most readers have it. With smooth scrolling for the whole page, the browser glided to
# where the section was before the sections on the way were drawn, and nothing corrected it
# (csswg-drafts#9833): 1480 to 12,136 px off at 390 px wide. Going back glided too and drew the
# sections on the way, so going forward again restored a place that no longer held its section.
# Even in one go, the browser's own jump fell short at some sizes (#tecnicas 560 px at 430 px wide).
# The reader reads on in the lower of the two lowest sections the bars link to, at the address with
# no section; the address changes to that section and then to the lowest; back and forward twice
# must land each section's address clear of the bars and put the address with no section back at the
# scroll position the reader left. Chrome goes to a section's start on back and forward to its address, also on a
# plain page (only where the section has gone does it return to where the reader had scrolled), so
# a section's address is held to its start. Then each section is reached from the top.
READ_ON = 200  # px: how far the reader scrolls on in a section before going elsewhere
STILL = """() => new Promise(done => { let last = scrollY, still = 0, n = 0;
  const frame = () => { still = Math.abs(scrollY - last) < 1 ? still + 1 : 0; last = scrollY;
    if (still >= 10 || ++n > 300) done(); else requestAnimationFrame(frame); };
  requestAnimationFrame(frame); })"""
LOWEST = f"""() => [...new Set(({JUMPS})())].sort((a, b) => document.getElementById(b.slice(1)).getBoundingClientRect().top -
  document.getElementById(a.slice(1)).getBoundingClientRect().top)"""
TOP_OF = "(href) => Math.round(document.getElementById(href.slice(1)).getBoundingClientRect().top)"


def reach(page, href: str, how: str) -> str | None:
    """Change the address to `href`; once the page has stopped moving, what is wrong with where it starts, or None."""
    page.evaluate("href => { location.hash = href }", href)
    page.evaluate(STILL)
    problem = landing(page, href)
    return f"{how} {problem}" if problem else None


def back_and_forward(page, low: str, lowest: str) -> list[str]:
    """Read on in `low` at the address with no section, change the address to `low` and then to `lowest`,
    and go back twice and forward twice. Each section's address lands it clear of the bars, as Chrome
    goes to a section's start on back and forward, also on a plain page; at the address with no section
    the page is left to the browser, which puts it back at the scroll position the reader left. (A section
    above the reader drawn in between, its real size replacing the guess, moves what is there: 24 to 26 px
    at 932x430 and with 20 px text at 650x800, also before P1.) List what does not."""
    page.evaluate("history.replaceState(null, '', location.pathname + location.search)")
    page.evaluate(f"""href => {{ document.getElementById(href.slice(1)).scrollIntoView({{behavior: 'instant'}});
      scrollBy({{top: {READ_ON}, behavior: 'instant'}}) }}""", low)
    page.evaluate(STILL)
    page.wait_for_timeout(SETTLE)
    left = round(page.evaluate("scrollY"))
    wrong = [reach(page, low, "the address changed to"), reach(page, lowest, "the address changed to")]
    for step, href in (("back", low), ("back", None), ("forward", low), ("forward", lowest)):
        page.evaluate(f"history.{step}()")
        page.evaluate(STILL)
        page.wait_for_timeout(SETTLE)
        if href:
            problem = landing(page, href)
            wrong.append(f"{step} to {problem}" if problem else None)
            continue
        back = round(page.evaluate("scrollY"))
        if abs(back - left) > 1:
            wrong.append(f"back to the address with no section: the reader left at {left} px, and it came back at {back} px")
    return [w for w in wrong if w]


def address_changes(page) -> list[str]:
    """With motion on, change only the #section of the address and go back and forward between two;
    list each section that does not land clear of the bars, or a place back does not return to."""
    page.emulate_media(reduced_motion="no-preference")
    hrefs = page.evaluate(LOWEST)
    wrong = back_and_forward(page, hrefs[1], hrefs[0]) if len(hrefs) >= 2 else []
    for href in hrefs:
        page.evaluate("history.replaceState(null, '', location.pathname + location.search); scrollTo({top: 0, behavior: 'instant'})")
        page.evaluate(STILL)
        problem = reach(page, href, "from the top, the address changed to")
        if problem:
            wrong.append(problem)
    page.emulate_media(reduced_motion=MOTION[0])
    return wrong
