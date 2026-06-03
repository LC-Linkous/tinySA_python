#! /usr/bin/python3
"""
Command-construction tests for the CalibrationMixin.

Mocked-serial `tsa` fixture; no hardware. Frequency-range checks use the seeded
minSADeviceFreq / maxSADeviceFreq from the fixture (100kHz .. 12GHz).

Known bugs are pinned with explicit tests and marked KNOWN BUG.
"""

import pytest


# --- actual_freq: None (get) or in-range int/float ------------------------

def test_actual_freq_get(tsa):
    tsa.get_actual_freq()
    assert tsa._recorder.last == "actual_freq\r\n"


def test_actual_freq_set_valid(tsa):
    tsa.set_actual_freq(3_000_000_000)
    assert tsa._recorder.last == "actual_freq 3000000000\r\n"


@pytest.mark.parametrize("val", [1, 20e9, "x"])   # below min / above max / non-numeric
def test_actual_freq_set_invalid(tsa, val):
    tsa.actual_freq(val)
    assert tsa._recorder.count == 0


# --- freq: in-range int/float ---------------------------------------------

def test_freq_valid(tsa):
    tsa.set_freq(100_000_000)
    assert tsa._recorder.last == "freq 100000000\r\n"


@pytest.mark.parametrize("val", [1, 20e9, "x"])
def test_freq_invalid(tsa, val):
    tsa.freq(val)
    assert tsa._recorder.count == 0


# --- freq_corr / aliases: fixed string ------------------------------------

def test_freq_corr(tsa):
    tsa.freq_corr()
    assert tsa._recorder.last == "freq_corr\r\n"


def test_get_frequency_correction_alias(tsa):
    tsa.get_frequency_correction()
    assert tsa._recorder.last == "freq_corr\r\n"


# --- set_IF: 0/'auto' or 433M..435M ---------------------------------------

@pytest.mark.parametrize("val,expected", [
    (0, "if 0\r\n"),
    ("auto", "if 0\r\n"),
    (434e6, "if 434000000.0\r\n"),
])
def test_set_IF_valid(tsa, val, expected):
    tsa.set_IF(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [100, 500e6])
def test_set_IF_invalid(tsa, val):
    tsa.set_IF(val)
    assert tsa._recorder.count == 0


# --- set_IF1: 0/'auto' or 975M..979M --------------------------------------

@pytest.mark.parametrize("val,expected", [
    (0, "if1 0\r\n"),
    ("auto", "if1 0\r\n"),
    (977e6, "if1 977000000.0\r\n"),
])
def test_set_IF1_valid(tsa, val, expected):
    tsa.set_IF1(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [100, 500e6])
def test_set_IF1_invalid(tsa, val):
    tsa.set_IF1(val)
    assert tsa._recorder.count == 0


# --- spur: on/off ---------------------------------------------------------

@pytest.mark.parametrize("method,expected", [
    ("spur_on", "spur on\r\n"),
    ("spur_off", "spur off\r\n"),
])
def test_spur_aliases(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_spur_invalid(tsa):
    tsa.spur("maybe")
    assert tsa._recorder.count == 0


# --- vbat_offset: None (get) or 0..4095 -----------------------------------

def test_vbat_offset_get(tsa):
    tsa.get_vbat_offset()
    assert tsa._recorder.last == "vbat_offset\r\n"


def test_vbat_offset_set_valid(tsa):
    tsa.set_vbat_offset(300)
    assert tsa._recorder.last == "vbat_offset 300\r\n"


@pytest.mark.parametrize("val", [-1, 4096])
def test_vbat_offset_set_invalid(tsa, val):
    tsa.vbat_offset(val)
    assert tsa._recorder.count == 0


# --- level_offset: table arg + offset -20..20 -----------------------------

def test_level_offset_input(tsa):
    tsa.level_offset("low", 5.0, isOutput=False)
    assert tsa._recorder.last == "leveloffset low 5.0\r\n"


def test_level_offset_output(tsa):
    tsa.level_offset("switch", -3.0, isOutput=True)
    assert tsa._recorder.last == "leveloffset switch output -3.0\r\n"


@pytest.mark.parametrize("val,offset", [
    ("nope", 5.0),      # bad table arg
    ("low", 25.0),      # offset out of range
    ("low", -25.0),
])
def test_level_offset_invalid(tsa, val, offset):
    tsa.level_offset(val, offset)
    assert tsa._recorder.count == 0


# --- correction: dump form (table arg, no slot) ---------------------------

def test_correction_dump(tsa):
    tsa.correction("low")
    assert tsa._recorder.last == "correction low\r\n"


def test_correction_bad_table_arg(tsa):
    tsa.correction("bogus")
    assert tsa._recorder.count == 0


def test_correction_full_set(tsa):
    # valid: table arg + slot 0..19 + in-range freq + in-range dB
    tsa.correction("low", 0, 100_000_000, 5)
    assert tsa._recorder.last == "correction low 0 100000000 5\r\n"


# --- zero: get (None) or set ----------------------------------------------

def test_zero_set(tsa):
    tsa.zero(174)
    assert tsa._recorder.last == "zero 174\r\n"


def test_zero_get_with_none(tsa):
    tsa.zero(None)
    assert tsa._recorder.last == "zero\r\n"


def test_get_zero_offset_is_broken_known_bug(tsa):
    """
    KNOWN BUG: get_zero_offset() calls self.zero() with no argument, but zero()
    has a required positional 'val'. So the alias raises TypeError. Pinned so a
    fix (giving zero() a default, or passing None) is noticed.
    """
    with pytest.raises(TypeError):
        tsa.get_zero_offset()
