#! /usr/bin/python3
"""
Command-construction tests for the PresetsConfigMixin.

Mocked-serial `tsa` fixture; no hardware. NOTE: methods like reset/clear_config
would be destructive on a real device, but here tinySA_serial is replaced by a
recorder, so these only assert the command string is built correctly -- nothing
is sent to hardware.
"""

import pytest


# --- preset slots: load / recall / save (0..4) ----------------------------

@pytest.mark.parametrize("method,val,expected", [
    ("load", 0, "load 0\r\n"),
    ("load", 4, "load 4\r\n"),
    ("recall", 2, "recall 2\r\n"),
    ("save", 1, "save 1\r\n"),
    ("save", 0, "save 0\r\n"),
])
def test_preset_slots_valid(tsa, method, val, expected):
    getattr(tsa, method)(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("method,val", [
    ("load", 5), ("load", -1),
    ("recall", 9),
    ("save", 5), ("save", "x"),
])
def test_preset_slots_invalid(tsa, method, val):
    getattr(tsa, method)(val)
    assert tsa._recorder.count == 0


# --- device_id: None (get) or int -----------------------------------------

def test_device_id_get(tsa):
    tsa.get_device_id()
    assert tsa._recorder.last == "deviceid\r\n"


def test_device_id_set_valid(tsa):
    tsa.set_device_id(12)
    assert tsa._recorder.last == "deviceid 12\r\n"


def test_device_id_set_invalid(tsa):
    tsa.device_id("twelve")
    assert tsa._recorder.count == 0


# --- fixed-string config commands -----------------------------------------

@pytest.mark.parametrize("method,expected", [
    ("clear_config", "clearconfig 1234\r\n"),
    ("save_config", "saveconfig\r\n"),
    ("reset", "reset\r\n"),
    ("reset_device", "reset\r\n"),
    ("sd_list", "sd_list\r\n"),
])
def test_fixed_string_commands(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_clear_and_reset_sends_both(tsa):
    tsa.clear_and_reset()
    # clear_config then reset -> two serial calls, reset last
    assert tsa._recorder.count == 2
    assert tsa._recorder.calls[0] == "clearconfig 1234\r\n"
    assert tsa._recorder.calls[1] == "reset\r\n"


# --- sd_delete / sd_read: passthrough filenames ---------------------------

def test_sd_delete(tsa):
    tsa.sd_delete("-0.bmp")
    assert tsa._recorder.last == "sd_delete -0.bmp\r\n"


def test_sd_read(tsa):
    tsa.sd_read("-0.bmp")
    assert tsa._recorder.last == "sd_read -0.bmp\r\n"


# --- remark: passthrough --------------------------------------------------

def test_remark(tsa):
    tsa.remark("test note")
    assert tsa._recorder.last == "remark test note\r\n"


# --- repeat: int 1..1000 --------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    (1, "repeat 1\r\n"),
    (1000, "repeat 1000\r\n"),
])
def test_repeat_valid(tsa, val, expected):
    tsa.repeat(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [0, 1001])
def test_repeat_invalid(tsa, val):
    tsa.repeat(val)
    assert tsa._recorder.count == 0


# --- restart: 0 (cancel) or positive seconds ------------------------------

def test_restart_cancel(tsa):
    tsa.cancel_restart()
    assert tsa._recorder.last == "restart 0\r\n"


def test_restart_seconds(tsa):
    tsa.restart_device(5)
    assert tsa._recorder.last == "restart 5\r\n"


# --- wait: None (indefinite) or positive seconds --------------------------

def test_wait_indefinite(tsa):
    tsa.wait(None)
    assert tsa._recorder.last == "wait\r\n"


def test_wait_seconds(tsa):
    tsa.wait(3)
    assert tsa._recorder.last == "wait 3\r\n"


def test_wait_zero_invalid(tsa):
    # default val=0 is neither None nor >0 -> error path
    tsa.wait(0)
    assert tsa._recorder.count == 0


# --- abort: stateful (must enable before action) --------------------------

def test_abort_enable(tsa):
    tsa.enable_abort()
    assert tsa._recorder.last == "abort on\r\n"
    assert tsa.abortEnabled is True


def test_abort_disable(tsa):
    tsa.disable_abort()
    assert tsa._recorder.last == "abort off\r\n"
    assert tsa.abortEnabled is False


def test_abort_action_requires_enable_first(tsa):
    # With abort disabled (default), the bare action should NOT send.
    tsa.abortEnabled = False
    tsa.abort_action()
    assert tsa._recorder.count == 0


def test_abort_action_after_enable(tsa):
    tsa.enable_abort()          # sends 'abort on'
    tsa.abort_action()          # now allowed -> sends bare 'abort'
    assert tsa._recorder.calls[-1] == "abort\r\n"


def test_clear_and_reset_sends_both_and_survives(tsa):
    # clear_and_reset sends clearconfig then reset. On REAL hardware reset()
    # disconnects the serial and may raise/hang, so clear_and_reset catches
    # exceptions and must not propagate them. (The mock can't simulate the
    # disconnect; this only verifies both commands are sent and no exception
    # escapes. See diagnose_reset.py for the real-hardware behavior check.)
    tsa.clear_and_reset()                    # must not raise
    assert tsa._recorder.calls[0] == "clearconfig 1234\r\n"
    assert tsa._recorder.calls[1] == "reset\r\n"
    # return value is intentionally not asserted: it is None or msgbytes
    # depending on whether the port dropped before a response arrived.