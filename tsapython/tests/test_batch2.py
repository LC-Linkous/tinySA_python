#! /usr/bin/python3
"""
Batch 2 (3.1.0): getters, SD card download, firmware dump, new command wrappers,
prompt detection, ':' decoding. Mocked serial; no hardware.
"""

import pytest

from tsapython import tinySA

PROMPT = b"ch> "


class ScriptedPort:
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
        if body is not None:
            self._buf = data + body + PROMPT
        return len(data)

    def reset_input_buffer(self):
        pass

    def reset_output_buffer(self):
        pass

    def close(self):
        pass


FIRMWARE = bytes(range(256)) * 1024                         # 262144 bytes, every byte value

REPLIES = {
    # real replies from the ZS405 v1.4-143 probe run
    "rbw ?": b"usage: rbw 0.2..850|auto\r\n10kHz\r\n",
    "attenuate ?": b"usage: attenuate 0..31|auto\r\n   0\r\n",
    "sweeptime ?": b"usage: sweeptime 0.003..60\r\n 462ms\r\n",
    "if ?": b"usage: usage: if {975M..979M}\r\n977.400000MHz\r\n",
    "zero ?": b"usage: zero {level}\r\n174dBm\r\n",
    "nf ?": b"usage: nf {value}\r\n5.000000000\r\n",
    "dac ?": b"usage: dac {value(0-4095)}\r\ncurrent value: 1922\r\n",
    "calc ?": b"usage: calc [{trace#}] off|minh|maxh|maxd|aver4|aver16|aver|quasi|log|lin\r\nQUASI\r\n",
    "sweep": b"97600000 98600000 450\r\n",
    "deviceid ?": b"usage: deviceid [<number>]\r\n",
    "sd_list *.bin": b"LINKOUSFW.bin 262144\r\nSMALL.bin 100\r\n",
    "sd_list": b"LINKOUSFW.bin 262144\r\n-0.bmp 307322\r\n",
    "sd_read LINKOUSFW.bin": (262144).to_bytes(4, "little") + FIRMWARE,
    "sd_read SMALL.bin": (100).to_bytes(4, "little") + bytes(100),
    "sd_read missing.bin": b"err: (4) no file\r\n",
    "waitscan 1": b"waitscan?\r\n",
}


@pytest.fixture
def dev():
    d = tinySA()
    d.ser = ScriptedPort(dict(REPLIES))
    d.set_error_byte_return(True)
    return d


# --- getters ---------------------------------------------------------------------

def test_getters_parse_real_replies(dev):
    assert dev.get_rbw() == 10.0
    assert dev.get_attenuation() == 0.0
    assert dev.get_sweep_time() == pytest.approx(0.462)
    assert dev.get_IF() == 977_400_000.0
    assert dev.get_scanraw_offset() == 174
    assert dev.get_noise_figure() == 5.0
    assert dev.get_dac_value() == 1922
    assert dev.get_calc() == "QUASI"
    assert dev.get_sweep_range() == (97_600_000, 98_600_000, 450)


def test_getter_rbw_in_hz():
    d = tinySA()
    d.ser = ScriptedPort({"rbw ?": b"usage: rbw 0.2..850|auto\r\n300Hz\r\n"})
    assert d.get_rbw() == pytest.approx(0.3)


def test_getter_returns_none_on_unknown_command():
    d = tinySA()
    d.ser = ScriptedPort({"nf ?": b"nf?\r\n"})
    assert d.get_noise_figure() is None


# --- prompt detection: text containing '>' is no longer cut short ----------------

def test_reply_containing_greater_than(dev):
    assert dev.command("deviceid ?") == bytearray(b"usage: deviceid [<number>]\r")


def test_prompt_without_trailing_space_still_terminates(parsing_tsa):
    parsing_tsa.ser._buf = b"deviceid\r\ndeviceid 0\r\nch>"
    assert parsing_tsa.get_serial_return().endswith(b"ch>")


# --- ':' artifact ------------------------------------------------------------------

@pytest.mark.parametrize("text,value", [
    ("-:.000000e+01", -100.0),
    (":.000000e+00", 10.0),
    ("-6.446875e+01", -64.46875),
    (b"-5.715625e+01", -57.15625),
    ("100000000", 100000000.0),
])
def test_decode_number(text, value):
    assert tinySA.decode_number(text) == pytest.approx(value)


# --- SD card and firmware dump -------------------------------------------------------

def test_list_sd_files(dev):
    assert dev.list_sd_files() == [("LINKOUSFW.bin", 262144), ("-0.bmp", 307322)]
    assert dev.list_sd_files("*.bin") == [("LINKOUSFW.bin", 262144), ("SMALL.bin", 100)]


def test_sd_read_returns_every_byte(dev):
    data = dev.sd_read("LINKOUSFW.bin")
    assert len(data) == 262144
    assert bytes(data) == FIRMWARE               # includes 0x3E, 0x7D and 'ch> ' sequences


def test_save_sd_file(dev, tmp_path):
    out = tmp_path / "small.bin"
    assert dev.save_sd_file("SMALL.bin", str(out)) == 100
    assert out.read_bytes() == bytes(100)


def test_save_sd_file_missing(dev, tmp_path):
    assert dev.save_sd_file("missing.bin", str(tmp_path / "x")) == -1
    assert not (tmp_path / "x").exists()


def test_save_firmware_dump_picks_largest_bin(dev, tmp_path):
    out = tmp_path / "fw.bin"
    assert dev.save_firmware_dump(str(out)) == 262144
    assert out.read_bytes() == FIRMWARE


def test_save_firmware_dump_no_file(tmp_path):
    d = tinySA()
    d.ser = ScriptedPort({"sd_list *.bin": b"err: (3) no card\r\n"})
    assert d.save_firmware_dump(str(tmp_path / "fw.bin")) == -1


# --- new command wrappers (recorder) ----------------------------------------------

@pytest.mark.parametrize("call,expected", [
    (lambda t: t.waitscan(3), "waitscan 3\r\n"),
    (lambda t: t.resume(5), "resume 5\r\n"),
    (lambda t: t.resume(), "resume\r\n"),
    (lambda t: t.channel(), "channel\r\n"),
    (lambda t: t.channel(2), "channel 2\r\n"),
    (lambda t: t.time(), "time\r\n"),
    (lambda t: t.time("h", 13), "time h 13\r\n"),
    (lambda t: t.usbdisk(), "usbdisk\r\n"),
    (lambda t: t.usbdisk("off"), "usbdisk off\r\n"),
    (lambda t: t.avoid("dump"), "avoid dump\r\n"),
    (lambda t: t.correction_reset("low"), "correction low reset\r\n"),
    (lambda t: t.sweep_mode("precise"), "sweep precise\r\n"),
    (lambda t: t.sd_list("*.bin"), "sd_list *.bin\r\n"),
    (lambda t: t.marker_mode(2, "delta", 1), "marker 2 delta 1\r\n"),
    (lambda t: t.marker_mode(2, "noise", "on"), "marker 2 noise on\r\n"),
    (lambda t: t.marker_mode(1, "trace", 2), "marker 1 trace 2\r\n"),
    (lambda t: t.marker_all_off(), "marker off\r\n"),
    (lambda t: t.marker_read(), "marker\r\n"),
    (lambda t: t.marker_read(3), "marker 3\r\n"),
])
def test_new_wrappers_send(tsa, call, expected):
    call(tsa)
    assert tsa._recorder.last == expected


@pytest.mark.parametrize("call", [
    lambda t: t.waitscan(0),
    lambda t: t.resume(0),
    lambda t: t.channel(4),
    lambda t: t.time("year", 5),
    lambda t: t.usbdisk("maybe"),
    lambda t: t.avoid("sometimes"),
    lambda t: t.correction_reset("everything"),
    lambda t: t.sweep_mode("slow"),
    lambda t: t.marker_mode(2, "noise", "maybe"),
    lambda t: t.marker_mode(0, "delta", 1),
    lambda t: t.marker_read(0),
])
def test_new_wrappers_block_bad_input(tsa, call):
    call(tsa)
    assert tsa._recorder.count == 0


def test_unknown_command_reply_is_the_error_value(dev):
    # on firmware before v1.4-216 the device answers 'waitscan?'; 4.0.0 returns the error value
    assert dev.waitscan(1) == bytearray(b"ERROR")
    # the raw escape hatch still shows the device's text
    assert dev.command("waitscan 1") == bytearray(b"waitscan?\r")
