#! /usr/bin/python3
"""
Command-construction tests for the SystemInfoMixin.

Verifies command strings for valid input and the error path for invalid input,
using the mocked-serial `tsa` fixture. No hardware required.

Several methods here are fixed-string getters (info, version, vbat, ...). For
those we assert the exact command string. Methods with validation (dac, rbw,
self_test) get valid + invalid cases.

"""

import pytest


# --- fixed-string getters: no args, one exact command ---------------------

@pytest.mark.parametrize("method,expected", [
    ("info", "info\r\n"),
    ("get_info", "info\r\n"),
    ("nf", "nf\r\n"),
    ("get_nf", "nf\r\n"),
    ("status", "status\r\n"),
    ("temp", "k\r\n"),            # single-letter device command
    ("get_temp", "k\r\n"),
    ("threads", "threads\r\n"),
    ("usart_cfg", "usart_cfg\r\n"),
    ("get_usart_cfg", "usart_cfg\r\n"),
    ("vbat", "vbat\r\n"),
    ("get_vbat", "vbat\r\n"),
    ("version", "version\r\n"),
    ("get_version", "version\r\n"),
    ("tinySA_help", "help\r\n"),
])
def test_fixed_string_getters(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_get_status_returns_status(tsa):
    # FIXED: get_status now calls status().
    tsa.get_status()
    assert tsa._recorder.last == "status\r\n"


# --- command(): passthrough -----------------------------------------------

def test_command_passthrough(tsa):
    tsa.command("custom_thing 5")
    assert tsa._recorder.last == "custom_thing 5\r\n"


# --- dac: None (get) or int/float 0..4095 ---------------------------------

def test_dac_get(tsa):
    tsa.dac()
    assert tsa._recorder.last == "dac\r\n"


@pytest.mark.parametrize("val,expected", [
    (0, "dac 0\r\n"),
    (4095, "dac 4095\r\n"),
    (2000, "dac 2000\r\n"),
])
def test_dac_set_valid(tsa, val, expected):
    tsa.set_dac(val)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("val", [-1, 4096, "high"])
def test_dac_set_invalid(tsa, val):
    tsa.dac(val)
    assert tsa._recorder.count == 0


# --- rbw: "auto" or int ---------------------------------------------------

@pytest.mark.parametrize("val,expected", [
    ("auto", "rbw auto\r\n"),
    (3, "rbw 3\r\n"),
    (600, "rbw 600\r\n"),
])
def test_rbw_valid(tsa, val, expected):
    tsa.rbw(val)
    assert tsa._recorder.last == expected


def test_rbw_auto_alias(tsa):
    tsa.set_rbw_auto()
    assert tsa._recorder.last == "rbw auto\r\n"


@pytest.mark.parametrize("val", [3.5, "fast", None])
def test_rbw_invalid(tsa, val):
    tsa.rbw(val)
    assert tsa._recorder.count == 0


# --- self_test: any int accepted ------------------------------------------

@pytest.mark.parametrize("val,expected", [
    (0, "selftest 0\r\n"),
    (9, "selftest 9\r\n"),
])
def test_self_test_valid(tsa, val, expected):
    tsa.self_test(val)
    assert tsa._recorder.last == expected


def test_self_test_invalid(tsa):
    tsa.self_test("all")
    assert tsa._recorder.count == 0


# --- help() routing -------------------------------------------------------

def test_help_routes_to_device(tsa):
    # val != 1 -> tinySA_help() -> sends 'help\r\n'
    tsa.help(0)
    assert tsa._recorder.last == "help\r\n"


def test_help_library_no_serial(tsa):
    # val == 1 -> library_help() -> returns b'' without touching serial
    out = tsa.help(1)
    assert tsa._recorder.count == 0
    assert out == b""