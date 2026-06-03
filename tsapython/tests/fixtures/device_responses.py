#! /usr/bin/python3
"""
Canned device responses for parsing tests.

This matches the project README's documented "Example Return" captures. Each
entry pairs the RAW bytes the device emits with the CLEANED bytes the library
should produce (where the README documents both).

When you collect fresh samples from hardware (see tests/collect_samples.py),
append/replace entries here. Keep raw captures as exact bytes literals.

This can be adapted for other devices in the product line, but it does not mean
that the other tests will run correctly.

Last update: June 3rd, 2026
"""

RESPONSES = {
    # From README "Serial Message Return Format": the canonical clean example.
    "deviceid": {
        "raw": b"deviceid\r\ndeviceid 0\r\nch>",
        "cleaned": b"deviceid 0\r",
    },

    # scanraw 15 pts: full raw frame (README "scanraw" example).
    # Begins with the echoed command, payload is delimited by { ... }, ends ch>.
    "scanraw_15pts_raw": {
        "raw": (
            b"scanraw 150000000 200000000 15 2\r\n"
            b"{x\"\nx3\nx4\nx\x15\nx6\nx\x07\nx)\nxj\nx\xfb\txm\nx]\nxO\nxp\nx\xb2\x0bx3\x0c}ch>"
        ),
        # cleaned form not documented for this exact frame; parsing test focuses
        # on the marker extraction rather than a fixed cleaned target.
    },

    # scanraw 5 pts (README): documented cleaned result.
    "scanraw_5pts": {
        "cleaned": b"{xS\nxd\nx\x98\nx]\nx\x02\x0c",
    },

    # scan outmask examples (README "scan"): cleaned bytearrays.
    "scan_0_2e6_5_1": {
        "cleaned": b"0 \r\n1 \r\n1 \r\n2 \r\n2 \r",
    },
    "scan_0_2e6_5_2": {
        "cleaned": (
            b"5.843750e+00 0.000000000 \r\n5.343750e+00 0.000000000 \r\n"
            b"4.843750e+00 0.000000000 \r\n4.843750e+00 0.000000000 \r\n"
            b"4.843750e+00 0.000000000 \r"
        ),
    },

    # vbat_offset (README): "0 ppb\r"
    "vbat_offset": {
        "cleaned": b"0 ppb\r",
    },

    # dac (README): usage + current value
    "dac": {
        "cleaned": b"usage: dac {value(0-4095)}\r\ncurrent value: 1922\r",
    },
}