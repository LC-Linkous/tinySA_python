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