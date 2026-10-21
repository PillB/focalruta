"""N10: the home page's top bar keeps its tools in view and shows every control focus lands on.

The top bar holds the section links and four tools: Modo sol, ▶ Sesión, 📋 Tarjeta and PDF.
The row can be longer than the bar, so it scrolls sideways and fades out its last 36 px to say
there is more. Ending the row with the tools put the field card, session mode and PDF past the
end on every computer screen (red team N10). Wherever there is no bottom bar to carry them,
wider than 640 px, the tools must be whole on screen without scrolling anything.

Wherever keyboard focus lands in the top bar, the control must be whole too: not past the end of
a row nor under its fade (WCAG 2.2 SC 2.4.11, and 2.4.12 for no part of it). The browser only
scrolls a row for a control wholly out of it, so one a few px inside the fade kept focus unseen.
"""
from __future__ import annotations

BOTTOM_BAR = 640  # px: the widest screen with the home page's bottom bar
TAB_LIMIT = 40
TOOLS = ('#visibility-toggle, nav.glass [onclick="openSessionRun()"], nav.glass [onclick="openFieldCard()"], '
         'nav.glass [onclick="window.print()"]')

# How much of a control's width the reader sees: what is inside every box that clips it, short
# of the faded end of any box that fades (a mask to transparent over its last N px).
SHOWN = """(el) => {
  const r = el.getBoundingClientRect();
  let left = Math.max(r.left, 0), right = Math.min(r.right, innerWidth);
  for (let a = el.parentElement; a; a = a.parentElement) {
    const s = getComputedStyle(a), b = a.getBoundingClientRect(), mask = s.maskImage || s.webkitMaskImage || 'none';
    if (s.overflowX !== 'visible') { left = Math.max(left, b.left); right = Math.min(right, b.right); }
    if (mask !== 'none') { const fade = /calc\\(100% - ([\\d.]+)px\\)/.exec(mask); right = Math.min(right, b.right - (fade ? +fade[1] : b.width)); }
  }
  return {name: (el.getAttribute('aria-label') || el.textContent).trim().replace(/\\s+/g, ' ').slice(0, 30),
          width: Math.round(r.width), shown: Math.max(0, Math.round(right - left))};
}"""

# Where focus is against the top bar: before it (the skip link), in it, or past it.
WHERE = """() => {
  const nav = document.querySelector('nav.glass'), e = document.activeElement;
  if (nav.contains(e)) return 'in';
  return nav.compareDocumentPosition(e) & Node.DOCUMENT_POSITION_FOLLOWING ? 'past' : 'before';
}"""


def cut(seen: dict) -> str | None:
    """The complaint for a control not whole in view, or None."""
    if seen["shown"] >= seen["width"] - 1:  # a px of rounding
        return None
    return f"{seen['name']}: {seen['shown']} of {seen['width']} px in view"


def tools_in_view(page, width: int) -> list[str]:
    """At the top of the page, with nothing scrolled, list the tools not whole in view where there is no bottom bar."""
    if width <= BOTTOM_BAR:
        return []
    wrong = []
    for i in range(page.evaluate(f"document.querySelectorAll({TOOLS!r}).length")):
        problem = cut(page.evaluate_handle(f"document.querySelectorAll({TOOLS!r})[{i}]").evaluate(SHOWN))
        if problem:
            wrong.append(problem)
    return wrong


def focus_in_top_bar(page) -> list[str]:
    """Tab from the top of the page through the top bar; list each control focus lands on that is not whole in view."""
    wrong = []
    for _ in range(TAB_LIMIT):
        page.keyboard.press("Tab")
        page.wait_for_timeout(50)
        where = page.evaluate(WHERE)
        if where == "past":
            break
        if where == "in":
            problem = cut(page.evaluate_handle("document.activeElement").evaluate(SHOWN))
            if problem:
                wrong.append(problem)
    return wrong
