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


@pytest.mark.parametrize("method", [
    "set_cal_output_off", "set_cal_output_30", "set_cal_output_15",
    "set_cal_output_10", "set_cal_output_4", "set_cal_output_3",
    "set_cal_output_2", "set_cal_output_1",
])
def test_cal_output_aliases_attributeerror_known_bug(tsa, method):
    """
    KNOWN BUG: these aliases call self.caloutput(...) but the method is named
    cal_output. They raise AttributeError. Fix = rename the call to cal_output.
    """
    with pytest.raises(AttributeError):
        getattr(tsa, method)()


# --- direct: on/off (no freq) vs start/stop (with freq) -------------------

def test_direct_start_with_freq(tsa):
    tsa.set_direct_start(900_000_000)
    assert tsa._recorder.last == "direct start 900000000\r\n"


def test_direct_stop_with_freq(tsa):
    tsa.set_direct_stop(900_000_000)
    assert tsa._recorder.last == "direct stop 900000000\r\n"


@pytest.mark.parametrize("method", ["set_direct_on", "set_direct_off"])
def test_direct_on_off_aliases_typeerror_known_bug(tsa, method):
    """
    KNOWN BUG: set_direct_on/off call direct("on"/"off") but direct() requires
    a second positional 'freq'. They raise TypeError. Fix = give direct() a
    default freq=None, or have the aliases pass freq=None.
    """
    with pytest.raises(TypeError):
        getattr(tsa, method)()


# --- mode: stray '+ +' makes every call raise -----------------------------

@pytest.mark.parametrize("method", [
    "set_low_input_mode", "set_low_output_mode",
    "set_high_input_mode", "set_high_output_mode",
])
def test_mode_typeerror_known_bug(tsa, method):
    """
    KNOWN BUG: mode() builds 'mode '+str(val1)+ + ' '... -- the doubled '+ +'
    applies a unary plus to a string and raises TypeError. Every mode alias is
    currently unusable. Fix = remove the extra '+'.
    """
    with pytest.raises(TypeError):
        getattr(tsa, method)()


# --- modulation: builds an 'output ...' command (bug) but is reachable ----

@pytest.mark.parametrize("method,val", [
    ("set_mod_off", "off"),
    ("set_mod_AM_1khz", "AM_1kHz"),
    ("set_mod_AM_10Hz", "AM_10Hz"),
    ("set_mod_NFM", "NFM"),
    ("set_mod_WFM", "WFM"),
    ("set_mod_extern", "extern"),
])
def test_modulation_aliases_send_output_command_known_bug(tsa, method, val):
    """
    KNOWN BUG: modulation() builds 'output '+val instead of 'modulation '+val.
    Pinned to actual output. Fix = change the command prefix to 'modulation'.
    """
    getattr(tsa, method)()
    assert tsa._recorder.last == f"output {val}\r\n"


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
