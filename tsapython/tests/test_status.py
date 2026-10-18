#! /usr/bin/python3
"""
get_last_status(): how the last command ended, independent of the return value.

In the default error mode an accepted setter and a rejected one both return
b'', so callers (and the library's own multi-step helpers) need this to tell
them apart. No hardware.
"""

from tsapython import tinySA

from tests.test_v4_profiles import ScriptedPort, ZS405_143

PROMPT = b"ch> "

# the generator helpers pause and resume around their settings
GEN = dict(ZS405_143, **{"pause": b"", "resume": b"", "mode low output": b""})


def connect_default_mode(replies):
    # like test_v4_profiles.connect(), but WITHOUT set_error_byte_return(True)
    d = tinySA()
    port = ScriptedPort(dict(replies))
    d.ser = port
    d.identify()
    d.set_output_allowed(True)
    return d, port


def test_status_ok_after_accepted_setter():
    d, _ = connect_default_mode(ZS405_143)
    assert d.rbw(30) == bytearray(b"")
    assert d.get_last_status() == "ok"


def test_status_blocked_when_the_library_refuses():
    d, port = connect_default_mode(ZS405_143)
    sent_before = list(port.sent)
    assert d.level(50) == bytearray(b"")             # same return value as an accepted setter...
    assert d.get_last_status() == "blocked"          # ...but the status tells
    assert port.sent == sent_before                  # and nothing was sent


def test_status_usage_when_the_device_rejects():
    d, _ = connect_default_mode(dict(ZS405_143, **{"rbw 30": b"usage: rbw 0.2..850|auto\r\n"}))
    assert d.rbw(30) == bytearray(b"")               # the device, not the library, said no
    assert d.get_last_status() == "usage"


def test_status_unknown_command():
    d, _ = connect_default_mode(ZS405_143)
    assert d.command("nosuchcommand") is not None
    assert d.get_last_status() == "unknown-command"


def test_status_timeout(parsing_tsa):
    parsing_tsa.set_serial_timeout(0.1)
    assert parsing_tsa.command("version") is None
    assert parsing_tsa.get_last_status() == "timeout"


# --- the generator helpers use the status, not the return value ---------------------

def test_setup_generator_default_mode_detects_a_blocked_step():
    d, port = connect_default_mode(GEN)
    assert d.setup_generator(300e6, -30, high=True) is False    # 'mode high output' is Ultra-blocked
    assert "mode high output" not in port.sent
    assert "level -30" not in port.sent                         # stopped at the refused step
    assert port.sent[-1] == "resume"                            # and the sweep was resumed
    assert d.get_last_status() == "blocked"


def test_setup_generator_default_mode_detects_a_device_rejection():
    replies = dict(GEN)
    replies["mode low output"] = b"usage: mode [low] input|output\r\n"
    d, port = connect_default_mode(replies)
    assert d.setup_generator(10e6, -30) is False
    assert d.get_last_status() == "usage"
    assert port.sent[-1] == "resume"


def test_set_generator_default_mode_detects_an_out_of_range_level():
    d, port = connect_default_mode(GEN)
    assert d.set_generator(level_dbm=50) is False
    assert port.sent[-2:] == ["pause", "resume"]
    assert d.get_last_status() == "blocked"


def test_set_generator_default_mode_success():
    replies = dict(GEN, **{"level -40": b"", "sweep cw 20000000": b""})
    d, port = connect_default_mode(replies)
    assert d.set_generator(level_dbm=-40, freq_hz=20e6) is True
    assert d.get_last_status() == "ok"
