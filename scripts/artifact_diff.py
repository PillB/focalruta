#!/usr/bin/env python3
"""Locate where two artifacts diverge, instead of only reporting that they do.

The release gates compare whole generated files. Reporting "regenerate it" is
useless on a 400 KB page whose longest line is 273 747 characters: it reads the
same for a stray byte and for an empty file.

Measured on the real challenge page with one attribute renamed:

    line-level unified_diff   5 lines, longest 273 750 chars   unusable
    tag-normalized diff       7 lines, longest 109 chars       readable
    first differing offset    offset 12 062 of 398 880         exact

So this module does both: an exact offset with a context window, and a
tag-normalized diff a human can read. Text and bytes are both supported, since
ZIP members and binaries go through the same gates.
"""
from __future__ import annotations

import difflib
import re
from dataclasses import dataclass

CONTEXT = 90
MAX_DIFF_LINES = 40
MAX_LINE = 160
_TAG_BOUNDARY = re.compile(r"><")


@dataclass(frozen=True)
class Difference:
    """Where two artifacts first diverge, with a window of either side."""

    offset: int
    expected_window: str
    actual_window: str
    expected_length: int
    actual_length: int


def _as_text(value: str | bytes) -> str:
    return value.decode("utf-8", errors="replace") if isinstance(value, bytes) else value


def _window(text: str, offset: int) -> str:
    return text[max(0, offset - CONTEXT): offset + CONTEXT]


def first_difference(expected: str | bytes, actual: str | bytes) -> Difference | None:
    """First differing index, or None. Truncation reports the truncation point."""
    if expected == actual:
        return None
    shared = min(len(expected), len(actual))
    offset = next((index for index in range(shared) if expected[index] != actual[index]), shared)
    expected_text, actual_text = _as_text(expected), _as_text(actual)
    return Difference(
        offset=offset,
        expected_window=_window(expected_text, offset),
        actual_window=_window(actual_text, offset),
        expected_length=len(expected),
        actual_length=len(actual),
    )


def _normalized_lines(value: str | bytes) -> list[str]:
    """Split between adjacent tags so a minified artifact becomes diffable."""
    text = _TAG_BOUNDARY.sub(">\n<", _as_text(value))
    return [line if len(line) <= MAX_LINE else line[:MAX_LINE] + "…" for line in text.splitlines(keepends=True)]


def readable_diff(expected: str | bytes, actual: str | bytes) -> str:
    """A bounded, tag-normalized unified diff."""
    rows = difflib.unified_diff(
        _normalized_lines(expected), _normalized_lines(actual),
        fromfile="expected", tofile="actual", n=1, lineterm="",
    )
    kept = [row.rstrip("\n") for _, row in zip(range(MAX_DIFF_LINES), rows)]
    return "\n".join(kept)


def describe(expected: str | bytes, actual: str | bytes, label: str) -> str | None:
    """The message a failing gate should print, or None when they match."""
    found = first_difference(expected, actual)
    if found is None:
        return None
    size = (
        f"same length ({found.expected_length} bytes)"
        if found.expected_length == found.actual_length
        else f"expected {found.expected_length} bytes, got {found.actual_length}"
    )
    return (
        f"{label}: first difference at offset {found.offset} of {found.expected_length} ({size})\n"
        f"  expected …{found.expected_window!r}\n"
        f"  actual   …{found.actual_window!r}\n"
        f"{readable_diff(expected, actual)}"
    )
