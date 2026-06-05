#! /usr/bin/python3

##-------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './examples/filtering_scan_artifacts.py'
#   Demonstrates the ':' firmware artifact in scan data and compares filtering
#   approaches for cleaning it, all plotted on ONE figure for comparison.
#
#   BACKGROUND -- the ':' artifact:
#   On some firmware builds, SCAN/SWEEP data occasionally contains malformed
#   values like ":.000000e-01" or "-:.000000e+01". The ':' is ASCII 0x3A, one
#   past '9' (0x39): the firmware overflows a single digit slot, so a value that
#   should read "10" renders as ":". The standard handling (used in the plotting
#   examples) replaces the ':' form with 10:
#       data.replace(b"-:.0", b"-10.0").replace(b":.0", b"10.0")
#   That keeps the data parseable, but the substituted points land near the
#   noise floor and show up as sharp downward SPIKES in the trace. This example
#   shows those spikes and two ways to filter them.
#
#   FILTERS COMPARED:
#     * Median filter   -- removes isolated spikes cleanly (right tool here).
#     * Moving average  -- smooths, but SMEARS spikes into neighbors (shown as a
#                          cautionary contrast, not a recommendation).
#   Both are implemented in pure numpy (no scipy dependency).
#
#   HARDWARE REQUIRED. Needs the plotting extra:
#       pip install "tsapython[plotting]"
#
#   Last update: 2026
##-------------------------------------------------------------------------------\

# import tinySA_python (tsapython) package
from tsapython import tinySA

# imports FOR THE EXAMPLE
try:
    import numpy as np
    import matplotlib.pyplot as plt
except ImportError as exc:
    raise SystemExit(
        "This example requires the plotting extra (numpy and matplotlib). "
        'Install it with:  pip install "tsapython[plotting]"'
    ) from exc


def parse_scan_levels(data_bytes, fix_artifact=True):
    # Parse scan(outmask=2) output to an array of dBm levels.
    # If fix_artifact is True, apply the standard ':' -> 10 substitution so the
    # data is parseable. (With it False, the malformed rows would raise on
    # float() -- shown here only to explain why the fix exists.)
    raw = bytes(data_bytes)
    if fix_artifact:
        raw = raw.replace(b"-:.0", b"-10.0").replace(b":.0", b"10.0")
    levels = []
    for line in bytearray(raw).decode("utf-8").split("\n"):
        line = line.strip()
        if line:
            levels.append(float(line.split()[0]))
    return np.array(levels)


def median_filter(x, k=5):
    # Pure-numpy median filter. k is forced odd. Edge-padded so length is kept.
    if k % 2 == 0:
        k += 1
    pad = k // 2
    xp = np.pad(x, pad, mode="edge")
    return np.array([np.median(xp[i:i + k]) for i in range(len(x))])


def moving_average(x, k=5):
    # Pure-numpy moving average. k is forced odd. Edge-padded so length is kept.
    if k % 2 == 0:
        k += 1
    pad = k // 2
    xp = np.pad(x, pad, mode="edge")
    return np.convolve(xp, np.ones(k) / k, mode="valid")


def main():
    tsa = tinySA()
    tsa.set_verbose(False)
    tsa.set_error_byte_return(True)

    found, connected = tsa.autoconnect()
    if not connected:
        print("ERROR: could not connect to port")
        return

    start = int(1e9)     # 1 GHz
    stop = int(3e9)      # 3 GHz
    pts = 450

    data_bytes = tsa.scan(start, stop, pts, 2)   # outmask 2 = measured data
    tsa.resume()
    tsa.disconnect()

    raw_levels = parse_scan_levels(data_bytes, fix_artifact=True)
    freqs = np.linspace(start, stop, len(raw_levels))

    # apply the two filters
    med = median_filter(raw_levels, k=5)
    avg = moving_average(raw_levels, k=5)

    # report how many artifact-substituted points there were (points sitting at
    # the -10 substitution value are the likely artifacts)
    n_artifacts = int(np.sum(np.isclose(raw_levels, -10.0)))
    print(f"Scanned {len(raw_levels)} points; "
          f"{n_artifacts} look like ':'-artifact substitutions (~-10 dBm).")

    # plot all three on one figure
    plt.figure(figsize=(12, 7))
    plt.plot(freqs / 1e9, raw_levels, lw=0.8, alpha=0.6,
             label="raw (artifact-substituted, spikes visible)")
    plt.plot(freqs / 1e9, med, lw=1.3,
             label="median filter k=5 (removes spikes)")
    plt.plot(freqs / 1e9, avg, lw=1.3, alpha=0.8,
             label="moving average k=5 (smears spikes -- cautionary)")
    plt.xlabel("Frequency (GHz)")
    plt.ylabel("Power (dBm)")
    plt.title("tinySA scan: ':' artifact and filtering comparison")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()


if __name__ == "__main__":
    main()