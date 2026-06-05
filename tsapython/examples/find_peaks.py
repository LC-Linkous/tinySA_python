#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/find_peaks.py'
#   Find the strongest signal(s) in a frequency range two ways:
#     1. using the device's built-in marker peak (hardware finds the peak)
#     2. computing peaks from scan data in Python (lets you find MULTIPLE peaks)
#
#   HARDWARE REQUIRED. Needs the plotting extra for the optional plot:
#       pip install "tsapython[plotting]"
#
#   Last update: 2026
##-------------------------------------------------------------------------------\

# import tinySA_python (tsapython) package
from tsapython import tinySA

# imports FOR THE EXAMPLE
# numpy is part of the plotting extra; matplotlib is only needed for the plot.
try:
    import numpy as np
except ImportError as exc:
    raise SystemExit(
        "This example requires numpy (the plotting extra). "
        'Install it with:  pip install "tsapython[plotting]"'
    ) from exc


def parse_scan_levels(data_bytes):
    # scan(outmask=2) returns newline-separated rows; the first value per row is
    # the measured level in dBm. (Also handles the ':' firmware artifact -- see
    # the colon-artifact note in the plotting examples.)
    cleaned = bytearray(data_bytes.replace(b"-:.0", b"-10.0").replace(b":.0", b"10.0"))
    levels = []
    for line in cleaned.decode("utf-8").split("\n"):
        line = line.strip()
        if line:
            levels.append(float(line.split()[0]))
    return np.array(levels)


def find_peaks_python(freqs, levels, num_peaks=3, min_separation_bins=5):
    # Simple multi-peak finder: repeatedly take the max, then blank out a window
    # around it so the next-strongest peak isn't the same signal's shoulder.
    peaks = []
    work = levels.copy()
    for _ in range(num_peaks):
        idx = int(np.argmax(work))
        peaks.append((freqs[idx], levels[idx]))
        lo = max(0, idx - min_separation_bins)
        hi = min(len(work), idx + min_separation_bins + 1)
        work[lo:hi] = -np.inf      # blank this peak's neighborhood
        if np.all(np.isneginf(work)):
            break
    return peaks


def main():
    tsa = tinySA()
    tsa.set_verbose(False)
    tsa.set_error_byte_return(True)

    found, connected = tsa.autoconnect()
    if not connected:
        print("ERROR: could not connect to port")
        return

    # scan range
    start = int(150e6)   # 150 MHz
    stop = int(500e6)    # 500 MHz
    pts = 290

    # --- 1) DEVICE marker peak: ask the hardware for the single strongest signal
    # marker 1 peak: activates marker 1 and parks it on the strongest signal,
    # then returns the marker info.
    print("Device marker peak (single strongest signal):")
    peak_info = tsa.marker_peak(1)
    print(f"  {peak_info}")

    # --- 2) PYTHON-side peaks from scan data: find the top few signals
    data_bytes = tsa.scan(start, stop, pts, 2)   # outmask 2 = measured data
    tsa.resume()
    tsa.disconnect()

    levels = parse_scan_levels(data_bytes)
    freqs = np.linspace(start, stop, len(levels))

    peaks = find_peaks_python(freqs, levels, num_peaks=3)
    print(f"\nTop {len(peaks)} peaks from scan data:")
    for i, (f, lvl) in enumerate(peaks, start=1):
        print(f"  {i}. {f/1e6:8.3f} MHz   {lvl:6.1f} dBm")

    # --- optional plot: spectrum with the peaks marked
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print('\n(install "tsapython[plotting]" to also see the plot)')
        return

    plt.figure(figsize=(11, 6))
    plt.plot(freqs / 1e6, levels, lw=1.0, label="spectrum")
    for f, lvl in peaks:
        plt.plot(f / 1e6, lvl, "rv", markersize=10)
        plt.annotate(f"{f/1e6:.2f} MHz", (f / 1e6, lvl),
                     textcoords="offset points", xytext=(0, 8),
                     ha="center", fontsize=8)
    plt.xlabel("Frequency (MHz)")
    plt.ylabel("Power (dBm)")
    plt.title("tinySA peak finding")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    main()