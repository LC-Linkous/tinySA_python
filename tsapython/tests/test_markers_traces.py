#! /usr/bin/python3
"""
Command-construction tests for the MarkersTracesMixin.

Mocked-serial `tsa` fixture; no hardware.

Several methods have KNOWN BUGS (pinned below): the marker_* aliases don't
return their result, trace_copy builds a 'subtract' command, and a few
trace_* methods omit a space in the command string. Tests pin ACTUAL behavior
so a future fix is noticed (the assertion will change when the bug is fixed).
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


@pytest.mark.parametrize("method", ["marker_on", "marker_off", "marker_peak"])
def test_marker_aliases_send_but_return_none_known_bug(tsa, method):
    """
    The marker_on/off/peak aliases build and send the correct command, but they
    do NOT return msgbytes (missing 'return' in the alias). Pinned: command is
    sent correctly, return is None. When the aliases add 'return', update this
    to assert the returned bytearray.
    """
    out = getattr(tsa, method)(1)
    assert tsa._recorder.count == 1          # command WAS sent
    assert out is None                       # KNOWN BUG: alias swallows return


# --- trace_select: int >= 0 -----------------------------------------------

def test_trace_select_valid(tsa):
    tsa.trace_select(0)
    assert tsa._recorder.last == "trace 0\r\n"


def test_trace_select_invalid(tsa):
    tsa.trace_select(-1)
    assert tsa._recorder.count == 0


# --- trace_units ----------------------------------------------------------

@pytest.mark.parametrize("unit", ["dBm", "dBmV", "dBuV", "V", "W", "Vpp", "RAW"])
def test_trace_units_valid(tsa, unit):
    tsa.trace_units(unit)
    assert tsa._recorder.last == f"trace {unit}\r\n"


def test_trace_units_invalid(tsa):
    tsa.trace_units("furlongs")
    assert tsa._recorder.count == 0


# --- trace_toggle ---------------------------------------------------------

def test_trace_toggle_on(tsa):
    tsa.trace_toggle(0, "on")
    assert tsa._recorder.last == "trace0 on\r\n"


def test_trace_toggle_invalid(tsa):
    tsa.trace_toggle(0, "maybe")
    assert tsa._recorder.count == 0


# --- trace_subtract -------------------------------------------------------

def test_trace_subtract(tsa):
    tsa.trace_subtract(0, 1)
    assert tsa._recorder.last == "trace0 subtract 1\r\n"


def test_trace_subtract_invalid(tsa):
    tsa.trace_subtract("a", 1)
    assert tsa._recorder.count == 0


# --- trace_freeze (the corrected single definition) -----------------------

def test_trace_freeze_valid(tsa):
    tsa.trace_freeze(2)
    assert tsa._recorder.last == "trace2 freeze\r\n"


def test_trace_freeze_invalid(tsa):
    tsa.trace_freeze("two")
    assert tsa._recorder.count == 0


# --- trace_action ---------------------------------------------------------

@pytest.mark.parametrize("action", ["copy", "freeze", "subtract", "view", "value"])
def test_trace_action_valid(tsa, action):
    tsa.trace_action(0, action)
    assert tsa._recorder.last == f"trace0 {action}\r\n"


def test_trace_action_invalid(tsa):
    tsa.trace_action(0, "explode")
    assert tsa._recorder.count == 0


# --- KNOWN BUGS in trace_copy / trace_scale / trace_value -----------------

def test_trace_copy_sends_subtract_known_bug(tsa):
    """
    KNOWN BUG: trace_copy builds a 'subtract' command (copy/paste from
    trace_subtract). It should build a 'copy' command. Pinned to actual output.
    """
    tsa.trace_copy(0, 1)
    assert tsa._recorder.last == "trace0 subtract 1\r\n"


def test_trace_scale_missing_space_known_bug(tsa):
    """KNOWN BUG: 'trace scale' + val with no separator -> 'trace scaleauto'."""
    tsa.trace_scale()
    assert tsa._recorder.last == "trace scaleauto\r\n"


def test_trace_value_missing_space_known_bug(tsa):
    """KNOWN BUG: 'trace' + ID + 'value ' -> 'trace0value ' (no space after ID)."""
    tsa.trace_value(0)
    assert tsa._recorder.last == "trace0value \r\n"
