#! /usr/bin/python3
"""
Hardware tests that switch the tinySA's RF OUTPUT ON.

Never run by default (pyproject deselects the marker). Two guards must both be
satisfied: run with `pytest -m hardware_output`, and set the environment
variable TSAPYTHON_OUTPUT_OK=1 to confirm a load or attenuator is on the RF port.

    TSAPYTHON_OUTPUT_OK=1 uv run pytest -m hardware_output -s

These tests only prove the device ACCEPTED each setting (nothing is read back
by the firmware). Measuring what comes out of the port is the job of
tests/bench_generator.py with a receiver.
"""

import os
import time

import pytest

pytestmark = pytest.mark.hardware_output

LEVEL_MIN = -76          # bottom of every model's low output range


@pytest.fixture
def gen():
    if os.environ.get("TSAPYTHON_OUTPUT_OK") != "1":
        pytest.skip("set TSAPYTHON_OUTPUT_OK=1 with a load or attenuator on the RF port")
    from tsapython import tinySA
    dev = tinySA()
    dev.set_error_byte_return(True)
    found, connected = dev.autoconnect()
    if not connected:
        pytest.skip("no tinySA device connected")
    dev.set_output_allowed(True)
    assert dev.setup_generator(10e6, LEVEL_MIN) is True
    yield dev
    dev.output("off")
    dev.modulation("off")
    dev.mode("low", "input")
    dev.disconnect()


def ok(reply):
    return reply is not None and reply != bytearray(b"ERROR")


def test_output_on_and_off_accepted(gen):
    assert ok(gen.output("on"))
    time.sleep(0.5)
    assert ok(gen.output("off"))


def test_level_steps_accepted(gen):
    # settings in output mode go through set_generator(), which pauses the sweep
    # so 'level' returns at once instead of waiting for a generator sweep to end
    assert ok(gen.output("on"))
    for level in (-76, -60, -40.5, -20, -6):
        assert gen.set_generator(level_dbm=level) is True, level
        time.sleep(0.3)
    assert gen.set_generator(level_dbm=LEVEL_MIN) is True
    assert ok(gen.output("off"))


def test_frequency_changes_accepted(gen):
    assert ok(gen.output("on"))
    for freq in (1e6, 10e6, 100e6, 300e6):
        assert gen.set_generator(freq_hz=freq) is True, freq
        time.sleep(0.3)
    assert ok(gen.output("off"))


def test_am_and_fm_accepted(gen):
    words = gen.profile.modulation_words
    assert ok(gen.output("on"))
    assert gen.set_generator(modulation_type="am", modulation_rate_hz=1000) is True
    if "fm" in words:                       # Ultra family
        assert gen.set_generator(depth_percent=50) is True
        assert gen.set_generator(modulation_type="fm", deviation_hz=3000) is True
    else:                                   # Basic
        assert gen.set_generator(modulation_type="nfm") is True
    assert gen.set_generator(modulation_type="off") is True
    assert ok(gen.output("off"))


def test_mode_change_mutes(gen):
    """The firmware switches the output off on a mode change; the library relies on that."""
    assert ok(gen.output("on"))
    assert ok(gen.mode("low", "input"))
    assert ok(gen.mode("low", "output"))
    # after the mode change the output must be off; nothing can read that back,
    # so this test only documents the sequence for the bench session to observe
    assert gen.set_generator(level_dbm=LEVEL_MIN) is True
