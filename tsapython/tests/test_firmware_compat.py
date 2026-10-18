#! /usr/bin/python3
"""
Command-construction tests for arguments the tinySA firmware accepts but the
library used to block, or built incorrectly.

Each case was read from the firmware source (github.com/erikkaashoek/tinySA,
v1.4-244). Mocked-serial `tsa` fixture; no hardware.
"""

import pytest


# --- hop: outmask 3 (the firmware default) used to raise UnboundLocalError ---

def test_hop_outmask_both(tsa):
    tsa.hop(100e6, 500e6, 12, 3)
    assert tsa._recorder.last == "hop 100000000.0 500000000.0 12 3\r\n"


@pytest.mark.parametrize("outmask", [0, 4, "2", 1.5, True])
def test_hop_bad_outmask_returns_error_value(tsa, outmask):
    tsa.set_error_byte_return(True)
    out = tsa.hop(100e6, 500e6, 12, outmask)
    assert tsa._recorder.count == 0
    assert out == bytearray(b"ERROR")


# --- wait(): the bare command is now the default ----------------------------

def test_wait_default_sends_bare_command(tsa):
    tsa.wait()
    assert tsa._recorder.last == "wait\r\n"


# --- scan / scan_raw ---------------------------------------------------------

def test_scan_zero_span(tsa):
    tsa.scan(100_000_000, 100_000_000, 20, 3)
    assert tsa._recorder.last == "scan 100000000 100000000 20 3\r\n"


def test_scan_raw_buffered(tsa):
    tsa.scan_raw(100_000_000, 200_000_000, 20, 0)
    assert tsa._recorder.last == "scanraw 100000000 200000000 20 0\r\n"


def test_scan_raw_zero_span(tsa):
    tsa.scan_raw(100_000_000, 100_000_000, 20, 1)
    assert tsa._recorder.last == "scanraw 100000000 100000000 20 1\r\n"


# --- trigger level is a float in the firmware --------------------------------

def test_trigger_level_decimal(tsa):
    tsa.trigger_level(-52.5)
    assert tsa._recorder.last == "trigger -52.5\r\n"


def test_trigger_level_rejects_bool(tsa):
    tsa.trigger_level(True)
    assert tsa._recorder.count == 0


# --- spur auto (Ultra family) ------------------------------------------------

def test_spur_auto(tsa):
    tsa.spur_auto()
    assert tsa._recorder.last == "spur auto\r\n"


# --- if: each board has its own range ----------------------------------------

@pytest.mark.parametrize("board,val", [
    ("BASIC", 434_000_000), ("ZS405", 977_000_000), ("ZS406", 1_070_000_000), ("ZS407", 1_070_000_000),
])
def test_set_IF_ranges_per_board(tsa, board, val):
    tsa.select_existing_device(board)
    tsa.set_IF(val)
    assert tsa._recorder.last == f"if {val}\r\n"


@pytest.mark.parametrize("board,val", [
    ("ZS405", 434_000_000), ("ZS405", 1_070_000_000), ("ZS406", 977_000_000), ("BASIC", 977_000_000),
    ("ZS405", 980_000_000), ("ZS405", "977M"),
])
def test_set_IF_wrong_board_rejected(tsa, board, val):
    tsa.select_existing_device(board)
    tsa.set_IF(val)
    assert tsa._recorder.count == 0


# --- leveloffset names added in firmware v1.4-193 ----------------------------

@pytest.mark.parametrize("name", ["shift4", "direct_output", "low_output"])
def test_level_offset_newer_names(tsa, name):
    tsa.level_offset(name, 1.5)
    assert tsa._recorder.last == f"leveloffset {name} 1.5\r\n"


def test_level_offset_high_is_basic_only(tsa):
    tsa.level_offset("high", 1.5)
    assert tsa._recorder.count == 0
    tsa.select_existing_device("BASIC")
    tsa.level_offset("high", 1.5)
    assert tsa._recorder.last == "leveloffset high 1.5\r\n"


# --- package version ----------------------------------------------------------

def test_dunder_version_is_not_stale():
    import tsapython
    assert tsapython.__version__ != "2.0.0"
