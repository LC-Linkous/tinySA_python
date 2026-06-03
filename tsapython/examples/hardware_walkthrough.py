#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/hardware_walkthrough.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Demonstrative walkthrough of talking to a real device: connect, read the device id and
#   info, and collect a short hop() sweep. HARDWARE IS REQUIRED.
#
#   This is a human-readable demo (prints results as it goes). For the automated correctness
#   checks, see tests/test_hardware.py (run with `pytest -m hardware`).
#
#   Run with: python examples/hardware_walkthrough.py
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

from tsapython import tinySA


def walkthrough():
    print("=" * 50)
    print("HARDWARE WALKTHROUGH (requires a connected tinySA)")
    print("=" * 50)

    tsa = tinySA()
    tsa.set_verbose(True)
    tsa.set_error_byte_return(True)

    found_bool, connected_bool = tsa.autoconnect()
    if not connected_bool:
        print("Could not connect to a device. Check the cable/port and try again.")
        return

    print("Connected.")
    print(f"Device ID:   {tsa.get_device_id()}")
    print(f"Device Info: {tsa.info()}")

    # Short sweep so the demo runs quickly.
    start_freq, stop_freq, n_pts = 100e6, 500e6, 12
    tsa.pause()
    freq_vals = tsa.hop(start_freq, stop_freq, n_pts, 1)
    dbm_vals = tsa.hop(start_freq, stop_freq, n_pts, 2)

    freq_list = [float(x) for x in freq_vals.decode("utf-8").split()]
    power_list = [float(x) for x in dbm_vals.decode("utf-8").split()]
    print(f"Collected {len(freq_list)} frequency points and "
          f"{len(power_list)} power measurements.")
    print("NOTE: hop() returns one MORE point than requested -- the initial "
          "frequency point is included.")

    tsa.disconnect()
    print("Disconnected. Done.")


if __name__ == "__main__":
    walkthrough()