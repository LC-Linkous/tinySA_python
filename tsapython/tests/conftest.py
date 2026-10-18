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

    def __call__(self, writebyte, printBool=False, pts=None, _raw=False):
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

    select_existing_device("ZS405") below sets the device bounds the
    range-checking methods validate against (points, frequencies, screen).
    Use this for command-construction tests:

        def test_agc(tsa):
            tsa.agc(3)
            assert tsa._recorder.last == 'agc 3\\r\\n'
    """
    dev = tinySA()
    dev.tinySA_serial = recorder
    dev._recorder = recorder          # handy backref for assertions
    # 4.0.0: command-construction tests run with the RF output gate open and the
    # Ultra ZS405 profile selected, so gated calls are exercised rather than refused.
    dev.select_existing_device("ZS405")
    dev.set_output_allowed(True)
    return dev


# ---------------------------------------------------------------------------
# Parsing seam
# ---------------------------------------------------------------------------

class FakePort:
    """
    Stand-in for serial.Serial that behaves like the real port where the
    library's readers care:

    - reset_input_buffer() FLUSHES anything already in the buffer, as pyserial's
      does. So a reply loaded into `_buf` before the command is sent is thrown
      away by tinySA_serial(), exactly as a stale reply would be on hardware.
      Queue replies with answer() instead: each write() delivers the next one.
    - Replies can arrive in pieces: answer(..., chunks=n) or answer_chunked([...])
      hands the bytes out over several reads, so a prompt or the echo split
      across USB packets is exercised.
    - `_buf` can still be loaded directly for a reader called on its own
      (get_serial_return / get_binary_return / get_capture_return), which does
      not reset the buffer first.
    """

    def __init__(self, payload=b""):
        self._buf = bytes(payload)
        self._pending = []          # replies queued by answer(): one per write()
        self._chunks = []           # pieces of the current reply still to arrive
        self.written = []           # bytes written by the library
        self._reset_in = 0
        self._reset_out = 0

    # --- test helpers ---
    def answer(self, *replies, chunks=1):
        """Queue one reply per future write(). chunks>1 splits each into that many reads."""
        for reply in replies:
            reply = bytes(reply)
            if chunks <= 1 or len(reply) < 2:
                self._pending.append([reply])
            else:
                size = max(1, -(-len(reply) // chunks))
                self._pending.append([reply[i:i + size] for i in range(0, len(reply), size)])

    def answer_chunked(self, pieces):
        """Queue one reply for the next write(), delivered exactly in these pieces."""
        self._pending.append([bytes(p) for p in pieces])

    # --- attributes the library reads/calls ---
    @property
    def in_waiting(self):
        if not self._buf and self._chunks:
            self._buf = self._chunks.pop(0)      # the next USB packet "arrives"
        return len(self._buf)

    def read(self, n):
        chunk, self._buf = self._buf[:n], self._buf[n:]
        return chunk

    def write(self, data):
        self.written.append(data)
        if self._pending:
            self._chunks = self._pending.pop(0)
        return len(data)

    def reset_input_buffer(self):
        self._reset_in += 1
        self._buf = b""
        self._chunks = []

    def reset_output_buffer(self):
        self._reset_out += 1

    def close(self):
        pass


@pytest.fixture
def parsing_tsa():
    """
    A tinySA instance with the REAL tinySA_serial/clean_return logic intact,
    but `ser` swapped for a FakePort. Queue the device's reply, then call:

        def test_deviceid(parsing_tsa):
            parsing_tsa.ser.answer(b'deviceid\\r\\ndeviceid 0\\r\\nch> ')
            assert parsing_tsa.command('deviceid') == bytearray(b'deviceid 0\\r')

    Loading `_buf` directly only works for a reader called on its own (the
    command path flushes the input buffer first, as the real port does).
    """
    dev = tinySA()
    dev.ser = FakePort()
    return dev
