#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './tests/test_hardware.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Hardware-backed pytest tests. These REQUIRE a serial-connected tinySA device and are
#   skipped by default. Run them explicitly with:
#
#       pytest -m hardware
#
#   Run everything EXCEPT these with:
#
#       pytest -m "not hardware"   (or just `pytest`, which skips on no-connect)
#
#   The demonstrative connect/info walkthrough now lives in examples/hardware_walkthrough.py;
#   this file keeps only the checks that actually assert correctness.
#
#   Author(s): Lauren Linkous
#   Last update: June 3rd, 2026
##--------------------------------------------------------------------------------------------------\

import pytest

pytestmark = pytest.mark.hardware


@pytest.fixture
def device():
    """
    Connect to a real tinySA for the duration of one test, then disconnect.
    Skips (does not fail) if no device is detected, so `pytest -m hardware`
    on a machine without hardware reports skips rather than errors.
    """
    from tsapython import tinySA
    dev = tinySA()
    dev.set_verbose(True)
    dev.set_error_byte_return(True)

    found, connected = dev.autoconnect()
    if not connected:
        pytest.skip("no tinySA device connected")
    yield dev
    dev.disconnect()


def test_device_id_nonempty(device):
    """A connected device returns a non-empty device id."""
    device_id = device.get_device_id()
    assert device_id  # non-empty bytearray


def test_device_info_nonempty(device):
    """A connected device returns non-empty info text."""
    info = device.info()
    assert info


def test_hop_returns_npts_plus_one(device):
    """
    hop() returns one MORE point than requested: the initial frequency point
    is included. This is the substantive behavioral check carried over from the
    old test_hardware.py.
    """
    start_freq = 100e6   # 100 MHz
    stop_freq = 500e6    # 500 MHz
    n_pts = 12

    device.pause()

    freq_vals = device.hop(start_freq, stop_freq, n_pts, 1)   # frequencies
    dbm_vals = device.hop(start_freq, stop_freq, n_pts, 2)    # measured data
    assert freq_vals, "no frequency data returned"
    assert dbm_vals, "no power data returned"

    freq_list = [float(x) for x in freq_vals.decode("utf-8").split()]
    power_list = [float(x) for x in dbm_vals.decode("utf-8").split()]

    assert len(freq_list) == n_pts + 1
    assert len(power_list) == n_pts + 1


# ---------------------------------------------------------------------------
# 3.1.0: set-and-read-back checks. Each one restores what it changed.
# ---------------------------------------------------------------------------

def test_attenuate_31_round_trip(device):
    """31 is the top of the firmware range and used to be refused by the library."""
    try:
        device.attenuate(31)
        assert device.get_attenuation() == 31.0
    finally:
        device.attenuate("auto")


def test_rbw_decimal_round_trip(device):
    """rbw 0.3 asks for 300 Hz; the device rounds UP to its next available RBW."""
    try:
        device.rbw(0.3)
        value = device.get_rbw()
        assert value is not None and 0.2 <= value <= 1.0
    finally:
        device.rbw("auto")


def test_calc_quasi_round_trip(device):
    try:
        device.calc("quasip")                      # old keyword, sent as 'quasi'
        assert device.get_calc() == "QUASI"
    finally:
        device.calc("off")


def test_getters_return_values(device):
    assert device.get_scanraw_offset() in (128, 174)
    assert device.get_dac_value() is not None
    assert device.get_sweep_range() is not None
    assert device.get_sweep_time() is not None


def test_capture_is_full_frame(device):
    """The screen dump must be exactly width*height*2 bytes (480x320 Ultra, 320x240 Basic)."""
    data = device.capture()
    assert len(data) in (480 * 320 * 2, 320 * 240 * 2)


def test_reply_with_greater_than_is_complete(device):
    """'usage: deviceid [<number>]' used to be cut at the '>' inside the text."""
    reply = device.command("deviceid ?")
    assert b"[<number>]" in reply


def test_sd_list_parses(device):
    """Ultra family only: a device without a card returns an empty list, not an error."""
    files = device.list_sd_files()
    assert isinstance(files, list)
    for name, size in files:
        assert isinstance(name, str) and size >= 0
