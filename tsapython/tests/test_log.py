#! /usr/bin/python3
"""
Log file tests (set_log_file / close_log_file).

Format: JSON Lines, one object per line. See the README section "Logging".
"""

import json

import pytest

PROMPT = b"ch> "


class ScriptedPort:
    """A fake serial port that answers each written command from a table."""

    port = "FAKE0"

    def __init__(self, replies):
        self.replies = replies
        self._buf = b""

    @property
    def in_waiting(self):
        return len(self._buf)

    def read(self, n):
        chunk, self._buf = self._buf[:n], self._buf[n:]
        return chunk

    def write(self, data):
        command = data.decode().strip()
        body = self.replies.get(command)
        if body is None:
            return len(data)                     # stay silent
        self._buf = data + body + PROMPT
        return len(data)

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass

    def close(self):
        pass


REPLIES = {
    "version": b"tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1 \r\n",
    "info": b"tinySA ULTRA\r\n2019-2024 Copyright @Erik Kaashoek\r\n",
    "rbw 30": b"",
    "calc quasi": b"",
    "mode high input": b"usage: mode [low] input|output\r\n",
    "waitscan 1": b"waitscan?\r\n",
    "frequencies": b"".join(b"%d\r\n" % (1000000 + i) for i in range(100)),
    "scanraw 100 200 4 1": None,                 # handled below
}


@pytest.fixture
def logged(tmp_path):
    from tsapython import tinySA
    dev = tinySA()
    dev.ser = ScriptedPort(dict(REPLIES))
    path = tmp_path / "session.jsonl"
    assert dev.set_log_file(str(path)) is True
    return dev, path


def records(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def test_off_by_default():
    from tsapython import tinySA
    assert tinySA().get_log_file() is None


def test_session_record_identifies_the_device(logged):
    dev, path = logged
    first = records(path)[0]
    assert first["type"] == "session"
    assert first["log_format"] == 1
    assert first["port"] == "FAKE0"
    assert first["family"] == "ultra"
    assert first["board"] == "ZS405"
    assert first["build"] == [1, 4, 143]
    assert first["info_first_line"] == "tinySA ULTRA"
    assert first["t"].endswith("Z") and "T" in first["t"]


def test_identification_reads_are_not_logged_as_commands(logged):
    dev, path = logged
    assert [r["type"] for r in records(path)] == ["session"]


def test_accepted_command(logged):
    dev, path = logged
    dev.rbw(30)
    rec = records(path)[-1]
    assert rec["type"] == "command"
    assert rec["seq"] == 1
    assert rec["function"] == "rbw"
    assert rec["sent"] == "rbw 30"
    assert rec["status"] == "ok"
    assert rec["reply"] == "" and rec["reply_len"] == 0
    assert rec["truncated"] is False
    assert isinstance(rec["elapsed_ms"], int)


def test_rejected_argument_is_logged_as_usage(logged):
    dev, path = logged
    dev.select_existing_device("BASIC")          # so the word check lets 'high' through to the device
    reply = dev.mode("high", "input")
    assert reply == bytearray(b"")               # 4.0.0: device rejection -> error value (flag off)
    rec = [r for r in records(path) if r["type"] == "command"][-1]
    assert rec["status"] == "usage"
    assert rec["reason"] == "device rejected the argument"
    assert "mode [low] input|output" in rec["reply"]


def test_unknown_command(logged):
    dev, path = logged
    dev.command("waitscan 1")
    rec = records(path)[-1]
    assert rec["status"] == "unknown-command"
    assert rec["function"] == "command"


def test_library_check_is_logged_as_blocked_with_the_reason(logged):
    dev, path = logged
    dev.attenuate(40)
    rec = records(path)[-1]
    assert rec["status"] == "blocked"
    assert rec["function"] == "attenuate"
    assert rec["sent"] == ""
    assert "attenuate() takes vals" in rec["reason"]


def test_reason_does_not_leak_into_the_next_record(logged):
    dev, path = logged
    dev.attenuate(40)
    dev.rbw(30)
    assert records(path)[-1]["reason"] == ""


def test_timeout_is_logged(logged):
    dev, path = logged
    dev.set_serial_timeout(0.2)
    assert dev.command("silence") is None
    rec = records(path)[-1]
    assert rec["status"] == "timeout"


def test_commands_level_truncates_long_text(logged):
    dev, path = logged
    dev.frequencies()
    rec = records(path)[-1]
    assert rec["truncated"] is True
    assert len(rec["reply"]) == 256
    assert rec["reply_len"] > 256


def test_data_level_keeps_everything(tmp_path):
    from tsapython import tinySA
    dev = tinySA()
    dev.ser = ScriptedPort(dict(REPLIES))
    path = tmp_path / "full.jsonl"
    dev.set_log_file(str(path), level="data")
    dev.frequencies()
    rec = records(path)[-1]
    assert rec["truncated"] is False
    assert len(rec["reply"]) == rec["reply_len"]


def test_binary_reply_by_length_or_base64(tmp_path):
    import base64
    from tsapython import tinySA
    frame = b"{" + b"x\x10\x20" * 4 + b"}"
    for level in ("commands", "data"):
        dev = tinySA()
        port = ScriptedPort(dict(REPLIES))
        port.replies["scanraw 100 200 4 1"] = frame
        dev.ser = port
        path = tmp_path / (level + ".jsonl")
        dev.set_log_file(str(path), level=level)
        dev.scan_raw(100, 200, 4, 1)
        rec = records(path)[-1]
        assert rec["function"] == "scan_raw"
        assert rec["reply"] == ""
        assert rec["reply_len"] == 13            # '{' + 4 * 3 bytes
        if level == "commands":
            assert rec["truncated"] is True and "reply_b64" not in rec
        else:
            assert base64.b64decode(rec["reply_b64"]) == frame[:-1]


def test_close_writes_an_event_and_stops_logging(logged):
    dev, path = logged
    dev.close_log_file()
    assert dev.get_log_file() is None
    count = len(records(path))
    assert records(path)[-1] == {**records(path)[-1], "type": "event", "event": "log-closed"}
    dev.rbw(30)
    assert len(records(path)) == count


def test_bad_level_is_refused(tmp_path):
    from tsapython import tinySA
    dev = tinySA()
    assert dev.set_log_file(str(tmp_path / "x.jsonl"), level="everything") is False
    assert dev.get_log_file() is None


def test_unwritable_path_is_refused(tmp_path):
    from tsapython import tinySA
    dev = tinySA()
    assert dev.set_log_file(str(tmp_path / "no_such_dir" / "x.jsonl")) is False


def test_logging_without_a_port_writes_an_empty_session(tmp_path):
    from tsapython import tinySA
    dev = tinySA()
    path = tmp_path / "noport.jsonl"
    assert dev.set_log_file(str(path)) is True
    first = records(path)[0]
    assert first["type"] == "session" and first["family"] == "unknown"
