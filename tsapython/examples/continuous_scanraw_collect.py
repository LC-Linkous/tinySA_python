#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/continuous_scanraw_collect.py'
#   Continuous SCANRAW by LOOPING scan_raw() a fixed number of times, decoding
#   each frame to dBm, and saving all sweeps to a CSV (one row per sweep).
#
#   HOW CONTINUOUS SCANNING WORKS ON THIS DEVICE:
#   The tinySA returns exactly ONE binary frame per scanraw call (it does not
#   open an unbounded multi-frame stream over USB). So we acquire a series of
#   sweeps by calling scan_raw() in a loop -- each call returns one full frame.
#   This is the data-capture counterpart to continuous_scanraw_live.py (which
#   plots instead of saving).
#
#   HARDWARE REQUIRED. Needs the plotting extra (for numpy):
#       pip install "tsapython[plotting]"
#
#   Last update: 2026
##-------------------------------------------------------------------------------\

# import tinySA_python (tsapython) package
from tsapython import tinySA

# imports FOR THE EXAMPLE
import csv
import struct
from datetime import datetime
# This example needs numpy (part of the plotting extra).
# Install it with:  pip install "tsapython[plotting]"
try:
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "This example requires numpy (the plotting extra). "
        'Install it with:  pip install "tsapython[plotting]"'
    ) from exc


# tinySA Ultra and newer = 174; tinySA Basic = 128
SCALE_FACTOR = 174


def decode_scanraw(frame_bytes, pts):
    # frame_bytes is '{' + pts*( 'x' + 2-byte LE uint16 ); trailing '}' already
    # dropped by the library. Skip the '{', unpack 'xH' per point ('x' pad byte,
    # 'H' unsigned 16-bit sample), then convert to dBm.
    bin_part = frame_bytes[1:]
    if len(bin_part) != 3 * pts:
        return None
    raw_vals = struct.unpack('<' + 'xH' * pts, bin_part)
    samples = np.array(raw_vals, dtype=np.uint16)
    return samples / 32 - SCALE_FACTOR


def main():
    tsa = tinySA()
    tsa.set_verbose(False)
    tsa.set_error_byte_return(True)

    found_bool, connected_bool = tsa.autoconnect()
    if not connected_bool:
        print("ERROR: could not connect to port")
        return

    # scan parameters
    start = int(150e6)   # 150 MHz
    stop = int(500e6)    # 500 MHz
    pts = 290            # within the device's per-sweep resolution
    unbuf = 1            # scanraw mode bit: 1 = unbuffered (single frame per call)

    num_sweeps = 20      # how many sweeps to collect

    freq_arr = np.linspace(start, stop, pts)
    sweeps = []          # list of (timestamp, dbm_array)

    print(f"Collecting {num_sweeps} sweeps ({pts} pts each)...")
    collected = 0
    attempts = 0
    while collected < num_sweeps and attempts < num_sweeps * 3:
        attempts += 1
        frame = tsa.scan_raw(start, stop, pts, unbuf)
        dbm = decode_scanraw(frame, pts)
        if dbm is None:
            # incomplete frame; retry without counting it
            continue
        sweeps.append((datetime.now(), dbm))
        collected += 1
        print(f"  sweep {collected}/{num_sweeps}")

    # done acquiring; leave device sweeping and release the port
    tsa.resume()
    tsa.disconnect()

    if not sweeps:
        print("No complete sweeps collected.")
        return

    # write CSV: one row per sweep. Columns: sweep#, timestamp, then one column
    # per frequency bin (header is the frequency in Hz).
    filename = "continuous_scanraw.csv"
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Sweep", "Timestamp"] + [f"{hz:.0f}" for hz in freq_arr])
        for i, (ts, dbm) in enumerate(sweeps, start=1):
            writer.writerow([i, ts.strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]] + dbm.tolist())

    print(f"Saved {len(sweeps)} sweeps x {pts} points to {filename}")


if __name__ == "__main__":
    main()