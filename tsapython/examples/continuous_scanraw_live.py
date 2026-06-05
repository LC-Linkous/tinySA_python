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
#   PLOTTING ARCHITECTURE:
#   Acquisition runs in a BACKGROUND THREAD and hands frames to the main thread
#   through a queue; matplotlib's FuncAnimation draws on the GUI event loop. This
#   keeps the window responsive (a tight manual loop with plt.pause() starves the
#   GUI event loop, so the window stops rendering and controls stop responding).
#   This mirrors the pattern in plotting_waterfall_realtime.py.
#
#   NOTE: the device screen does not update while scanraw runs -- scanraw is a
#   data-acquisition mode, not a display mode. A frozen device screen during this
#   example is expected, not a hang.
#
#   Close the plot window (or Ctrl+C) to stop.
#
#   NOTE: if scanning is slow, check your device's RBW setting. 'auto' works best
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
import time
import threading
import queue
# This example needs the optional plotting dependencies.
# Install them with:  pip install "tsapython[plotting]"
try:
    import numpy as np
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
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


class LiveScanrawPlotter:
    def __init__(self, tsa, start, stop, pts, unbuf=1):
        self.tsa = tsa
        self.start = start
        self.stop = stop
        self.pts = pts
        self.unbuf = unbuf
        self.freq_arr = np.linspace(start, stop, pts)
        self.data_queue = queue.Queue()
        self.running = False
        self.thread = None

    def _acquire(self):
        # background thread: loop scan_raw, decode, hand the latest frame off
        while self.running:
            try:
                frame = self.tsa.scan_raw(self.start, self.stop, self.pts, self.unbuf)
                dbm = decode_scanraw(frame, self.pts)
                if dbm is not None:
                    self.data_queue.put(dbm)
            except Exception as e:
                print(f"acquisition error: {e}")
                time.sleep(0.15)

    def start_acquisition(self):
        self.running = True
        self.thread = threading.Thread(target=self._acquire, daemon=True)
        self.thread.start()

    def stop_acquisition(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=1.0)

    def update(self, frame, line, ax):
        # main thread: drain to the most recent frame and draw it
        latest = None
        while not self.data_queue.empty():
            try:
                latest = self.data_queue.get_nowait()
            except queue.Empty:
                break
        if latest is not None:
            line.set_ydata(latest)
            ax.set_ylim(np.min(latest) - 5, np.max(latest) + 5)
        return (line,)


def main():
    tsa = tinySA()
    tsa.set_verbose(False)            # quiet: we loop a lot
    tsa.set_error_byte_return(True)

    found_bool, connected_bool = tsa.autoconnect()
    if not connected_bool:
        print("ERROR: could not connect to port")
        return

    # scan parameters
    start = int(150e6)   # 150 MHz
    stop = int(400e6)    # 400 MHz
    pts = 290            # within the device's per-sweep resolution
    unbuf = 1            # scanraw mode bit: 1 = unbuffered (single frame per call)

    plotter = LiveScanrawPlotter(tsa, start, stop, pts, unbuf)

    fig, ax = plt.subplots(figsize=(11, 6))
    (line,) = ax.plot(plotter.freq_arr / 1e9, np.full(pts, -120.0), lw=1.2)
    ax.set_xlabel("Frequency (GHz)")
    ax.set_ylabel("Power (dBm)")
    ax.set_title("tinySA continuous SCANRAW (looped) - close window to stop")
    ax.grid(True, alpha=0.3)
    ax.set_ylim(-120, 0)

    print("Live scanning. Close the plot window to stop.")
    plotter.start_acquisition()

    # FuncAnimation drives redraws on the GUI event loop, keeping the window
    # responsive. interval is the redraw period in ms; acquisition runs
    # independently in the background thread.
    ani = animation.FuncAnimation(
        fig, plotter.update, fargs=(line, ax),
        interval=200, blit=False, cache_frame_data=False)

    try:
        plt.show()   # blocks until the window is closed
    except KeyboardInterrupt:
        print("\nStopped by user.")
    finally:
        plotter.stop_acquisition()
        tsa.resume()
        tsa.disconnect()
        print("Disconnected.")


if __name__ == "__main__":
    main()