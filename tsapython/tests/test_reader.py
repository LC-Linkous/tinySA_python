#! /usr/bin/python3
"""
Serial reader tests: the optional read timeout and the by-length screen capture.

Uses the FakePort seam from conftest; no hardware.
"""

import time

import pytest

PROMPT = b"ch> "


# --- optional read timeout ----------------------------------------------------

def test_timeout_default_is_none(parsing_tsa):
    assert parsing_tsa.get_serial_timeout() is None


def test_timeout_returns_none_when_device_is_silent(parsing_tsa):
    parsing_tsa.set_serial_timeout(0.2)
    started = time.monotonic()
    out = parsing_tsa.command("version")       # FakePort has nothing to say
    assert out is None
    assert 0.15 < (time.monotonic() - started) < 2.0


def test_timeout_does_not_affect_a_normal_reply(parsing_tsa):
    parsing_tsa.set_serial_timeout(0.5)
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None      # keep the canned reply in place
    port._buf = b"deviceid\r\ndeviceid 0\r\n" + PROMPT
    assert parsing_tsa.command("deviceid") == bytearray(b"deviceid 0\r")


@pytest.mark.parametrize("bad", [0, -1])
def test_timeout_rejects_non_positive(parsing_tsa, bad):
    parsing_tsa.set_serial_timeout(bad)
    assert parsing_tsa.get_serial_timeout() is None


def test_timeout_can_be_cleared(parsing_tsa):
    parsing_tsa.set_serial_timeout(5)
    parsing_tsa.set_serial_timeout(None)
    assert parsing_tsa.get_serial_timeout() is None


# --- capture: read by length, not to the first '>' -----------------------------

def _load(parsing_tsa, pixels):
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    port._buf = b"capture\r\n" + pixels + PROMPT


def test_capture_returns_every_pixel_byte(parsing_tsa):
    parsing_tsa.screenWidth, parsing_tsa.screenHeight = 8, 4
    pixels = bytes(range(64))                   # includes 0x3e ('>') at offset 62
    assert b">" in pixels
    _load(parsing_tsa, pixels)
    assert parsing_tsa.capture() == bytearray(pixels)


def test_capture_with_prompt_like_bytes_inside_the_image(parsing_tsa):
    parsing_tsa.screenWidth, parsing_tsa.screenHeight = 8, 4
    pixels = b"ch> " + bytes(56) + b"ch> "      # prompt text at both ends of the data
    _load(parsing_tsa, pixels)
    assert parsing_tsa.capture() == bytearray(pixels)


def test_capture_other_screen_size_falls_back_to_idle(parsing_tsa):
    # library still set for a 480x320 Ultra, device sends a smaller frame
    pixels = bytes([0x3e, 0x00] * 100)
    _load(parsing_tsa, pixels)
    assert parsing_tsa.capture() == bytearray(pixels)


def test_capture_times_out_on_a_silent_device(parsing_tsa):
    parsing_tsa.set_serial_timeout(0.2)
    assert parsing_tsa.capture() is None


def test_capture_through_command_uses_the_same_reader(parsing_tsa):
    parsing_tsa.screenWidth, parsing_tsa.screenHeight = 8, 4
    pixels = bytes([0x3e] * 64)
    _load(parsing_tsa, pixels)
    assert parsing_tsa.command("capture") == bytearray(pixels)
