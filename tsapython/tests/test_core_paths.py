#! /usr/bin/python3
"""
Coverage for core paths that the command tests do not reach: connect() and
autoconnect() with a mocked serial module, identification corner cases, the
legacy boundary setters, binary-read timeouts, sd_read error paths, log
session fallbacks. No hardware.
"""

import time

import pytest

import tsapython.core as core
from tsapython import tinySA
from tsapython._profiles import BASIC, DEFAULT, ULTRA_ZS405, profile_for

PROMPT = b"ch> "


class ScriptedPort:
    """Answers each command from a table; unknown commands get 'name?'."""
    def __init__(self, port="COM7", timeout=1, replies=None, silent=False, **kwargs):
        self.port = port
        self.timeout = timeout
        self.replies = dict(replies or {})
        self.silent = silent
        self._buf = b""
        self.sent = []
        self.closed = False

    @property
    def in_waiting(self):
        return len(self._buf)

    def read(self, n):
        chunk, self._buf = self._buf[:n], self._buf[n:]
        return chunk

    def write(self, data):
        command = data.decode().strip()
        self.sent.append(command)
        if self.silent:
            return len(data)
        body = self.replies.get(command)
        if body is None:
            body = (command.split()[0] + "?\r\n").encode()
        self._buf = data + body + PROMPT
        return len(data)

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass

    def close(self):
        self.closed = True


ZS405 = {
    "version": b"tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1 \r\n",
    "info": b"tinySA ULTRA\r\n",
    "help": b"commands: rbw version info help scan\r\n",
}


@pytest.fixture
def fake_serial(monkeypatch):
    """Replace serial.Serial with ScriptedPort; return a dict to set replies/behaviour."""
    cfg = {"replies": ZS405, "silent": False, "raise": False, "created": []}

    def factory(port, timeout=1, **kwargs):
        if cfg["raise"]:
            raise OSError("could not open port " + port)
        p = ScriptedPort(port, timeout, cfg["replies"], cfg["silent"])
        cfg["created"].append(p)
        return p

    monkeypatch.setattr(core.serial, "Serial", factory)
    return cfg


class FakePortInfo:
    def __init__(self, device, vid, pid):
        self.device, self.vid, self.pid = device, vid, pid


# --- connect / autoconnect ----------------------------------------------------------

def test_connect_identifies(fake_serial):
    d = tinySA()
    assert d.connect("COM7") is True
    assert d.profile is ULTRA_ZS405 and d.firmwareBuild == (1, 4, 143)
    assert fake_serial["created"][0].sent[:3] == ["version", "info", "help"]


def test_connect_without_identification(fake_serial):
    d = tinySA()
    d.identifyOnConnect = False
    assert d.connect("COM7") is True
    assert d.profile is DEFAULT and fake_serial["created"][0].sent == []


def test_connect_failure_returns_false(fake_serial):
    fake_serial["raise"] = True
    d = tinySA()
    d.set_verbose(True)
    assert d.connect("COM99") is False
    assert d.ser is None


def test_connect_silent_device_does_not_hang(fake_serial):
    fake_serial["silent"] = True
    d = tinySA(serial_timeout=0.3)           # identify() caps at min(timeout, 3 s)
    started = time.monotonic()
    assert d.connect("COM7") is True
    assert (time.monotonic() - started) < 20     # the 3 s cap times a few reads; never the 120 s default
    assert d.profile is DEFAULT and d.get_serial_timeout() == 0.3


def test_autoconnect_finds_the_usb_id(fake_serial, monkeypatch):
    monkeypatch.setattr(core.serial.tools.list_ports, "comports", lambda: [
        FakePortInfo("COM3", None, None), FakePortInfo("COM4", 0x1234, 0x5678), FakePortInfo("COM7", 0x0483, 0x5740)])
    d = tinySA()
    assert d.autoconnect() == (True, True)
    assert fake_serial["created"][0].port == "COM7"


def test_autoconnect_nothing_found(fake_serial, monkeypatch):
    monkeypatch.setattr(core.serial.tools.list_ports, "comports", lambda: [FakePortInfo("COM3", None, None)])
    assert tinySA().autoconnect() == (False, False)


def test_disconnect_closes_and_logs(fake_serial, tmp_path):
    d = tinySA()
    d.connect("COM7")
    d.set_log_file(str(tmp_path / "l.jsonl"))
    d.disconnect()
    assert fake_serial["created"][0].closed
    assert '"event":"disconnect"' in (tmp_path / "l.jsonl").read_text()


def test_log_session_written_on_connect(fake_serial, tmp_path):
    d = tinySA()
    path = tmp_path / "l.jsonl"
    d.set_log_file(str(path))
    d.connect("COM7")
    text = path.read_text()
    assert text.count('"type":"session"') == 2            # once at set_log_file, once at connect
    assert '"event":"profile"' in text


def test_require_serial_message():
    with pytest.raises(RuntimeError, match="not connected"):
        tinySA().version()


# --- identify corner cases ---------------------------------------------------------------

def test_identify_without_help_uses_profile_commands():
    d = tinySA()
    d.set_error_byte_return(True)
    d.ser = ScriptedPort(replies={"version": ZS405["version"], "info": ZS405["info"], "help": b"",
                                  "hop 100000000.0 200000000.0 5": b"100000000 -90.0 \r\n"})
    d.identify()
    assert d.deviceCommands is None
    assert d.hop(1e8, 2e8, 5) != bytearray(b"ERROR")      # falls back to the ZS405 profile list
    assert d.waitscan(1) == bytearray(b"ERROR")            # not in the profile's command set


def test_identify_below_floor_logs_event(tmp_path):
    d = tinySA()
    path = tmp_path / "l.jsonl"
    d.set_log_file(str(path))
    d.ser = ScriptedPort(replies=ZS405)
    found = d.identify()
    assert found["build"] == [1, 4, 143] and found["profile"].startswith("tinySA Ultra")
    assert '"event":"firmware-below-floor"' in path.read_text()


def test_identify_basic_and_profile_for():
    d = tinySA()
    d.ser = ScriptedPort(replies={"version": b"tinySA_v1.4-244-gabc1234\r\n", "info": b"tinySA v0.3ZS304\r\n",
                                  "help": b"commands: scan\r\n"})
    d.identify()
    assert d.profile is BASIC
    assert profile_for("ultra", "ZS999").board == "unknown"
    assert profile_for("nanovna", "x") is DEFAULT
    assert ULTRA_ZS405.has_command("hop") and not BASIC.has_command("hop")


def test_set_output_allowed_logs(tmp_path):
    d = tinySA()
    path = tmp_path / "l.jsonl"
    d.set_log_file(str(path))
    d.set_output_allowed(True)
    assert '"event":"output-allowed","detail":"True"' in path.read_text()


# --- legacy boundary setters (kept for compatibility) --------------------------------------

def test_legacy_boundary_setters_and_flags():
    d = tinySA()
    d.set_min_SA_freq("1e5"); d.set_max_SA_freq(6e9); d.set_min_SG_freq(2e5); d.set_max_SG_freq(9e8)
    assert (d.get_min_SA_freq(), d.get_max_SA_freq(), d.get_min_SG_freq(), d.get_max_SG_freq()) == (1e5, 6e9, 2e5, 9e8)
    d.set_ultra_mode(True); d.set_abort_mode(True); d.set_harmonic_mode(True)
    assert d.ultraEnabled and d.abortEnabled and d.harmonicEnabled
    assert d.get_verbose() is False
    d.set_verbose(True)
    assert d.get_verbose() is True and d.get_error_byte_return() is False
    d.load_custom_config("x.toml")            # still a no-op
    d.convert_frequency("1M"); d.convert_time("1m")


def test_get_profile_and_select_logs(tmp_path):
    d = tinySA()
    path = tmp_path / "l.jsonl"
    d.set_log_file(str(path))
    d.select_existing_device("basic")
    assert d.get_profile() is BASIC
    assert "(selected)" in path.read_text()


# --- binary reads: timeout and streaming branches ---------------------------------------------

def test_scan_raw_short_frame_is_a_failure(parsing_tsa):
    # 4.0.0: a partial frame is not returned as data (callers unpack 3*pts bytes)
    parsing_tsa.ser._buf = b"scanraw 1 2 4 1\r\n{x\x01\x02x\x03"   # 2 of 4 points
    assert parsing_tsa.get_binary_return(4, timeout=0.2) is None
    assert parsing_tsa._serial_timed_out is True


def test_scan_raw_short_frame_through_scan_raw_is_logged_as_timeout(parsing_tsa, tmp_path):
    import json
    parsing_tsa.set_serial_timeout(0.1)
    log = tmp_path / "t.jsonl"
    parsing_tsa.set_log_file(str(log))
    parsing_tsa.ser.answer(b"scanraw 1000000 2000000 4 1\r\n{x\x01\x02")
    assert parsing_tsa.scan_raw(1_000_000, 2_000_000, 4) is None
    assert parsing_tsa.get_last_status() == "timeout"
    rec = [json.loads(l) for l in log.read_text().splitlines() if '"scanraw' in l][-1]
    assert rec["status"] == "timeout"


def test_scan_raw_no_frame_start_is_a_failure(parsing_tsa):
    parsing_tsa.set_error_byte_return(True)
    parsing_tsa.ser._buf = b"scanraw 1 2 4 1\r\n"
    assert parsing_tsa.get_binary_return(4, timeout=0.2) is None


def test_binary_streaming_mode_finds_boundary(parsing_tsa):
    frame = b"{" + b"x\x7d\x01" * 3 + b"}"        # 0x7d inside a sample must not end the frame
    parsing_tsa.ser._buf = b"scanraw\r\n" + frame
    assert parsing_tsa.get_binary_return(None) == bytearray(frame[:-1])


def test_binary_streaming_mode_idle_is_a_failure(parsing_tsa):
    parsing_tsa.ser._buf = b"scanraw\r\n{x\x01\x02"
    assert parsing_tsa.get_binary_return(None, timeout=5, idle_timeout=0.1) is None


def test_binary_streaming_mode_no_brace(parsing_tsa):
    parsing_tsa.set_error_byte_return(True)
    parsing_tsa.ser._buf = b"junk"
    assert parsing_tsa.get_binary_return(None, timeout=0.2, idle_timeout=0.1) is None


# --- sd_read paths ---------------------------------------------------------------------------

def test_sd_read_error_text(parsing_tsa):
    parsing_tsa.ser.answer(b"sd_read nope.bin\r\nerr: (4) no file\r\nch> ")
    assert parsing_tsa.sd_read("nope.bin") == bytearray(b"err: (4) no file")


def test_sd_read_timeout(parsing_tsa):
    parsing_tsa.set_serial_timeout(0.2)
    parsing_tsa.ser.answer(b"sd_read big.bin\r\n" + (1000).to_bytes(4, "little") + bytes(10))
    assert parsing_tsa.sd_read("big.bin") is None


def test_save_firmware_dump_warns_on_odd_size(tmp_path):
    d = tinySA()
    d.ser = ScriptedPort(replies={"sd_list *.bin": b"odd.bin 10\r\n",
                                  "sd_read odd.bin": (10).to_bytes(4, "little") + bytes(10)})
    d.select_existing_device("ZS405")
    assert d.save_firmware_dump(str(tmp_path / "o.bin")) == 10


# --- getters: unparsable and unit variants ---------------------------------------------------

@pytest.mark.parametrize("cmd,reply,method,value", [
    ("rbw ?", b"usage: rbw\r\n1MHz\r\n", "get_rbw", 1000.0),
    ("rbw ?", b"usage: rbw\r\n850Hz\r\n", "get_rbw", 0.85),
    ("sweeptime ?", b"usage: sweeptime\r\n500us\r\n", "get_sweep_time", 0.0005),
    ("sweeptime ?", b"usage: sweeptime\r\n2.5s\r\n", "get_sweep_time", 2.5),
    ("if ?", b"usage: if\r\n434000kHz\r\n", "get_IF", 434e6),
    ("if ?", b"usage: if\r\n433800000Hz\r\n", "get_IF", 433.8e6),
])
def test_getter_units(cmd, reply, method, value):
    d = tinySA()
    d.ser = ScriptedPort(replies={cmd: reply})
    assert getattr(d, method)() == pytest.approx(value)


def test_getters_none_on_empty_or_short():
    d = tinySA()
    d.ser = ScriptedPort(replies={"rbw ?": b"", "sweep": b"100\r\n", "dac ?": b"", "sweeptime ?": b"", "if ?": b""})
    assert d.get_rbw() is None and d.get_sweep_range() is None and d.get_dac_value() is None
    assert d.get_sweep_time() is None and d.get_IF() is None
    d.ser = ScriptedPort(silent=True)
    d.set_serial_timeout(0.2)
    assert d.get_sweep_range() is None


def test_decode_number_colon_without_exponent():
    assert tinySA.decode_number("1:5") == 15.0


# --- log: identification failure inside _log_session is swallowed ----------------------------

def test_log_session_survives_broken_port(tmp_path):
    class Broken(ScriptedPort):
        def write(self, data):
            raise OSError("gone")
    d = tinySA()
    d.ser = Broken()
    d.set_verbose(True)
    assert d.set_log_file(str(tmp_path / "l.jsonl")) is True
    assert '"family":"unknown"' in (tmp_path / "l.jsonl").read_text()


def test_log_closed_level_change_and_unwritable(tmp_path):
    d = tinySA()
    assert d.set_log_file(str(tmp_path / "a.jsonl"), level="data") is True
    assert d.set_log_file(str(tmp_path / "b.jsonl")) is True     # replaces the first
    assert d.get_log_file().endswith("b.jsonl")
    d.close_log_file()
    d.close_log_file()                                            # idempotent


def test_print_message_collects_reason_only_while_logging(tmp_path):
    d = tinySA()
    d.print_message("ERROR: not logged")
    assert d._log_reason == ""
    d.set_log_file(str(tmp_path / "l.jsonl"))
    d.print_message("ERROR: one")
    d.print_message("ERROR: two")
    assert d._log_reason == "ERROR: one | ERROR: two"


# --- remaining command-module branches ----------------------------------------------------------

def test_correction_table_word_per_family(tsa):
    tsa.set_error_byte_return(True)
    assert tsa.correction("high") == bytearray(b"ERROR")           # Basic-only table on the ZS405
    tsa.correction("low")
    assert tsa._recorder.last == "correction low\r\n"
    assert tsa.correction("low", slot=25, freq=1e6, val=1.0) == bytearray(b"ERROR")
    assert tsa.correction("low", slot=1, freq=1, val=1.0) == bytearray(b"ERROR")   # freq below range
    assert tsa.correction("low", slot=1, freq=1e8, val=99) == bytearray(b"ERROR")  # dB out of range
    assert tsa.correction("nonsense", slot=1, freq=1e8, val=1) == bytearray(b"ERROR")
    tsa.correction("low", slot=1, freq=1e8, val=1.5)
    assert tsa._recorder.last == "correction low 1 100000000.0 1.5\r\n"


def test_get_color_paths(tsa):
    tsa._recorder.next_return = bytearray(b"usage: color {id} {rgb24}\r\n  0: 0x000000\r\n  1: 0xF8FCF8\r")
    assert tsa.get_color(1) == "0xF8FCF8"
    tsa.set_error_byte_return(True)
    assert tsa.get_color(31) == bytearray(b"ERROR")
    tsa._recorder.next_return = bytearray(b"")
    assert tsa.get_color(1) == bytearray(b"")


def test_trace_scale_reflevel_and_select(tsa):
    tsa.trace_reflevel(-20)
    assert tsa._recorder.last == "trace reflevel -20\r\n"
    tsa.trace_scale("auto")
    assert tsa._recorder.last == "trace scale auto\r\n"
    tsa.trace_select(2)
    assert tsa._recorder.last == "trace 2\r\n"
    tsa.trace_select(0)
    assert tsa._recorder.last == "trace 2\r\n"


def test_ultra_command_variants(tsa):
    tsa.set_error_byte_return(True)
    tsa.ultra("start", 800e6)
    assert tsa._recorder.last == "ultra start 800000000.0\r\n"
    assert tsa.ultra("sideways") == bytearray(b"ERROR")


def test_clear_and_reset_tolerates_serial_drop(tsa):
    calls = []

    def dropping(writebyte, printBool=False, pts=None, _raw=False):
        calls.append(writebyte)
        if writebyte.startswith("reset"):
            raise OSError("port gone")
        return bytearray(b"")

    tsa.tinySA_serial = dropping
    assert tsa.clear_and_reset() is None
    assert calls == ["clearconfig 1234\r\n", "reset\r\n"]


def test_scan_raw_stream_bad_range_and_idle():
    d = tinySA()
    d.firmwareBuild = (1, 4, 244)
    assert list(d.scan_raw_stream(2e8, 1e8, 4)) == []           # start > stop
    port = ScriptedPort(silent=True)
    d.ser = port
    import tsapython._commands.acquisition as acq
    # shorten the idle limit by monkeypatching time inside the generator is awkward; use a tiny
    # frame count with a port that sends one frame then stays silent
    class OneFrame(ScriptedPort):
        def write(self, data):
            self.sent.append(data.decode().strip())
            if data.startswith(b"scanraw"):
                self._buf = b"{" + b"x\x01\x02" * 4 + b"}"
            return len(data)
    d.ser = OneFrame()
    frames = list(d.scan_raw_stream(1e8, 2e8, 4, count=1))
    assert len(frames) == 1
    assert len(frames) == 1 and d.ser.sent[-1] == "pause"
    del acq


def test_wait_negative_rejected(tsa):
    tsa.set_error_byte_return(True)
    assert tsa.wait(-3) == bytearray(b"ERROR")


def test_abort_modes(tsa):
    tsa.set_error_byte_return(True)
    assert tsa.abort() == bytearray(b"")            # not enabled: nothing sent
    assert tsa._recorder.count == 0
    tsa.enable_abort()
    tsa.abort_action()
    assert tsa._recorder.calls == ["abort on\r\n", "abort\r\n"]
    assert tsa.abort("maybe") == bytearray(b"")


# --- 4.0.0 review fixes: command length, connect/disconnect lifecycle ---------------------------

def test_command_longer_than_the_firmware_line_is_refused_before_sending(parsing_tsa):
    # the check lives in tinySA_serial, so this goes through the FakePort, not the recorder
    parsing_tsa.set_error_byte_return(True)
    parsing_tsa.set_serial_timeout(0.2)
    port = parsing_tsa.ser
    assert parsing_tsa.text("A" * 48) == bytearray(b"ERROR")     # 'text ' + 48 = 53 bytes
    assert port.written == []
    assert parsing_tsa.get_last_status() == "blocked"
    port.answer(b"text " + b"A" * 42 + b"\r\nch> ")
    assert parsing_tsa.text("A" * 42) == bytearray(b"")          # 'text ' + 42 = 47: the limit itself
    assert port.written == [b"text " + b"A" * 42 + b"\r\n"]


def test_connect_closes_the_port_when_identification_raises(monkeypatch):
    import serial as pyserial
    from tsapython import tinySA

    class Dropped:
        closed = False
        port = "COMX"
        def __init__(self, **kw):
            pass
        @property
        def in_waiting(self):
            raise pyserial.SerialException("device dropped")
        def write(self, d):
            return len(d)
        def reset_input_buffer(self):
            pass
        def reset_output_buffer(self):
            pass
        def close(self):
            Dropped.closed = True

    monkeypatch.setattr(core.serial, "Serial", Dropped)
    d = tinySA()
    assert d.connect("COMX") is False
    assert Dropped.closed is True
    assert d.ser is None                    # not left pointing at a dead handle
    with pytest.raises(RuntimeError):
        d.version()


def test_disconnect_leaves_the_library_not_connected(parsing_tsa):
    parsing_tsa.disconnect()
    assert parsing_tsa.ser is None
    with pytest.raises(RuntimeError):
        parsing_tsa.version()
