#! /usr/bin/python3
"""
Shared pytest fixtures for the tsapython test suite.

These tests run WITHOUT hardware. The tinySA class talks to the device only
through `self.ser` (a pyserial Serial object) and the single method
`tinySA_serial()`. We exploit those two seams:

  * `recorder`   -> replaces tinySA_serial, capturing the exact command string
                    each library method builds. Use for command-construction tests.
  * `fake_port`  -> a stand-in serial port that returns canned bytes, letting us
                    test the real get_serial_return / clean_return / get_binary_return
                    parsing logic against captured device output.

Neither touches real hardware.
"""

import sys
import os
import pytest

# Make 'src' importable when running `pytest` from the repo root.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from tsapython import tinySA  # noqa: E402


# ---------------------------------------------------------------------------
# Command-construction seam
# ---------------------------------------------------------------------------

class SerialRecorder:
    """
    Drop-in replacement for tinySA.tinySA_serial.

    Records every writebyte string it is handed and returns a canned reply
    (default empty bytearray, matching the device's "no data" responses).
    Set .next_return to control what a given call hands back.
    """

    def __init__(self):
        self.calls = []            # list of writebyte strings, in order
        self.next_return = bytearray(b"")

    def __call__(self, writebyte, printBool=False, pts=None):
        self.calls.append(writebyte)
        return self.next_return

    # convenience accessors -------------------------------------------------
    @property
    def last(self):
        """The most recent command string sent, or None if nothing was sent."""
        return self.calls[-1] if self.calls else None

    @property
    def count(self):
        return len(self.calls)


@pytest.fixture
def recorder():
    """A bare SerialRecorder, in case a test wants to wire it up manually."""
    return SerialRecorder()


@pytest.fixture
def tsa(recorder):
    """
    A tinySA instance whose serial layer is replaced by the recorder.

    Device-parameter defaults are seeded (as select_existing_device would do)
    so that range-checking methods have sane bounds to validate against.
    Use this for command-construction tests:

        def test_agc(tsa):
            tsa.agc(3)
            assert tsa._recorder.last == 'agc 3\\r\\n'
    """
    dev = tinySA()
    # Seed library-side device bounds (normally set by select_existing_device).
    dev.maxPoints = 450
    dev.minSADeviceFreq = 100e3
    dev.maxSADeviceFreq = 12e9
    dev.minSGDeviceFreq = 100e3
    dev.maxSGDeviceFreq = 960e6
    dev.maxDeviceBattery = 4095
    dev.screenWidth = 480
    dev.screenHeight = 320

    dev.tinySA_serial = recorder
    dev._recorder = recorder          # handy backref for assertions
    return dev


# ---------------------------------------------------------------------------
# Parsing seam
# ---------------------------------------------------------------------------

class FakePort:
    """
    Minimal stand-in for serial.Serial, used to drive the real parsing helpers
    (get_serial_return, get_binary_return) with canned bytes.

    Feed it the raw bytes the device would emit; it dispenses them through the
    in_waiting / read() interface the library expects.
    """

    def __init__(self, payload=b""):
        self._buf = bytes(payload)
        self.written = []           # bytes written by the library
        self._reset_in = 0
        self._reset_out = 0

    # --- attributes the library reads/calls ---
    @property
    def in_waiting(self):
        return len(self._buf)

    def read(self, n):
        chunk, self._buf = self._buf[:n], self._buf[n:]
        return chunk

    def write(self, data):
        self.written.append(data)
        return len(data)

    def reset_input_buffer(self):
        self._reset_in += 1

    def reset_output_buffer(self):
        self._reset_out += 1

    def close(self):
        pass


@pytest.fixture
def parsing_tsa():
    """
    A tinySA instance with the REAL tinySA_serial/clean_return logic intact,
    but `ser` swapped for a FakePort. Load a payload per-test:

        def test_clean(parsing_tsa):
            parsing_tsa.ser._buf = b'deviceid\\r\\ndeviceid 0\\r\\nch>'
            out = parsing_tsa.get_serial_return()
            ...
    """
    dev = tinySA()
    dev.ser = FakePort()
    return dev