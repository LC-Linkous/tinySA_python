#! /usr/bin/python3
"""
Ultra-family-only commands are refused before anything is sent on a Basic, and
the sd_read reader returns a text reply instead of reading it as a file length.
No hardware.
"""

import time

import pytest


@pytest.mark.parametrize("call", [
    lambda t: t.direct("on"),
    lambda t: t.ultra("on"),
    lambda t: t.restart(5),
    lambda t: t.sd_delete("x.bin"),
    lambda t: t.sd_read("x.bin"),
    lambda t: t.freq_corr(),
])
def test_ultra_only_command_is_blocked_on_basic_before_sending(tsa, call):
    tsa.select_existing_device("BASIC")
    tsa.set_error_byte_return(True)
    assert call(tsa) == bytearray(b"ERROR")
    assert tsa._recorder.calls == []
    assert tsa.get_last_status() == "blocked"


@pytest.mark.parametrize("call, sent", [
    (lambda t: t.direct("on"), "direct on\r\n"),
    (lambda t: t.ultra("on"), "ultra on\r\n"),
    (lambda t: t.restart(5), "restart 5\r\n"),
    (lambda t: t.sd_delete("x.bin"), "sd_delete x.bin\r\n"),
    (lambda t: t.freq_corr(), "freq_corr\r\n"),
])
def test_ultra_only_command_is_sent_on_ultra(tsa, call, sent):
    tsa.select_existing_device("ZS405")
    call(tsa)
    assert tsa._recorder.calls == [sent]


def test_sd_read_text_reply_is_not_read_as_a_length(parsing_tsa):
    # an older firmware without the command: 'sd_read?' and the prompt, no size prefix
    parsing_tsa.select_existing_device("ZS405")
    parsing_tsa.set_error_byte_return(True)
    parsing_tsa.set_serial_timeout(5)
    port = parsing_tsa.ser
    port.answer(b"sd_read x.bin\r\nsd_read?\r\nch> ")
    started = time.monotonic()
    out = parsing_tsa.sd_read("x.bin")
    assert (time.monotonic() - started) < 4.0    # did not wait out the 5 s timeout
    assert out == bytearray(b"ERROR")
    assert parsing_tsa.get_last_status() == "unknown-command"


def test_sd_read_err_reply_is_text(parsing_tsa):
    parsing_tsa.select_existing_device("ZS405")
    port = parsing_tsa.ser
    port.answer(b"sd_read x.bin\r\nerr: (4) no file\r\nch> ")
    assert parsing_tsa.sd_read("x.bin") == bytearray(b"err: (4) no file")


def test_sd_read_file_bytes_still_work(parsing_tsa):
    parsing_tsa.select_existing_device("ZS405")
    port = parsing_tsa.ser
    body = bytes(range(256)) * 2            # 512 bytes incl. 'c','h','>',' ' values
    port.answer(b"sd_read x.bin\r\n" + (512).to_bytes(4, "little") + body + b"ch> ")
    assert parsing_tsa.sd_read("x.bin") == bytearray(body)
