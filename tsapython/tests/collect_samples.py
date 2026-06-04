#! /usr/bin/python3
"""
collect_samples.py  --  ONE-TIME hardware capture helper.

Run this with a tinySA plugged in to capture REAL raw device responses. It
saves them to tests/fixtures/captured_responses.py, which the parsing tests can
then use instead of (or alongside) the README-derived samples.

This is NOT a test. It's a manual data-collection utility, like your existing
test_basic.py / test_hardware.py demo scripts.

USAGE
-----
    python collect_samples.py                 # auto-detect port
    python collect_samples.py --port COM5     # explicit port (Windows)
    python collect_samples.py --port /dev/ttyACM0   # explicit (Linux/Mac)

WHAT IT CAPTURES
----------------
For each command below it records the *raw* bytes (pre-clean) AND the cleaned
bytes, so the test suite can verify clean_return against real framing. It uses
safe, read-only / non-destructive commands -- nothing that writes calibration,
resets the device, or deletes SD files.

The captures we most want (these stress the parsing logic):
  * deviceid      - short, simple frame (front-strip + ch> tail)
  * version/info  - multi-line text frame
  * vbat / status - short numeric frames
  * dac           - "usage:" + value frame
  * scan ... 1/2/3/4  - the four outmask formats (frequencies / data / both)
  * scanraw ...   - BINARY frame with the { ... } end-marker (read_until_end_marker)
  * frequencies   - list frame

If a command errors or your model doesn't support it, the script records the
error text rather than crashing, so you still get useful data.
"""

import sys
import os
import argparse
import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from tsapython import tinySA   # noqa: E402


# (label, method-name, args) -- all read-only / non-destructive.
# We call the public methods so we capture exactly what users get.
SAFE_COMMANDS = [
    ("deviceid",        "device_id",     ()),
    ("version",         "version",       ()),
    ("info",            "info",          ()),
    ("vbat",            "vbat",          ()),
    ("status",          "status",        ()),
    ("dac",             "dac",           ()),
    ("vbat_offset",     "vbat_offset",   ()),
    ("frequencies",     "frequencies",   ()),
    # scan outmask variants: small point count to keep frames short
    ("scan_mask1",      "scan",          (0, 2_000_000, 5, 1)),
    ("scan_mask2",      "scan",          (0, 2_000_000, 5, 2)),
    ("scan_mask3",      "scan",          (0, 2_000_000, 5, 3)),
    ("scan_mask4",      "scan",          (0, 2_000_000, 5, 4)),
    # scanraw: the binary { ... } frame
    ("scanraw_5pts",    "scan_raw",      (150_000_000, 200_000_000, 5, 1)),
    ("scanraw_15pts",   "scan_raw",      (150_000_000, 200_000_000, 15, 2)),
]


def capture_raw(tsa, writebyte):
    """
    Send a command and grab the RAW bytes before clean_return runs, then also
    the cleaned bytes. Mirrors tinySA_serial internals so we see both stages.
    """
    tsa.ser.reset_input_buffer()
    tsa.ser.reset_output_buffer()
    tsa.ser.write(bytes(writebyte, "utf-8"))
    raw = tsa.get_serial_return()
    cleaned = tsa.clean_return(bytearray(raw))
    return bytes(raw), bytes(cleaned)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", default=None,
                    help="serial port (e.g. COM5 or /dev/ttyACM0). "
                         "Omitted = autoconnect.")
    ap.add_argument("--out", default=os.path.join(
        os.path.dirname(__file__), "fixtures", "captured_responses.py"))
    args = ap.parse_args()

    tsa = tinySA()
    tsa.set_verbose(True)
    tsa.set_error_byte_return(True)

    # connect ---------------------------------------------------------------
    if args.port:
        ok = tsa.connect(args.port)              # connect() returns a single bool
    else:
        _found, ok = tsa.autoconnect()           # autoconnect() returns (found, connected)
    if not ok:
        print("ERROR: could not open the serial port. "
              "Pass --port explicitly, or check permissions "
              "(Linux: sudo chmod a+rw /dev/ttyACM0).")
        sys.exit(1)

    print("Connected. Capturing %d commands...\n" % len(SAFE_COMMANDS))

    records = {}
    total = len(SAFE_COMMANDS)
    for i, (label, method, cmdargs) in enumerate(SAFE_COMMANDS, start=1):
        # Show which command this iteration is testing.
        argstr = ", ".join(repr(a) for a in cmdargs) if cmdargs else ""
        print(f"[{i}/{total}] {label}: {method}({argstr})")

        # Build the exact command string the method would send, by intercepting
        # tinySA_serial, then send it ourselves to grab raw+cleaned.
        sent = {}
        real_serial = tsa.tinySA_serial

        def spy(writebyte, printBool=False, pts=None):
            sent["cmd"] = writebyte
            return bytearray(b"")
        tsa.tinySA_serial = spy
        try:
            getattr(tsa, method)(*cmdargs)
        except Exception as e:  # noqa: BLE001
            sent.setdefault("cmd", None)
            print(f"[{label}] method raised before send: {e!r}")
        finally:
            tsa.tinySA_serial = real_serial

        writebyte = sent.get("cmd")
        if not writebyte:
            print(f"[{label}] SKIPPED (no command string produced; "
                  f"likely rejected by validation on this model)")
            records[label] = {"command": None, "raw": None, "cleaned": None}
            continue

        try:
            raw, cleaned = capture_raw(tsa, writebyte)
            records[label] = {
                "command": writebyte,
                "raw": raw,
                "cleaned": cleaned,
            }
            print(f"[{label}] OK  cmd={writebyte!r}  raw={len(raw)}B")
        except Exception as e:  # noqa: BLE001
            records[label] = {"command": writebyte, "raw": None,
                              "cleaned": None, "error": repr(e)}
            print(f"[{label}] ERROR during capture: {e!r}")

    tsa.disconnect()

    # write fixtures file ---------------------------------------------------
    header = (
        "#! /usr/bin/python3\n"
        '"""\n'
        "Captured tinySA device responses -- generated by collect_samples.py.\n"
        "Generated: %s\n"
        "Do not edit by hand; re-run the collector to refresh.\n"
        '"""\n\n'
        "CAPTURED = {\n"
    ) % datetime.datetime.now().isoformat(timespec="seconds")

    lines = [header]
    for label, rec in records.items():
        lines.append("    %r: {\n" % label)
        for k in ("command", "raw", "cleaned", "error"):
            if k in rec:
                lines.append("        %r: %r,\n" % (k, rec[k]))
        lines.append("    },\n")
    lines.append("}\n")

    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w") as f:
        f.write("".join(lines))

    print(f"\nWrote {args.out}")
    print("Next: point a parsing test at fixtures.captured_responses.CAPTURED, "
          "or paste good captures into device_responses.py.")


if __name__ == "__main__":
    main()