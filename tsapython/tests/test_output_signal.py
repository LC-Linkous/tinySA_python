#! /usr/bin/python3
"""
Command-construction tests for the OutputSignalMixin.

Mocked-serial `tsa` fixture; no hardware.

"""

import pytest


# --- cal_output: direct method works; aliases are broken ------------------

@pytest.mark.parametrize("val,expected", [
    ("off", "caloutput off\r\n"),
    (30, "caloutput 30\r\n"),
    (1, "caloutput 1\r\n"),
])
def test_cal_output_valid(tsa, val, expected):
    tsa.cal_output(val)
    assert tsa._recorder.last == expected


def test_cal_output_invalid(tsa):
    tsa.cal_output(7)
    assert tsa._recorder.count == 0


@pytest.mark.parametrize("method,expected", [
    ("set_cal_output_off", "caloutput off\r\n"),
    ("set_cal_output_30", "caloutput 30\r\n"),
    ("set_cal_output_15", "caloutput 15\r\n"),
    ("set_cal_output_10", "caloutput 10\r\n"),
    ("set_cal_output_4", "caloutput 4\r\n"),
    ("set_cal_output_3", "caloutput 3\r\n"),
    ("set_cal_output_2", "caloutput 2\r\n"),
    ("set_cal_output_1", "caloutput 1\r\n"),
])
def test_cal_output_aliases(tsa, method, expected):
    # FIXED: aliases now call cal_output() correctly.
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


# --- direct: on/off (no freq) vs start/stop (with freq) -------------------

def test_direct_start_with_freq(tsa):
    tsa.set_direct_start(900_000_000)
    assert tsa._recorder.last == "direct start 900000000\r\n"


def test_direct_stop_with_freq(tsa):
    tsa.set_direct_stop(900_000_000)
    assert tsa._recorder.last == "direct stop 900000000\r\n"


@pytest.mark.parametrize("method,expected", [
    ("set_direct_on", "direct on\r\n"),
    ("set_direct_off", "direct off\r\n"),
])
def test_direct_on_off_aliases(tsa, method, expected):
    # FIXED: direct() now defaults freq=None so on/off aliases work.
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


# --- mode: stray '+ +' makes every call raise -----------------------------

@pytest.mark.parametrize("method,expected", [
    ("set_low_input_mode", "mode low input\r\n"),
    ("set_low_output_mode", "mode low output\r\n"),
    ("set_high_input_mode", "mode high input\r\n"),
    ("set_high_output_mode", "mode high output\r\n"),
])
def test_mode_aliases(tsa, method, expected):
    # FIXED: removed the stray '+ +' in mode().
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


# --- modulation: builds an 'output ...' command (bug) but is reachable ----

@pytest.mark.parametrize("method,val", [
    ("set_mod_off", "off"),
    ("set_mod_AM_1khz", "AM_1kHz"),
    ("set_mod_AM_10Hz", "AM_10Hz"),
    ("set_mod_NFM", "NFM"),
    ("set_mod_WFM", "WFM"),
    ("set_mod_extern", "extern"),
])
def test_modulation_aliases(tsa, method, val):
    getattr(tsa, method)()
    assert tsa._recorder.last == f"modulation {val}\r\n"


def test_modulation_invalid(tsa):
    tsa.modulation("telepathy")
    assert tsa._recorder.count == 0


# --- output: on/off (this one is correct) ---------------------------------

@pytest.mark.parametrize("method,expected", [
    ("set_output_on", "output on\r\n"),
    ("set_output_off", "output off\r\n"),
])
def test_output_aliases(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_output_invalid(tsa):
    tsa.output("perhaps")
    assert tsa._recorder.count == 0


# --- ultra: off/on/auto (no freq) vs start/harm (with freq) ---------------

@pytest.mark.parametrize("method,expected", [
    ("set_ultra_on", "ultra on\r\n"),
    ("set_ultra_off", "ultra off\r\n"),
    ("set_ultra_auto", "ultra auto\r\n"),
])
def test_ultra_simple(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_ultra_start_with_freq(tsa):
    tsa.set_ultra_start(800_000_000)
    assert tsa._recorder.last == "ultra start 800000000\r\n"


def test_ultra_harmonic_with_freq(tsa):
    tsa.set_ultra_harmonic(5)
    assert tsa._recorder.last == "ultra harm 5\r\n"