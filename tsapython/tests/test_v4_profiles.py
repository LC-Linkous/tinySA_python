#! /usr/bin/python3
"""
4.0.0 behaviour: device profiles chosen at connect, per-device gates, the RF
output setting, device rejections returned as the error value, scan_raw split.
Mocked serial; no hardware.
"""

from tsapython import tinySA
from tsapython._profiles import BASIC, DEFAULT, ULTRA_ZS405, ULTRA_PLUS_ZS406, ULTRA_PLUS_ZS407

PROMPT = b"ch> "


class ScriptedPort:
    port = "FAKE0"

    def __init__(self, replies):
        self.replies = replies
        self._buf = b""
        self.sent = []

    @property
    def in_waiting(self):
        return len(self._buf)

    def read(self, n):
        chunk, self._buf = self._buf[:n], self._buf[n:]
        return chunk

    def write(self, data):
        command = data.decode().strip()
        self.sent.append(command)
        body = self.replies.get(command)
        if body is None:
            body = (command.split()[0] + "?\r\n").encode()      # unknown command
        self._buf = data + body + PROMPT
        return len(data)

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass

    def close(self):
        pass


HELP_143 = (b"commands: freq time dac nf saveconfig clearconfig zero sweep pause resume wait repeat status "
            b"caloutput save recall trace trigger marker line usart_cfg vbat_offset color if if1 lna2 agc "
            b"actual_freq freq_corr attenuate level sweeptime leveloffset levelchange modulation rbw mode "
            b"spur lna direct ultra load ext_gain output deviceid correction calc menu text remark\r\n"
            b"Other commands: version reset data frequencies scan hop scanraw test touchcal touchtest usart "
            b"capture refresh touch release vbat help info selftest sd_list sd_read sd_delete threads\r\n")

ZS405_143 = {
    "version": b"tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1 \r\n",
    "info": b"tinySA ULTRA\r\n2019-2024 Copyright @Erik Kaashoek\r\n",
    "help": HELP_143,
    "rbw 30": b"", "output off": b"", "output on": b"", "caloutput 30": b"", "caloutput off": b"",
    "mode high input": b"usage: mode [low] input|output\r\n",
    "calc quasi": b"", "attenuate 31": b"", "hop 100000000 200000000 5 3": b"100000000 -90.0 \r\n",
    "spur auto": b"",
}

ZS407_244 = {
    "version": b"tinySA4_v1.4-244-g650f538\r\nHW Version:V0.5.4 max2871\r\n",
    "info": b"tinySA ULTRA+ ZS407\r\n2019-2024 Copyright @Erik Kaashoek\r\n",
    "help": HELP_143.replace(b"remark\r\n", b"remark avoid waitscan channel usbdisk abort restart\r\n"),
    "waitscan 1": b"",
}

BASIC_244 = {
    "version": b"tinySA_v1.4-244-g650f538\r\n",
    "info": b"tinySA v0.3ZS304\r\n2019-2024 Copyright @Erik Kaashoek\r\n",
    "help": b"commands: freq dac saveconfig clearconfig zero sweep pause resume wait repeat status caloutput save recall "
            b"trace trigger marker line vbat_offset color if actual_freq attenuate level sweeptime leveloffset levelchange "
            b"modulation rbw mode spur load ext_gain output deviceid correction calc menu text remark version reset data "
            b"frequencies scan scanraw abort test touchcal touchtest capture refresh touch release vbat help info selftest threads\r\n",
    "mode high input": b"",
}


def connect(replies):
    d = tinySA()
    d.set_error_byte_return(True)
    port = ScriptedPort(dict(replies))
    d.ser = port
    d.identify()
    return d, port


# --- identification at connect -------------------------------------------------

def test_identify_zs405():
    d, _ = connect(ZS405_143)
    assert d.profile is ULTRA_ZS405
    assert d.profileDetected is True
    assert d.firmwareBuild == (1, 4, 143)
    assert "hop" in d.deviceCommands and "waitscan" not in d.deviceCommands
    assert d.maxPoints == 450 and d.screenWidth == 480


def test_identify_zs407():
    d, _ = connect(ZS407_244)
    assert d.profile is ULTRA_PLUS_ZS407
    assert d.firmwareBuild == (1, 4, 244)
    assert "waitscan" in d.deviceCommands


def test_identify_basic():
    d, _ = connect(BASIC_244)
    assert d.profile is BASIC
    assert d.maxPoints == 290 and d.screenWidth == 320 and d.screenHeight == 240


def test_identify_unknown_device_keeps_default():
    d, _ = connect({"version": b"NanoVNA-H 1.2.3\r\n", "info": b"NanoVNA\r\n", "help": b"commands: scan\r\n"})
    assert d.profile is DEFAULT
    assert d.profileDetected is False


def test_connect_can_skip_identification():
    d = tinySA()
    d.identifyOnConnect = False
    assert d.profile is DEFAULT


def test_select_existing_device():
    d = tinySA()
    assert d.select_existing_device("ZS406") is True
    assert d.profile is ULTRA_PLUS_ZS406 and d.profileDetected is False
    assert d.select_existing_device("ZS999") is False
    assert d.profile is ULTRA_PLUS_ZS406


# --- device rejections become the error value ---------------------------------

def test_usage_reply_returns_error_value():
    d, port = connect(BASIC_244 | {"mode high input": b"usage: mode low|high input|output\r\n"})
    assert d.mode("high", "input") == bytearray(b"ERROR")
    assert port.sent[-1] == "mode high input"              # it WAS sent; the device refused


def test_usage_reply_returns_empty_with_flag_off():
    d, _ = connect(BASIC_244 | {"mode high input": b"usage: mode low|high input|output\r\n"})
    d.set_error_byte_return(False)
    assert d.mode("high", "input") == bytearray(b"")


def test_command_passthrough_is_raw():
    d, _ = connect(ZS405_143)
    assert d.command("mode high input") == bytearray(b"usage: mode [low] input|output\r")
    assert d.command("waitscan 1") == bytearray(b"waitscan?\r")


def test_getters_are_not_treated_as_rejections():
    d, _ = connect(ZS405_143 | {"rbw ?": b"usage: rbw 0.2..850|auto\r\n10kHz\r\n"})
    assert d.get_rbw() == 10.0


# --- gates: commands the firmware lacks are not sent ---------------------------

def test_command_missing_from_help_is_refused_before_sending():
    d, port = connect(ZS405_143)
    assert d.waitscan(1) == bytearray(b"ERROR")
    assert "waitscan 1" not in port.sent


def test_command_present_in_help_is_sent():
    d, port = connect(ZS407_244)
    assert d.waitscan(1) == bytearray(b"")
    assert port.sent[-1] == "waitscan 1"


def test_ultra_only_command_refused_on_basic():
    d, port = connect(BASIC_244)
    assert d.hop(100e6, 200e6, 5, 3) == bytearray(b"ERROR")
    assert d.lna("on") == bytearray(b"ERROR")
    assert d.sd_list() == bytearray(b"ERROR")
    assert not any(s.startswith(("hop", "lna", "sd_list")) for s in port.sent)


def test_word_wrong_for_family_refused_before_sending():
    d, port = connect(ZS405_143)
    assert d.mode("high", "input") == bytearray(b"ERROR")
    assert "mode high input" not in port.sent
    d2, port2 = connect(BASIC_244)
    assert d2.spur("auto") == bytearray(b"ERROR")
    assert d2.output("mixer") == bytearray(b"ERROR")
    assert d2.calc("log") == bytearray(b"ERROR")
    assert port2.sent[-1] == "help"


def test_marker_and_trace_counts_per_family(tsa):
    tsa.select_existing_device("BASIC")
    tsa.marker_on(5)
    tsa.trace_units(4, "dBm")
    assert tsa._recorder.count == 0
    tsa.select_existing_device("ZS405")
    tsa.marker_on(8)
    tsa.trace_units(4, "dBm")
    assert tsa._recorder.count == 2


# --- RF output setting ------------------------------------------------------------

def test_output_on_refused_until_allowed():
    d, port = connect(ZS405_143)
    assert d.get_output_allowed() is False
    assert d.output("on") == bytearray(b"ERROR")
    assert d.set_output_on() == bytearray(b"ERROR")
    assert d.cal_output(30) == bytearray(b"ERROR")
    assert not any(s in ("output on", "caloutput 30") for s in port.sent)
    assert d.output("off") == bytearray(b"")                # always allowed
    assert d.cal_output("off") == bytearray(b"")
    d.set_output_allowed(True)
    assert d.output("on") == bytearray(b"")
    assert d.cal_output(30) == bytearray(b"")
    assert port.sent[-2:] == ["output on", "caloutput 30"]


def test_output_allowed_sends_nothing_to_the_device():
    d, port = connect(ZS405_143)
    before = list(port.sent)
    d.set_output_allowed(True)
    assert port.sent == before


# --- scan_raw split ------------------------------------------------------------------

def test_scan_raw_accepts_only_0_and_1(tsa):
    tsa.scan_raw(1e8, 2e8, 20, 1)
    tsa.scan_raw(1e8, 2e8, 20, 0)
    assert tsa._recorder.count == 2
    tsa.scan_raw(1e8, 2e8, 20, 2)
    tsa.scan_raw(1e8, 2e8, 20, 3)
    assert tsa._recorder.count == 2


def test_scan_raw_stream_needs_build_177():
    d = tinySA()
    d.firmwareBuild = (1, 4, 143)
    assert list(d.scan_raw_stream(1e8, 2e8, 4)) == []


def test_scan_raw_stream_reads_frames_and_interrupts():
    class StreamPort(ScriptedPort):
        def write(self, data):
            command = data.decode().strip()
            self.sent.append(command)
            if command.startswith("scanraw"):
                frame = b"{" + b"x\x10\x20" * 4 + b"}"
                self._buf = data + frame * 3
            return len(data)

    d = tinySA()
    d.firmwareBuild = (1, 4, 244)
    port = StreamPort({})
    d.ser = port
    frames = list(d.scan_raw_stream(100, 200, 4, count=2))
    assert len(frames) == 2 and all(len(f) == 13 for f in frames)
    assert port.sent == ["scanraw 100 200 4 3", "pause"]
