#! /usr/bin/python3
"""
Serial reader tests: the optional read timeout and the by-length screen capture.

Uses the FakePort seam from conftest; no hardware.
"""

import time

import pytest

PROMPT = b"ch> "


# --- optional read timeout ----------------------------------------------------

def test_timeout_default_is_120_s(parsing_tsa):
    from tsapython import tinySA
    assert tinySA.DEFAULT_SERIAL_TIMEOUT == 120.0
    assert parsing_tsa.get_serial_timeout() == 120.0


def test_timeout_constructor_argument():
    from tsapython import tinySA
    assert tinySA(serial_timeout=5).get_serial_timeout() == 5.0
    assert tinySA(serial_timeout=None).get_serial_timeout() is None


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
    assert parsing_tsa.get_serial_timeout() == 120.0     # unchanged


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


# --- stale output from a timed-out command is discarded ----------------------------

def test_stale_reply_before_echo_is_discarded(parsing_tsa):
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    # a late reply to an earlier 'sweep cw' arrives first, then the real reply
    port._buf = b"sweep cw 10000000\r\nch> " + b"modulation off\r\nch> "
    assert parsing_tsa.command("modulation off") == bytearray(b"")


def test_stale_reply_then_real_data(parsing_tsa):
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    port._buf = b"level -76\r\nch> " + b"deviceid\r\ndeviceid 7\r\nch> "
    assert parsing_tsa.command("deviceid") == bytearray(b"deviceid 7\r")


def test_echo_split_across_reads_still_works(parsing_tsa):
    # the echo can be split across USB packets: 'devi' + 'ceid\r\n...'
    class Chunked:
        def __init__(self, chunks):
            self.chunks = list(chunks)
            self._buf = b""
        @property
        def in_waiting(self):
            if not self._buf and self.chunks:
                self._buf = self.chunks.pop(0)
            return len(self._buf)
        def read(self, n):
            c, self._buf = self._buf[:n], self._buf[n:]
            return c
        def write(self, d):
            return len(d)
        def reset_input_buffer(self):
            pass
        def reset_output_buffer(self):
            pass
    parsing_tsa.ser = Chunked([b"devi", b"ceid\r\ndevi", b"ceid 7\r\nch> "])
    assert parsing_tsa.command("deviceid") == bytearray(b"deviceid 7\r")


def _answers(port, replies):
    # the device answers each WRITE with the next canned reply (one reply per
    # command, like a real port, instead of everything at once)
    replies = list(replies)
    def write(data):
        port.written.append(data)
        port._buf = replies.pop(0) if replies else b""
        return len(data)
    port.write = write


# --- the firmware's own 'Command timeout' (v1.4-222+) ends a reply --------------------

def test_command_timeout_line_ends_the_reply(parsing_tsa):
    # The sweep thread did not pick the command up within 20 s: the shell
    # prints 'Command timeout' and NO prompt. The reader must not wait out the
    # library timeout for a prompt that will never come.
    parsing_tsa.set_serial_timeout(5)
    parsing_tsa.set_error_byte_return(True)
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    # first attempt is dropped by the firmware; the library's single retry gets the prompt
    _answers(port, [b"level -76\r\nCommand timeout\r\n", b"level -76\r\nch> "])
    started = time.monotonic()
    out = parsing_tsa.level(-76)
    assert (time.monotonic() - started) < 1.0
    assert out == bytearray(b"")                    # the retry succeeded
    assert port.written == [b"level -76\r\n", b"level -76\r\n"]


def test_command_timeout_twice_is_an_error(parsing_tsa):
    parsing_tsa.set_serial_timeout(5)
    parsing_tsa.set_error_byte_return(True)
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    _answers(port, [b"level -76\r\nCommand timeout\r\n"] * 2)
    out = parsing_tsa.level(-76)
    assert out == bytearray(b"ERROR")               # retried exactly once, then gave up
    assert len(port.written) == 2


def test_command_timeout_is_logged_as_refused(parsing_tsa, tmp_path):
    import json
    log = tmp_path / "t.jsonl"
    parsing_tsa.set_serial_timeout(0.1)          # the session record's version/info reads hit a silent port
    parsing_tsa.set_log_file(str(log))
    parsing_tsa.set_serial_timeout(5)
    parsing_tsa.set_error_byte_return(True)
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    _answers(port, [b"sweep cw 10000000\r\nCommand timeout\r\n"] * 2)
    assert parsing_tsa.set_sweep_cw(10_000_000) == bytearray(b"ERROR")
    parsing_tsa.close_log_file()
    records = [json.loads(line) for line in log.read_text().splitlines()]
    cmds = [r for r in records if r["type"] == "command" and r["sent"].startswith("sweep cw")]
    assert len(cmds) == 2                           # both attempts are in the log
    assert all(c["status"] == "device-refused" for c in cmds)
    assert all(c["function"] == "config_sweep" for c in cmds)   # the retry is logged under the caller, too
    assert "Command timeout" in cmds[0]["reason"]


def test_timeout_log_keeps_what_arrived(parsing_tsa, tmp_path):
    # a partial reply (echo but no prompt) is kept in the log record's reason,
    # so a hardware log says what the device DID send before going quiet
    import json
    log = tmp_path / "t.jsonl"
    parsing_tsa.set_serial_timeout(0.1)
    parsing_tsa.set_log_file(str(log))
    parsing_tsa.set_serial_timeout(0.2)
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    port._buf = b"level -76\r\n"
    assert parsing_tsa.level(-76) is None
    parsing_tsa.close_log_file()
    records = [json.loads(line) for line in log.read_text().splitlines()]
    cmd = [r for r in records if r["type"] == "command" and r["sent"] == "level -76"][0]
    assert cmd["status"] == "timeout"
    assert "level -76" in cmd["reason"]


# --- settle after the shell-thread setters ------------------------------------------

def test_settle_after_output_and_modulation(parsing_tsa, monkeypatch):
    from tsapython import tinySA
    slept = []
    monkeypatch.setattr("tsapython.core.time.sleep", lambda s: slept.append(s))
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    parsing_tsa.set_output_allowed(True)
    port._buf = b"output off\r\nch> "
    parsing_tsa.output("off")
    port._buf = b"modulation off\r\nch> "
    parsing_tsa.modulation("off")
    port._buf = b"level -76\r\nch> "
    parsing_tsa.level(-76)                          # a between-sweeps command: no settle
    settles = [x for x in slept if x == tinySA.SETTLE_AFTER_IMMEDIATE_SETTER_S]
    assert len(settles) == 2


def test_command_timeout_is_not_retried_for_a_non_idempotent_command(parsing_tsa):
    parsing_tsa.set_serial_timeout(5)
    parsing_tsa.set_error_byte_return(True)
    port = parsing_tsa.ser
    port.reset_input_buffer = lambda: None
    _answers(port, [b"menu 6 2\r\nCommand timeout\r\n", b"menu 6 2\r\nch> "])
    assert parsing_tsa.tinySA_serial("menu 6 2\r\n") == bytearray(b"ERROR")
    assert len(port.written) == 1                   # 'menu' presses a button: never resent
