"""A failed parity check must say WHERE the artifacts diverge.

Requirements: M01, M04, M05, O03. The release gates reduce every comparison to
a boolean before reporting, so today a one-byte regression and an empty file
produce the same message. These tests pin the diagnostics, not the detection.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

import artifact_diff as ad

PAGE = "<html><body><p>uno</p><p>dos</p><p>tres</p></body></html>"


def test_identical_artifacts_report_nothing():
    assert ad.first_difference(PAGE, PAGE) is None
    assert ad.describe(PAGE, PAGE, "página") is None


def test_offset_points_at_the_first_differing_character():
    actual = PAGE.replace("dos", "DOS", 1)
    found = ad.first_difference(PAGE, actual)
    assert found is not None
    assert found.offset == PAGE.index("dos")
    assert "dos" in found.expected_window and "DOS" in found.actual_window


def test_difference_at_the_very_start_is_offset_zero():
    found = ad.first_difference(PAGE, "X" + PAGE[1:])
    assert found.offset == 0


def test_truncation_is_reported_at_the_truncation_point():
    truncated = PAGE[:-12]
    found = ad.first_difference(PAGE, truncated)
    assert found.offset == len(truncated)
    assert found.expected_length == len(PAGE)
    assert found.actual_length == len(truncated)


def test_pure_insertion_at_the_end_is_located():
    found = ad.first_difference(PAGE, PAGE + "<!-- extra -->")
    assert found.offset == len(PAGE)
    assert found.actual_length > found.expected_length


def test_readable_diff_does_not_dump_a_whole_minified_line():
    """The real artifacts have single lines of 273k characters."""
    long_expected = "<div>" + "<span>x</span>" * 4000 + "</div>"
    long_actual = long_expected.replace("<span>x</span>", "<span>y</span>", 1)
    lines = ad.readable_diff(long_expected, long_actual).splitlines()
    assert lines, "a difference must produce a readable diff"
    assert max(len(line) for line in lines) < 200
    assert any("y" in line for line in lines)


def test_readable_diff_is_bounded_when_everything_differs():
    lines = ad.readable_diff("<a>1</a>" * 500, "<b>2</b>" * 500).splitlines()
    assert len(lines) <= ad.MAX_DIFF_LINES


def test_describe_names_the_artifact_and_carries_the_offset():
    message = ad.describe(PAGE, PAGE.replace("tres", "TRES"), "página del reto")
    assert "página del reto" in message
    assert str(PAGE.index("tres")) in message
    assert "TRES" in message


def test_bytes_are_supported_for_zip_members_and_binaries():
    found = ad.first_difference(b"abcdef", b"abcXef")
    assert found.offset == 3
    assert ad.describe(b"abcdef", b"abcdef", "miembro") is None
