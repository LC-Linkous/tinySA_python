#! /usr/bin/python3
"""
Parsing tests against REAL device captures.

Unlike test_parsing.py (which uses README-derived samples), these run the
actual clean_return / read_until_end_marker logic against bytes captured from a
physical tinySA Ultra via collect_samples.py. They are hardware-free at run
time -- the bytes are frozen in fixtures/captured_responses.py.

If collect_samples.py has not been run, the fixture import is skipped so the
suite still passes on a machine that has never seen the device.
"""

import pytest

pytest.importorskip("tests.fixtures.captured_responses",
                    reason="run collect_samples.py to generate captured_responses.py")
try:
    from fixtures.captured_responses import CAPTURED
except ImportError:
    from .fixtures.captured_responses import CAPTURED


@pytest.fixture
def parsing_tsa():
    from tsapython import tinySA
    return tinySA()


# Every captured raw response, when run through clean_return, must reproduce the
# cleaned bytes the device produced at capture time.
@pytest.mark.parametrize("name", list(CAPTURED.keys()))
def test_clean_return_matches_device(parsing_tsa, name):
    rec = CAPTURED[name]
    if rec.get("raw") is None:
        pytest.skip(f"{name} has no raw capture")
    got = parsing_tsa.clean_return(bytearray(rec["raw"]))
    assert got == bytearray(rec["cleaned"])


# The scanraw frames are the binary { ... } payloads. Confirm the cleaned form
# starts with '{' and the raw ends with the device prompt.
@pytest.mark.parametrize("name", ["scanraw_5pts", "scanraw_15pts"])
def test_scanraw_frame_shape(name):
    rec = CAPTURED.get(name)
    if rec is None or rec.get("raw") is None:
        pytest.skip(f"{name} not captured")
    assert rec["raw"].endswith(b"ch>")
    assert rec["cleaned"].startswith(b"{")
    # 'x' separates each 16-bit sample inside the frame
    assert b"x" in rec["cleaned"]