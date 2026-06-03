#! /usr/bin/python3
"""
Parsing / response-cleaning tests.

These exercise the REAL parsing helpers (clean_return, get_serial_return,
read_until_end_marker) against raw device output captured in the project
README. No hardware required -- the bytes are canned.

Captures are kept in fixtures/device_responses.py so they can be expanded with
freshly collected hardware output (see collect_samples.py).
"""

import pytest
from fixtures.device_responses import RESPONSES


# ---------------------------------------------------------------------------
# clean_return: strips the echoed command + first \r\n from the front,
#               and a trailing 'ch>' from the end.
# ---------------------------------------------------------------------------

def test_clean_return_deviceid(parsing_tsa):
    raw = RESPONSES["deviceid"]["raw"]
    expected = RESPONSES["deviceid"]["cleaned"]
    assert parsing_tsa.clean_return(bytearray(raw)) == bytearray(expected)


def test_clean_return_strips_trailing_frame(parsing_tsa):
    # Real device output always ends '...\r\nch>'. clean_return uses data[:-4],
    # which removes 'ch>' (3 bytes) PLUS the preceding '\n' -- matching the
    # documented cleaned form that keeps the final '\r'. See README example.
    raw = bytearray(b"cmd\r\nPAYLOAD\r\nch>")
    assert parsing_tsa.clean_return(raw) == bytearray(b"PAYLOAD\r")


def test_clean_return_no_chevron_left_intact(parsing_tsa):
    # No trailing 'ch>' -> only the front (command + first \r\n) is stripped.
    raw = bytearray(b"cmd\r\nPAYLOAD\r")
    assert parsing_tsa.clean_return(raw) == bytearray(b"PAYLOAD\r")


def test_clean_return_minus4_eats_byte_before_chevron(parsing_tsa):
    # Documents a known fragility: clean_return strips 4 bytes for a 3-byte
    # 'ch>' marker, so it assumes a byte (normally '\n') precedes it. If 'ch>'
    # appears with no preceding byte in the payload, one real byte is lost.
    # This is intentional given device framing; flagged for the convert/cleanup
    # follow-up rather than changed here.
    raw = bytearray(b"cmd\r\nXch>")          # 'X' sits directly before ch>
    assert parsing_tsa.clean_return(raw) == bytearray(b"")  # X is consumed


# ---------------------------------------------------------------------------
# read_until_end_marker: used by scanraw; reads until the '}' marker.
# ---------------------------------------------------------------------------

def test_read_until_end_marker_basic(parsing_tsa):
    parsing_tsa.ser._buf = b"{xS\nxd\nx\x98\nx]\nx\x02\x0c}trailing"
    out = parsing_tsa.read_until_end_marker(end_marker=b"}")
    assert out.endswith(b"}")
    assert out == bytearray(b"{xS\nxd\nx\x98\nx]\nx\x02\x0c}")
    # remainder is preserved for the next read
    assert parsing_tsa.remaining_buffer == b"trailing"


def test_read_until_end_marker_timeout(parsing_tsa):
    # no marker present -> should time out and return what it has
    parsing_tsa.ser._buf = b"{xS\nxd"  # no closing }
    out = parsing_tsa.read_until_end_marker(end_marker=b"}", timeout=0.05)
    assert out == bytearray(b"{xS\nxd")


# ---------------------------------------------------------------------------
# get_serial_return: reads up to the 'ch>' prompt.
# ---------------------------------------------------------------------------

def test_get_serial_return_reads_to_prompt(parsing_tsa):
    parsing_tsa.ser._buf = b"deviceid\r\ndeviceid 0\r\nch>"
    out = parsing_tsa.get_serial_return()
    # returns through the '>' of the prompt
    assert out.endswith(b">")
    assert b"deviceid 0" in out


# ---------------------------------------------------------------------------
# is_rgb24: color-string validator
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("s,ok", [
    ("0xFF8800", True),
    ("0x000000", True),
    ("0xffffff", True),
    ("0xFF88", False),
    ("FF8800", False),
    ("0xGG8800", False),
    ("0xFF88000", False),
])
def test_is_rgb24(parsing_tsa, s, ok):
    assert parsing_tsa.is_rgb24(s) is ok


# ---------------------------------------------------------------------------
# error_byte_return: toggled by set_error_byte_return
# ---------------------------------------------------------------------------

def test_error_byte_default_empty(parsing_tsa):
    parsing_tsa.set_error_byte_return(False)
    assert parsing_tsa.error_byte_return() == bytearray(b"")


def test_error_byte_explicit(parsing_tsa):
    parsing_tsa.set_error_byte_return(True)
    assert parsing_tsa.error_byte_return() == bytearray(b"ERROR")
