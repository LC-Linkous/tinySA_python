#! /usr/bin/python3
"""
Command-construction tests for the LevelsGainMixin.

These verify that each library method, given valid input, builds the exact
serial command string the device expects, and that invalid input takes the
error path WITHOUT writing to serial. No hardware required.

This module is the template for the other command mixins: one happy-path
assert on the command string, one boundary/invalid assert on the error path.
"""

import pytest


# ---------------------------------------------------------------------------
# agc : accepts "auto" or ints 0..7  (np.arange(0, 8))
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    ("auto", "agc auto\r\n"),
    (0, "agc 0\r\n"),
    (7, "agc 7\r\n"),
])
def test_agc_valid(tsa, val, expected):
    tsa.agc(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [8, -1, "high", 3.5])
def test_agc_invalid_takes_error_path(tsa, val):
    out = tsa.agc(val)
    assert tsa._recorder.count == 0          # never hit serial
    assert out == bytearray(b"")             # default error byte (returnErrorByte False)


def test_agc_invalid_with_error_byte_enabled(tsa):
    tsa.set_error_byte_return(True)
    out = tsa.agc(99)
    assert out == bytearray(b"ERROR")


# ---------------------------------------------------------------------------
# attenuate : accepts "auto" or ints 0..30  (np.arange(0, 31) -> 31 EXCLUDED)
# NOTE: docstring/usage says "0-31" but the code excludes 31. Test documents
#       ACTUAL behavior; see flagged follow-up in the chat.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    ("auto", "attenuate auto\r\n"),
    (0, "attenuate 0\r\n"),
    (30, "attenuate 30\r\n"),
])
def test_attenuate_valid(tsa, val, expected):
    tsa.attenuate(val)
    assert tsa._recorder.last == expected


def test_attenuate_31_currently_rejected(tsa):
    """Documents the off-by-one: 31 is rejected despite the 0-31 usage string."""
    out = tsa.attenuate(31)
    assert tsa._recorder.count == 0
    assert out == bytearray(b"")


# ---------------------------------------------------------------------------
# lna : accepts "on" / "off" only
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    ("on", "lna on\r\n"),
    ("off", "lna off\r\n"),
])
def test_lna_valid(tsa, val, expected):
    tsa.lna(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [1, 0, "ON", "enable", True])
def test_lna_invalid(tsa, val):
    tsa.lna(val)
    assert tsa._recorder.count == 0


# ---------------------------------------------------------------------------
# level : accepts ints -76..13  (np.arange(-76, 14))
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    (-76, "level -76\r\n"),
    (0, "level 0\r\n"),
    (13, "level 13\r\n"),
])
def test_level_valid(tsa, val, expected):
    tsa.level(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [-77, 14, 100])
def test_level_out_of_range(tsa, val):
    tsa.level(val)
    assert tsa._recorder.count == 0


# ---------------------------------------------------------------------------
# ext_gain : accepts int/float in [-100, 100] (inclusive both ends)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    (-100, "ext_gain -100\r\n"),
    (100, "ext_gain 100\r\n"),
    (12.5, "ext_gain 12.5\r\n"),
])
def test_ext_gain_valid(tsa, val, expected):
    tsa.ext_gain(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [-101, 101, "auto"])
def test_ext_gain_invalid(tsa, val):
    tsa.ext_gain(val)
    assert tsa._recorder.count == 0