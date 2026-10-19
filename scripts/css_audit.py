"""Every declaration and selector in the CSS a page ships is one the browser keeps.

A browser drops what it cannot parse without a word: `font:600 14px/1.2 inherit` left the
field card's "Siguiente toma" and list buttons at the browser's 13.33 px default instead of
16 and 14 px bold. The CSSOM has already thrown such declarations away, so this module reads
the source text; the browser half asks `CSS.supports()` about each declaration and selector.

An HTML comment marker in a stylesheet is worse: `<!--` and `-->` are ignored only between
rules, so the words of `<!-- FIELD CARD CSS START -->` became the start of the next rule's
selector and the browser dropped that whole rule (the card's colours, padding and font on the
home page), and the end marker took the hosted home's `:root` colours with it.

Exempt by design: vendor-prefixed properties, values and pseudo-classes written for another
engine (`-moz-`, `-ms-`, `-webkit-overflow-scrolling`), a standard property written beside its
`-webkit-` twin in the same block (`line-clamp` next to `-webkit-line-clamp`), custom properties
(any value is valid until used), selectors written with `&` (they only parse inside their
parent rule), and descriptor blocks (`@font-face`, `@page`, `@property`), whose entries are not
properties.
"""
from __future__ import annotations

import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

COMMENT = re.compile(r"/\*.*?\*/", re.S)
DESCRIPTOR_BLOCKS = {"@font-face", "@page", "@property", "@counter-style", "@font-feature-values", "@font-palette-values"}
KEYFRAMES = {"@keyframes", "@-webkit-keyframes"}
OTHER_ENGINE = re.compile(r"(?<![\w-])-(?:moz|ms|o)-")
IMPORTANT = re.compile(r"\s*!\s*important\s*$", re.I)


def _scan(text: str, start: int, stop: str) -> int:
    """Index of the first `stop` character at depth zero, outside strings and brackets."""
    depth, quote, i = 0, "", start
    while i < len(text):
        char = text[i]
        if quote:
            if char == "\\":
                i += 1
            elif char == quote:
                quote = ""
        elif char in "\"'":
            quote = char
        elif char in "([":
            depth += 1
        elif char in ")]":
            depth = max(0, depth - 1)
        elif depth == 0 and char in stop:
            return i
        i += 1
    return len(text)


def _matching_brace(text: str, open_at: int) -> int:
    depth, i = 0, open_at
    while i < len(text):
        i = _scan(text, i, "{}")
        if i >= len(text):
            return i
        depth += 1 if text[i] == "{" else -1
        if depth == 0:
            return i
        i += 1
    return i


def _declaration(item: str, selector: str, block: int, out: dict) -> None:
    name, colon, value = item.partition(":")
    name = name.strip()
    if colon and name and not name.startswith("@"):
        out["declarations"].append({"selector": selector, "block": block, "property": name.lower(),
                                    "value": IMPORTANT.sub("", value.strip())})


def _rule(prelude: str, body: str, selector: str, out: dict) -> None:
    keyword = prelude.split(None, 1)[0].lower() if prelude.startswith("@") else ""
    if keyword in DESCRIPTOR_BLOCKS:
        return
    if keyword in KEYFRAMES:
        _block(body, f"{prelude} (fotograma)", out, keyframes=True)
        return
    if keyword:
        _block(body, selector, out)
        return
    out["selectors"].append(prelude)
    _block(body, prelude, out)


def _block(text: str, selector: str, out: dict, keyframes: bool = False) -> None:
    """Read declarations and nested rules from the inside of one block (or a whole sheet)."""
    out["blocks"] += 1
    block, i = out["blocks"], 0
    while i < len(text):
        end = _scan(text, i, ";{}")
        item = text[i:end].strip()
        if end < len(text) and text[end] == "{":
            close = _matching_brace(text, end)
            prelude = re.sub(r"\s+", " ", item)
            if keyframes:
                _block(text[end + 1:close], selector, out)
            else:
                _rule(prelude, text[end + 1:close], selector, out)
            i = close + 1
            continue
        if item:
            _declaration(item, selector, block, out)
        i = end + 1


def parse(css: str) -> dict:
    """Every declaration (with the selector it sits under) and every style rule's selector list."""
    out: dict = {"declarations": [], "selectors": [], "blocks": 0}
    _block(COMMENT.sub("", css), "(hoja)", out)
    return out


def split_selector_list(selector_list: str) -> list[str]:
    parts, i = [], 0
    while i <= len(selector_list):
        end = _scan(selector_list, i, ",")
        parts.append(selector_list[i:end].strip())
        i = end + 1
    return [part for part in parts if part]


def checkable(parsed: dict) -> dict:
    """What the browser is asked about: declarations and selector lists meant for this engine."""
    prefixed = {(d["block"], d["property"]) for d in parsed["declarations"] if d["property"].startswith("-webkit-")}
    declarations = [d for d in parsed["declarations"]
                    if not d["property"].startswith("-") and not OTHER_ENGINE.search(d["value"])
                    and (d["block"], "-webkit-" + d["property"]) not in prefixed]
    selectors = []
    for selector_list in parsed["selectors"]:
        parts = [part for part in split_selector_list(selector_list) if "&" not in part]
        own = [part for part in parts if not OTHER_ENGINE.search(part)]
        if own:
            # A list that mixes another engine's pseudo-class with ours is dropped whole.
            selectors.append({"list": selector_list, "parts": parts})
    return {"declarations": declarations, "selectors": selectors}


class _Styles(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.inline: list[str] = []
        self.links: list[str] = []
        self._in_style = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "style":
            self._in_style = True
            self.inline.append("")
        elif tag == "link" and "stylesheet" in (attrs.get("rel") or "").split():
            self.links.append(attrs.get("href") or "")

    def handle_endtag(self, tag):
        if tag == "style":
            self._in_style = False

    def handle_data(self, data):
        if self._in_style:
            self.inline[-1] += data


def page_css(page: Path) -> list[tuple[str, str]]:
    """(name, text) of every stylesheet a page carries: inline, and linked files beside it."""
    styles = _Styles()
    styles.feed(page.read_text(encoding="utf-8"))
    sheets = [(f"{page.name} <style> {n + 1}", text) for n, text in enumerate(styles.inline)]
    for href in styles.links:
        split = urlsplit(href)
        if split.scheme or split.netloc:
            continue
        target = (page.parent / split.path).resolve()
        if target.is_file():
            sheets.append((target.name, target.read_text(encoding="utf-8")))
    return sheets


# Runs in the page: what the browser would drop, out of what `checkable()` returns. A selector
# list is tried as a rule of its own, which is how the browser takes it (`CSS.supports` with
# `selector()` refuses some pseudo-elements a stylesheet accepts, such as ::-webkit-search-decoration).
DROPPED = """({declarations, selectors}) => {
  const sheet = new CSSStyleSheet();
  const parses = list => { try { sheet.insertRule(`${list}{}`, 0); sheet.deleteRule(0); return true } catch (e) { return false } };
  return {
    declarations: declarations.filter(d => !d.property.startsWith('--') && !CSS.supports(d.property, d.value))
      .map(d => `${d.selector} { ${d.property}: ${d.value} }`),
    selectors: selectors.filter(s => s.parts.length && !parses(s.parts.join(','))).map(s => s.list)};
}"""


# The home page shows the card in a dialog, from the same markup as the card's own page, so
# element i of one is element i of the other. For each element, what a reader sees of it:
# whether it is drawn, its background, padding, corners and each border a reader can see,
# and, for an element with text of its own, the text's colour, size, weight, font and leading.
CARD_LOOK = """(root) => { const app = document.querySelector(root);
  return [app, ...app.querySelectorAll('*')].map(e => {
    const r = e.getBoundingClientRect(), c = getComputedStyle(e);
    const look = {drawn: r.width > 0 && r.height > 0, background: c.backgroundColor, padding: c.padding, corners: c.borderRadius};
    for (const side of ['top', 'right', 'bottom', 'left']) {
      const width = c.getPropertyValue(`border-${side}-width`);
      look[`border-${side}`] = width === '0px' || c.getPropertyValue(`border-${side}-style`) === 'none' ? 'none'
        : `${width} ${c.getPropertyValue(`border-${side}-style`)} ${c.getPropertyValue(`border-${side}-color`)}`;
    }
    if ([...e.childNodes].some(n => n.nodeType === 3 && n.textContent.trim()))
      Object.assign(look, {color: c.color, size: c.fontSize, weight: c.fontWeight, font: c.fontFamily, leading: c.lineHeight, digits: c.fontVariantNumeric});
    const classes = typeof e.className === 'string' && e.className.trim() ? '.' + e.className.trim().split(/\\s+/).join('.') : '';
    return {name: e.tagName.toLowerCase() + (e.id ? '#' + e.id : '') + classes, look};
  }); }"""


def card_differences(card_page: list[dict], home: list[dict]) -> list[str]:
    """Where the home page's card looks different from the card's own page, element by element."""
    if len(card_page) != len(home):
        return [f"{len(card_page)} elements on the card page, {len(home)} in the home page's card"]
    out = []
    for own, embedded in zip(card_page, home):
        for key, value in own["look"].items():
            if embedded["look"].get(key) != value:
                out.append(f"{own['name']} {key}: {value} ≠ {embedded['look'].get(key)}")
    return out
