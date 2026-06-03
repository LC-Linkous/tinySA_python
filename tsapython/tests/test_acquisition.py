#! /usr/bin/python3
"""
Command-construction tests for the AcquisitionMixin.

Mocked-serial `tsa` fixture; no hardware. Covers data dump, frequencies, hop,
scan/scanraw (with pts bounded by the seeded maxPoints=450), sweep config and
its aliases, run_sweep, sweeptime, and triggers.
"""

import pytest


# --- data: 0..2 -----------------------------------------------------------

@pytest.mark.parametrize("method,expected", [
    ("get_temporary_data", "data 0\r\n"),
    ("get_stored_trace_data", "data 1\r\n"),
    ("dump_measurement_data", "data 2\r\n"),
])
def test_data_aliases(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_data_invalid(tsa):
    tsa.data(3)
    assert tsa._recorder.count == 0


# --- frequencies ----------------------------------------------------------

def test_frequencies(tsa):
    tsa.frequencies()
    assert tsa._recorder.last == "frequencies\r\n"


def test_get_last_freqs_alias(tsa):
    tsa.get_last_freqs()
    assert tsa._recorder.last == "frequencies\r\n"


# --- pause / resume -------------------------------------------------------

@pytest.mark.parametrize("method,expected", [
    ("pause", "pause\r\n"),
    ("resume", "resume\r\n"),
])
def test_pause_resume(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


# --- hop: start/stop/inc numeric, optional outmask 1|2 --------------------

def test_hop_with_outmask(tsa):
    tsa.hop(100e6, 500e6, 101, 1)
    assert tsa._recorder.last == "hop 100000000.0 500000000.0 101 1\r\n"


def test_hop_without_outmask(tsa):
    tsa.hop(100e6, 500e6, 101)
    assert tsa._recorder.last == "hop 100000000.0 500000000.0 101\r\n"


def test_get_sample_pts_alias(tsa):
    tsa.get_sample_pts(100e6, 500e6, 50)
    assert tsa._recorder.last == "hop 100000000.0 500000000.0 50 1\r\n"


def test_hop_non_numeric_returns_none(tsa):
    out = tsa.hop("a", 500e6, 101)
    assert tsa._recorder.count == 0
    assert out is None


# --- scan: 0<=start<stop, pts<=maxPoints ----------------------------------

def test_scan_no_outmask(tsa):
    tsa.scan(0, 2_000_000, 5)
    assert tsa._recorder.last == "scan 0 2000000 5\r\n"


def test_scan_with_outmask(tsa):
    tsa.scan(0, 2_000_000, 5, 2)
    assert tsa._recorder.last == "scan 0 2000000 5 2\r\n"


@pytest.mark.parametrize("start,stop,pts", [
    (2_000_000, 1_000_000, 5),   # start >= stop
    (-1, 1_000_000, 5),          # negative start
    (0, 1_000_000, 9999),        # pts > maxPoints (450)
])
def test_scan_invalid(tsa, start, stop, pts):
    tsa.scan(start, stop, pts)
    assert tsa._recorder.count == 0


# --- scan_raw: same bounds + unbuf in {1,2,3} -----------------------------

def test_scan_raw_valid(tsa):
    tsa.scan_raw(150e6, 200e6, 5, 1)
    assert tsa._recorder.last == "scanraw 150000000.0 200000000.0 5 1\r\n"


def test_scan_raw_bad_unbuf(tsa):
    tsa.scan_raw(150e6, 200e6, 5, 9)
    assert tsa._recorder.count == 0


def test_scan_raw_bad_range(tsa):
    tsa.scan_raw(200e6, 100e6, 5, 1)
    assert tsa._recorder.count == 0


# --- config_sweep + aliases -----------------------------------------------

def test_config_sweep_dump(tsa):
    tsa.get_sweep_params()
    assert tsa._recorder.last == "sweep\r\n"


@pytest.mark.parametrize("method,arg,val,expected", [
    ("set_sweep_start", None, 100e6, "sweep start 100000000.0\r\n"),
    ("set_sweep_stop", None, 200e6, "sweep stop 200000000.0\r\n"),
    ("set_sweep_center", None, 150e6, "sweep center 150000000.0\r\n"),
    ("set_sweep_span", None, 50e6, "sweep span 50000000.0\r\n"),
    ("set_sweep_cw", None, 150e6, "sweep cw 150000000.0\r\n"),
])
def test_config_sweep_aliases(tsa, method, arg, val, expected):
    getattr(tsa, method)(val)
    assert tsa._recorder.last == expected


def test_config_sweep_bad_arg(tsa):
    tsa.config_sweep("bogus", 100)
    assert tsa._recorder.count == 0


def test_config_sweep_arg_without_value(tsa):
    tsa.config_sweep("start", None)
    assert tsa._recorder.count == 0


# --- run_sweep ------------------------------------------------------------

def test_run_sweep_valid(tsa):
    tsa.run_sweep(100e6, 200e6, 250)
    # NOTE: command string has '2501' -- pts and the trailing '1' are concatenated
    # with no space in the source. Pinning ACTUAL behavior; see KNOWN BUG note.
    assert tsa._recorder.last == "sweep 100000000.0 200000000.0 2501\r\n"


@pytest.mark.parametrize("start,stop", [
    (None, 200e6),
    (200e6, 100e6),    # start >= stop
])
def test_run_sweep_invalid(tsa, start, stop):
    tsa.run_sweep(start, stop)
    assert tsa._recorder.count == 0


# --- sweep_time -----------------------------------------------------------

def test_sweep_time(tsa):
    tsa.sweep_time("120m")
    assert tsa._recorder.last == "sweeptime 120m\r\n"


# --- triggers -------------------------------------------------------------

@pytest.mark.parametrize("method,expected", [
    ("trigger_auto", "trigger auto\r\n"),
    ("trigger_normal", "trigger normal\r\n"),
    ("trigger_single", "trigger single\r\n"),
])
def test_trigger_aliases(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_trigger_level(tsa):
    tsa.trigger_level(-30)
    assert tsa._recorder.last == "trigger -30\r\n"


def test_trigger_invalid(tsa):
    tsa.trigger("sometimes")
    assert tsa._recorder.count == 0
