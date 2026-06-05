#! /usr/bin/python3
"""
Command-construction tests for the MarkersTracesMixin.

Mocked-serial `tsa` fixture; no hardware.

"""

import pytest


# --- line: 'off' or numeric -----------------------------------------------

def test_line_off_alias(tsa):
    tsa.line_off()
    assert tsa._recorder.last == "line off\r\n"


def test_line_numeric(tsa):
    tsa.set_line(-30)
    assert tsa._recorder.last == "line -30\r\n"


def test_line_invalid(tsa):
    tsa.line("sideways")
    assert tsa._recorder.count == 0


# --- marker: ID + on/off/peak/freq/index ----------------------------------

def test_marker_on_off_peak(tsa):
    tsa.marker(1, "on")
    assert tsa._recorder.last == "marker 1 on\r\n"
    tsa.marker(2, "peak")
    assert tsa._recorder.last == "marker 2 peak\r\n"


def test_marker_numeric(tsa):
    tsa.marker(1, 150000000)
    assert tsa._recorder.last == "marker 1 150000000\r\n"


def test_marker_none_id_invalid(tsa):
    tsa.marker(None, "on")
    assert tsa._recorder.count == 0


@pytest.mark.parametrize("method,word", [
    ("marker_on", "on"), ("marker_off", "off"), ("marker_peak", "peak"),
])
def test_marker_aliases_send_and_return(tsa, method, word):
    # FIXED: aliases now return the device response.
    out = getattr(tsa, method)(1)
    assert tsa._recorder.last == f"marker 1 {word}\r\n"
    assert out == bytearray(b"")             # recorder's canned return


# --- trace_select: int >= 0 -----------------------------------------------

def test_trace_select_valid(tsa):
    tsa.trace_select(1)
    assert tsa._recorder.last == "trace 1\r\n"


@pytest.mark.parametrize("bad", [0, -1])
def test_trace_select_invalid(tsa, bad):
    # traces are 1-indexed; 0 and negatives are rejected
    tsa.trace_select(bad)
    assert tsa._recorder.count == 0


# --- trace_units ----------------------------------------------------------

@pytest.mark.parametrize("unit", ["dBm", "dBmV", "dBuV", "V", "W", "Vpp", "RAW"])
def test_trace_units_valid(tsa, unit):
    tsa.trace_units(1, unit)
    assert tsa._recorder.last == f"trace 1 {unit}\r\n"


def test_trace_units_invalid_unit(tsa):
    tsa.trace_units(1, "furlongs")
    assert tsa._recorder.count == 0


def test_trace_units_invalid_id(tsa):
    tsa.trace_units(0, "dBm")
    assert tsa._recorder.count == 0


# --- trace_toggle ---------------------------------------------------------

def test_trace_toggle_on(tsa):
    tsa.trace_toggle(1, "on")
    assert tsa._recorder.last == "trace 1 view on\r\n"


def test_trace_toggle_off(tsa):
    tsa.trace_toggle(1, "off")
    assert tsa._recorder.last == "trace 1 view off\r\n"


def test_trace_toggle_invalid_val(tsa):
    tsa.trace_toggle(1, "maybe")
    assert tsa._recorder.count == 0


def test_trace_toggle_invalid_id(tsa):
    tsa.trace_toggle(0, "on")
    assert tsa._recorder.count == 0


# --- trace_subtract -------------------------------------------------------

def test_trace_subtract(tsa):
    tsa.trace_subtract(1, 2)
    assert tsa._recorder.last == "trace 1 subtract 2\r\n"


@pytest.mark.parametrize("a,b", [("a", 1), (0, 1), (1, 0)])
def test_trace_subtract_invalid(tsa, a, b):
    tsa.trace_subtract(a, b)
    assert tsa._recorder.count == 0


# --- trace_freeze (the corrected single definition) -----------------------

def test_trace_freeze_valid(tsa):
    tsa.trace_freeze(2)
    assert tsa._recorder.last == "trace 2 freeze\r\n"


@pytest.mark.parametrize("bad", ["two", 0])
def test_trace_freeze_invalid(tsa, bad):
    tsa.trace_freeze(bad)
    assert tsa._recorder.count == 0


# --- trace_action ---------------------------------------------------------

@pytest.mark.parametrize("action", ["copy", "freeze", "subtract", "view", "value"])
def test_trace_action_valid(tsa, action):
    tsa.trace_action(1, action)
    assert tsa._recorder.last == f"trace 1 {action}\r\n"


def test_trace_action_invalid_val(tsa):
    tsa.trace_action(1, "explode")
    assert tsa._recorder.count == 0


def test_trace_action_invalid_id(tsa):
    tsa.trace_action(0, "view")
    assert tsa._recorder.count == 0


def test_trace_copy_sends_copy(tsa):
    tsa.trace_copy(1, 2)
    assert tsa._recorder.last == "trace 1 copy 2\r\n"


def test_trace_copy_invalid_id(tsa):
    tsa.trace_copy(0, 1)
    assert tsa._recorder.count == 0


def test_trace_scale(tsa):
    tsa.trace_scale()
    assert tsa._recorder.last == "trace scale auto\r\n"


def test_trace_value(tsa):
    tsa.trace_value(1)
    assert tsa._recorder.last == "trace 1 value\r\n"


def test_trace_value_invalid_id(tsa):
    tsa.trace_value(0)
    assert tsa._recorder.count == 0