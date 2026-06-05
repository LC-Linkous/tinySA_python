#! /usr/bin/python3
"""
Command-construction tests for the DisplayUIMixin.

Mocked-serial `tsa` fixture; no hardware. Covers fixed-string screen/touch
commands, the color validator, refresh/text/menu, and touch coordinate bounds
(which use the seeded screenWidth/screenHeight from the fixture).
"""

import pytest


# --- fixed-string screen/touch commands -----------------------------------

@pytest.mark.parametrize("method,expected", [
    ("bulk", "bulk\r\n"),
    ("get_bulk_data", "bulk\r\n"),
    ("capture", "capture\r\n"),
    ("capture_screen", "capture\r\n"),
    ("fill", "fill\r\n"),
    ("get_fill_data", "fill\r\n"),
    ("release", "release\r\n"),
    ("touch_cal", "touchcal\r\n"),
    ("start_touch_cal", "touchcal\r\n"),
    ("touch_test", "touchtest\r\n"),
    ("start_touch_test", "touchtest\r\n"),
])
def test_fixed_string_commands(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


# --- color: None (dump), or ID 0..30 + valid rgb24 ------------------------

def test_color_dump(tsa):
    tsa.color()
    assert tsa._recorder.last == "color\r\n"


def test_color_set_valid(tsa):
    tsa.set_color(5, "0xFF8800")
    assert tsa._recorder.last == "color 5 0xFF8800\r\n"


@pytest.mark.parametrize("ID,rgb", [
    (5, "FF8800"),       # bad rgb (no 0x)
    (5, "0xFF88"),       # bad rgb (too short)
    (31, "0xFF8800"),    # ID out of range (arange(0,31) excludes 31)
    (-1, "0xFF8800"),    # ID out of range
])
def test_color_set_invalid(tsa, ID, rgb):
    tsa.color(ID, rgb)
    assert tsa._recorder.count == 0


# --- refresh: on/off ------------------------------------------------------

@pytest.mark.parametrize("method,expected", [
    ("refresh_on", "refresh on\r\n"),
    ("refresh_off", "refresh off\r\n"),
])
def test_refresh_aliases(tsa, method, expected):
    getattr(tsa, method)()
    assert tsa._recorder.last == expected


def test_refresh_invalid(tsa):
    tsa.refresh("maybe")
    assert tsa._recorder.count == 0


# --- menu: passthrough ----------------------------------------------------

def test_menu(tsa):
    tsa.menu(3)
    assert tsa._recorder.last == "menu 3\r\n"


# --- text: non-empty required ---------------------------------------------

def test_text_valid(tsa):
    tsa.text("hello")
    assert tsa._recorder.last == "text hello\r\n"


def test_text_empty_invalid(tsa):
    tsa.text("")
    assert tsa._recorder.count == 0


# --- touch: coordinate bounds (screenWidth=480, screenHeight=320) ---------

def test_touch_valid(tsa):
    tsa.touch(100, 100)
    assert tsa._recorder.last == "touch 100 100\r\n"


def test_touch_corner_origin(tsa):
    tsa.touch(0, 0)
    assert tsa._recorder.last == "touch 0 0\r\n"


@pytest.mark.parametrize("x,y", [
    (-1, 100),     # x too low
    (481, 100),    # x past screenWidth
    (100, -1),     # y too low
    (100, 321),    # y past screenHeight
])
def test_touch_out_of_bounds(tsa, x, y):
    tsa.touch(x, y)
    assert tsa._recorder.count == 0


def test_preform_touch_alias(tsa):
    tsa.preform_touch(10, 20)
    assert tsa._recorder.last == "touch 10 20\r\n"
