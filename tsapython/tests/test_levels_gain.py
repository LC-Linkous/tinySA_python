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
# agc : accepts "auto" or ints 0..7
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
# attenuate : accepts "auto" or ints 0..31, matching the firmware usage string
#             'attenuate 0..31|auto'. (31 was excluded by an off-by-one before.)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    ("auto", "attenuate auto\r\n"),
    (0, "attenuate 0\r\n"),
    (30, "attenuate 30\r\n"),
    (31, "attenuate 31\r\n"),
])
def test_attenuate_valid(tsa, val, expected):
    tsa.attenuate(val)
    assert tsa._recorder.last == expected


def test_attenuate_32_rejected(tsa):
    out = tsa.attenuate(32)
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
# level : the device's output range. ZS405 profile: -76..-6 (low output only);
#         BASIC profile: -76..13 (low and high output)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    (-76, "level -76\r\n"),
    (-30, "level -30\r\n"),
    (-6, "level -6\r\n"),
])
def test_level_valid(tsa, val, expected):
    tsa.level(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [-77, -5, 13, 100])
def test_level_out_of_range_ultra(tsa, val):
    tsa.level(val)
    assert tsa._recorder.count == 0


@pytest.mark.parametrize("val,sent", [(13, True), (0, True), (14, False)])
def test_level_basic_high_output_range(tsa, val, sent):
    tsa.select_existing_device("BASIC")
    tsa.level(val)
    assert (tsa._recorder.count == 1) is sent


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


# ===========================================================================
# Additional coverage: calc, level_change, lna2, and the set_* aliases.
# (These were not in the original test_levels_gain.py and brought the module
#  coverage below the others.)
# ===========================================================================

# --- calc: off|minh|maxh|maxd|aver4|aver16|aver|quasi|log|lin --------------
# 'quasip' is the pre-2022 firmware keyword; it is accepted and sent as 'quasi'.

@pytest.mark.parametrize("method,val", [
    ("set_calc_off", "off"),
    ("set_calc_minh", "minh"),
    ("set_calc_maxh", "maxh"),
    ("set_calc_maxd", "maxd"),
    ("set_calc_aver4", "aver4"),
    ("set_calc_aver16", "aver16"),
    ("set_calc_aver", "aver"),
    ("set_calc_quasi", "quasi"),
    ("set_calc_quasip", "quasi"),
])
def test_calc_aliases(tsa, method, val):
    getattr(tsa, method)()
    assert tsa._recorder.last == f"calc {val}\r\n"


@pytest.mark.parametrize("val", ["log", "lin"])
def test_calc_averaging_domain(tsa, val):
    tsa.calc(val)
    assert tsa._recorder.last == f"calc {val}\r\n"


def test_calc_invalid(tsa):
    tsa.calc("median")
    assert tsa._recorder.count == 0


# --- level_change: -70..70 ------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    (-70, "levelchange -70\r\n"),
    (0, "levelchange 0\r\n"),
    (70, "levelchange 70\r\n"),
])
def test_level_change_valid(tsa, val, expected):
    tsa.set_level_change(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val,expected", [
    (-90, "levelchange -90\r\n"),     # Ultra family range is +-90
    (90, "levelchange 90\r\n"),
    (2.5, "levelchange 2.5\r\n"),     # the firmware reads a float
])
def test_level_change_wider_range(tsa, val, expected):
    tsa.level_change(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [-91, 91, "5", True])
def test_level_change_invalid(tsa, val):
    tsa.level_change(val)
    assert tsa._recorder.count == 0


# --- lna / lna2 -----------------------------------------------------------

def test_lna_on_off_aliases(tsa):
    tsa.set_lna_on()
    assert tsa._recorder.last == "lna on\r\n"
    tsa.set_lna_off()
    assert tsa._recorder.last == "lna off\r\n"


@pytest.mark.parametrize("val,expected", [
    ("auto", "lna2 auto\r\n"),
    (0, "lna2 0\r\n"),
    (7, "lna2 7\r\n"),
])
def test_lna2_valid(tsa, val, expected):
    tsa.set_lna2(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [8, -1, "high"])
def test_lna2_invalid(tsa, val):
    tsa.lna2(val)
    assert tsa._recorder.count == 0


# --- set_* aliases mirror their base methods ------------------------------

def test_set_agc_alias(tsa):
    tsa.set_agc(3)
    assert tsa._recorder.last == "agc 3\r\n"


def test_set_attenuation_alias(tsa):
    tsa.set_attenuation(10)
    assert tsa._recorder.last == "attenuate 10\r\n"


def test_set_ext_gain_alias(tsa):
    tsa.set_ext_gain(20)
    assert tsa._recorder.last == "ext_gain 20\r\n"


def test_set_level_alias(tsa):
    tsa.set_level(-20)
    assert tsa._recorder.last == "level -20\r\n"


# --- level: decimals are valid (the firmware reads a float) ----------------

@pytest.mark.parametrize("val,expected", [
    (-30.5, "level -30.5\r\n"),
    (-76, "level -76\r\n"),
    (-6, "level -6\r\n"),
])
def test_level_decimal_and_limits(tsa, val, expected):
    tsa.level(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [-76.5, -5.9, "low", True, None])
def test_level_out_of_range_or_wrong_type(tsa, val):
    tsa.level(val)
    assert tsa._recorder.count == 0
