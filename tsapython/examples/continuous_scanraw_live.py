#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/continuous_scanraw_live.py'
#   Continuous SCANRAW by LOOPING scan_raw() and live-plotting each frame.
#
#   HOW CONTINUOUS SCANNING WORKS ON THIS DEVICE:
#   The tinySA returns exactly ONE binary frame per scanraw call (it does not
#   open an unbounded multi-frame stream over USB, even with the 'continuous'
#   bit set). So "continuous" acquisition is done by calling scan_raw() in a
#   loop -- each call returns one full frame, which we decode and plot. The
#   loop cadence is limited by the device sweep time (~150-200 ms/frame on a
#   tinySA Ultra for small point counts).
#
#   Close the plot window (or Ctrl+C) to stop.
#
#   HARDWARE REQUIRED. Needs the plotting extra:
#       pip install "tsapython[plotting]"
#
#   Last update: 2026
##-------------------------------------------------------------------------------\

# import tinySA_python (tsapython) package
from tsapython import tinySA

# imports FOR THE EXAMPLE
import struct
# This example needs the optional plotting dependencies.
# Install them with:  pip install "tsapython[plotting]"
try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "This example requires the plotting extra (numpy and matplotlib). "
        'Install it with:  pip install "tsapython[plotting]"'
    ) from exc


# tinySA Ultra and newer = 174; tinySA Basic = 128
SCALE_FACTOR = 174


def decode_scanraw(frame_bytes, pts):
    # frame_bytes is '{' + pts*( 'x' + 2-byte LE uint16 ), trailing '}' already
    # dropped by the library. Skip the leading '{', then unpack 'xH' per point.
    # 'x' = pad byte (the literal 'x' separator), 'H' = unsigned 16-bit sample.
    bin_part = frame_bytes[1:]
    if len(bin_part) != 3 * pts:
        # short/!= expected: the device frame was incomplete this iteration
        return None
    raw_vals = struct.unpack('<' + 'xH' * pts, bin_part)
    samples = np.array(raw_vals, dtype=np.uint16)
    return samples / 32 - SCALE_FACTOR     # dBm


def main():
    # create a new tinySA object
    tsa = tinySA()
    tsa.set_verbose(False)            # quiet: we loop a lot
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

    freq_arr = np.linspace(start, stop, pts)

    # set up an interactive line plot we update in place
    plt.ion()
    fig, ax = plt.subplots(figsize=(11, 6))
    (line,) = ax.plot(freq_arr / 1e9, np.full(pts, -120.0), lw=1.2)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Power (dBm)")
    ax.set_title("tinySA continuous SCANRAW (looped) - close window to stop")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-120, 0)

    print("Live scanning. Close the plot window to stop.")
    try:
        # loop until the window is closed
        while plt.fignum_exists(fig.number):
            frame = tsa.scan_raw(start, stop, pts, unbuf)
            dbm = decode_scanraw(frame, pts)
            if dbm is None:
                # incomplete frame this round; skip and try again
                continue
            line.set_ydata(dbm)
            # rescale y to the data with a little headroom
            ax.set_ylim(np.min(dbm) - 5, np.max(dbm) + 5)
            fig.canvas.draw_idle()
            plt.pause(0.01)   # let the GUI process events
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        # leave the device sweeping and release the port
        tsa.resume()
        tsa.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()