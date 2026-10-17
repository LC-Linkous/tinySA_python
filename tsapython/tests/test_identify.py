#! /usr/bin/python3
"""
Tests for the pure text helpers in _identify.py.

The ZS405 v1.4-143 replies are real captures (fixtures/captured_responses.py).
Replies for the other boards and builds are RECONSTRUCTED from the firmware
source and have not been captured from hardware.
"""

import pytest

from tsapython._identify import classify_reply, identify_device


@pytest.mark.parametrize("version,info,family,board,build", [
    # real capture
    ("tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1 ", "tinySA ULTRA\r\n2019-2024 ...",
     "ultra", "ZS405", [1, 4, 143]),
    # reconstructed from source
    ("tinySA4_v1.4-244-g650f538\r\nHW Version:V0.4.5.1 ", "tinySA ULTRA ZS405", "ultra", "ZS405", [1, 4, 244]),
    ("tinySA4_v1.4-244-g650f538\r\nHW Version:V0.4.6 ", "tinySA ULTRA+ ZS406", "ultra", "ZS406", [1, 4, 244]),
    ("tinySA4_v1.4-244-g650f538\r\nHW Version:V0.5.4 max2871", "tinySA ULTRA+ ZS407", "ultra", "ZS407", [1, 4, 244]),
    ("tinySA4_v1.4-182-ga85ca92\r\nHW Version:V0.5.3.2 max2871", "tinySA ULTRA", "ultra", "ZS407", [1, 4, 182]),
    ("tinySA4_v1.4-244-g650f538\r\nHW Version:Unknown ", "tinySA ULTRA", "ultra", "unknown", [1, 4, 244]),
    ("tinySA4_v1.4-244-g650f538\r\nHW Version:Unknown ", "tinySA ULTRA+ ZS407", "ultra", "ZS407", [1, 4, 244]),
    ("tinySA_v1.4-244-g650f538", "tinySA v0.3ZS304", "basic", "ZS304", [1, 4, 244]),
    ("tinySA4_unknown\r\nHW Version:V0.4.5.1.1 ", "", "ultra", "ZS405", None),
    ("ch> something else", "", "unknown", "unknown", None),
    ("", "", "unknown", "unknown", None),
])
def test_identify_device(version, info, family, board, build):
    found = identify_device(version, info)
    assert found["family"] == family
    assert found["board"] == board
    assert found["build"] == build


@pytest.mark.parametrize("sent,reply,status", [
    ("rbw 30\r\n", b"", "ok"),
    ("version\r\n", b"tinySA4_v1.4-143-g864bb27\r", "ok"),
    # a rejected argument
    ("calc quasip\r\n", b"usage: calc [{trace#}] off|minh\r\nOFF\r", "usage"),
    ("mode high input\r\n", b"usage: mode [low] input|output\r", "usage"),
    ("marker 9 on\r\n", b"marker [n] [on|off|peak]\r", "usage"),
    # the same usage text is the ANSWER when the command was a query
    ("rbw\r\n", b"usage: rbw 0.2..850|auto\r\n300.0Hz\r", "ok"),
    ("rbw ?\r\n", b"usage: rbw 0.2..850|auto\r\n300.0Hz\r", "ok"),
    # command missing from this firmware
    ("waitscan 1\r\n", b"waitscan?\r", "unknown-command"),
    ("usbdisk\r\n", b"usbdisk?\r", "unknown-command"),
    # refusals
    ("scan 1 2 3 3\r\n", b"usb disk mode active\r", "device-refused"),
    ("scan 100 200 1 3\r\n", b"sweep points exceeds range 450\r", "device-refused"),
    ("scan 100 200 20 3\r\n", b"Command timeout\r", "device-refused"),
    # failed read
    ("version\r\n", None, "read-failed"),
])
def test_classify_reply(sent, reply, status):
    assert classify_reply(sent, reply)[0] == status
