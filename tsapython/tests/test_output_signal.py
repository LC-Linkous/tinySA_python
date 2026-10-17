#! /usr/bin/python3
"""
Command-construction tests for the OutputSignalMixin.

Mocked-serial `tsa` fixture; no hardware.

This module has several KNOWN BUGS that are pinned below with the actual
(broken) behavior, so a fix will surface as a failing assertion:
  * the set_cal_output_* aliases call self.caloutput(...) which doesn't exist
    (the method is cal_output) -> AttributeError
  * set_direct_on/off call direct() with one arg, but direct() requires freq
    -> TypeError
  * mode() has a stray '+ +' producing a unary-plus on a str -> TypeError
  * modulation() builds an 'output ...' command instead of 'modulation ...'
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


# --- mode: 'high' is a Basic word; the Ultra family profile refuses it -----

@pytest.mark.parametrize("method,expected", [
    ("set_low_input_mode", "mode low input\r\n"),
    ("set_low_output_mode", "mode low output\r\n"),
])
def test_mode_aliases(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("method", ["set_high_input_mode", "set_high_output_mode"])
def test_mode_high_refused_on_ultra(tsa, method):
    getattr(tsa, method)()
    assert tsa._recorder.count == 0


@pytest.mark.parametrize("method,expected", [
    ("set_high_input_mode", "mode high input\r\n"),
    ("set_high_output_mode", "mode high output\r\n"),
])
def test_mode_aliases_basic(tsa, method, expected):
    tsa.select_existing_device("BASIC")
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


# --- modulation ------------------------------------------------------------
# Current firmware keywords: off|am|fm (Ultra family), off|am|nfm|wfm|extern
# (Basic). The pre-2020 keywords AM_1kHz, AM_10Hz, NFM, WFM are still accepted
# by the library and translated, because current firmware rejects them.

@pytest.mark.parametrize("board,method,expected", [
    ("ZS405", "set_mod_off", ["modulation off\r\n"]),
    ("ZS405", "set_mod_AM", ["modulation am\r\n"]),
    ("ZS405", "set_mod_FM", ["modulation fm\r\n"]),
    ("ZS405", "set_mod_AM_1khz", ["modulation am\r\n", "modulation freq 1000\r\n"]),   # deprecated alias
    ("ZS405", "set_mod_AM_10Hz", ["modulation am\r\n", "modulation freq 10\r\n"]),     # deprecated alias
    ("BASIC", "set_mod_NFM", ["modulation nfm\r\n"]),
    ("BASIC", "set_mod_WFM", ["modulation wfm\r\n"]),
    ("BASIC", "set_mod_extern", ["modulation extern\r\n"]),
    ("BASIC", "set_mod_AM_1khz", ["modulation am\r\n", "modulation freq 1000\r\n"]),
])
def test_modulation_aliases(tsa, board, method, expected):
    tsa.select_existing_device(board)
    getattr(tsa, method)()
    assert tsa._recorder.calls == expected


@pytest.mark.parametrize("board,val", [
    ("ZS405", "am"), ("ZS405", "fm"), ("ZS405", "off"),
    ("BASIC", "am"), ("BASIC", "nfm"), ("BASIC", "wfm"), ("BASIC", "extern"), ("BASIC", "off"),
])
def test_modulation_current_keywords(tsa, board, val):
    tsa.select_existing_device(board)
    tsa.modulation(val)
    assert tsa._recorder.calls == [f"modulation {val}\r\n"]


@pytest.mark.parametrize("board,val", [
    ("ZS405", "nfm"), ("ZS405", "wfm"), ("ZS405", "extern"), ("ZS405", "NFM"), ("BASIC", "fm"),
])
def test_modulation_word_wrong_family_refused(tsa, board, val):
    tsa.select_existing_device(board)
    tsa.modulation(val)
    assert tsa._recorder.count == 0


@pytest.mark.parametrize("method,val,expected", [
    ("modulation_freq", 1000, "modulation freq 1000\r\n"),
    ("modulation_freq", 400.0, "modulation freq 400\r\n"),
    ("modulation_depth", 50, "modulation depth 50\r\n"),
    ("modulation_deviation", 3000, "modulation deviation 3000\r\n"),
])
def test_modulation_parameters(tsa, method, val, expected):
    getattr(tsa, method)(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("method,val", [
    ("modulation_freq", 0),
    ("modulation_freq", 10001),
    ("modulation_freq", "1k"),
    ("modulation_depth", 101),
    ("modulation_depth", -1),
    ("modulation_deviation", 50),
    ("modulation_deviation", 300001),
    ("modulation_deviation", True),
])
def test_modulation_parameters_invalid(tsa, method, val):
    getattr(tsa, method)(val)
    assert tsa._recorder.count == 0


# --- output path (Ultra family): normal|mixer ------------------------------

@pytest.mark.parametrize("method,expected", [
    ("set_output_path_normal", "output normal\r\n"),
    ("set_output_path_mixer", "output mixer\r\n"),
])
def test_output_path(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


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


# --- direct: start/stop now require freq > 0 (positive number) ------------

def test_direct_start_rejects_bad_freq(tsa):
    for bad in (0, -5, None, "x"):
        tsa._recorder.calls.clear()
        tsa.direct("start", bad)
        assert tsa._recorder.count == 0, f"freq={bad!r} should be rejected"


def test_direct_start_accepts_positive_freq(tsa):
    tsa.set_direct_start(900_000_000)
    assert tsa._recorder.last == "direct start 900000000\r\n"
