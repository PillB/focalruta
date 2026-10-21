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
section a link jumps to. The page reserves that room with scroll-padding (technique C43).
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

# In-page links in the bars and the skip link, with where each one jumps.
JUMPS = """() => [...document.querySelectorAll('nav.glass a[href^="#"], .mobile-bottom-nav a[href^="#"], a.skip-link[href^="#"]')]
  .map(a => a.getAttribute('href')).filter(h => h.length > 1 && document.getElementById(h.slice(1)))"""

LANDED = """(href) => {
  document.querySelector(`a[href="${href}"]`).click();
  const box = e => e.getBoundingClientRect(), nav = box(document.querySelector('nav.glass'));
  const bar = box(document.getElementById('toggle-human').closest('section'));
  let floor = nav.top <= 0 && nav.bottom > 0 ? nav.bottom : 0;
  if (bar.top <= floor && bar.bottom > floor) floor = bar.bottom;
  const doc = document.documentElement;
  return {top: Math.round(box(document.getElementById(href.slice(1))).top), floor: Math.round(floor),
          edge: scrollY <= 0 || Math.ceil(scrollY + innerHeight) >= doc.scrollHeight - 1};
}"""

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


def jumps(page) -> list[str]:
    """Follow every in-page link in the bars; list the sections that start behind a bar or far below it.

    A jump that ends at the top or the bottom of the page cannot place its section, so only
    "behind" counts there: at the very top nothing is stuck yet.
    """
    wrong = []
    for href in page.evaluate(JUMPS):
        page.evaluate("scrollTo({top: 0, behavior: 'instant'})")
        landed = page.evaluate(LANDED, href)
        if landed["edge"] and page.evaluate("scrollY") <= 0:
            continue
        if landed["top"] < landed["floor"] or (landed["top"] > landed["floor"] + LANDING and not landed["edge"]):
            wrong.append(f"{href} starts at {landed['top']} px, what stays ends at {landed['floor']} px")
    return wrong


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
        page.wait_for_timeout(300)
        moved = page.evaluate(SEEN) - opened["top"]
        if moved:
            wrong.append(f"{opened['name']}: the page moved {moved} px")
    return wrong
