#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './tests/test_smoke.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Smoke tests for tsapython. Requires NO hardware.
#   Confirms the package imports, instantiates, exposes its core methods, and that
#   the library-side settings don't raise. Was previously test_basic.py (custom runner);
#   converted to standard pytest asserts.
#
#   Run with: pytest tests/test_smoke.py
#
#   Author(s): Lauren Linkous
#   Last update: June 3rd, 2026
##--------------------------------------------------------------------------------------------------\

import pytest


def test_import():
    """The package imports and exposes tinySA."""
    from tsapython import tinySA  # noqa: F401


def test_create_instance():
    """A tinySA instance can be constructed without hardware."""
    from tsapython import tinySA
    assert tinySA() is not None


# Device-agnostic methods that every model must expose. If the refactor ever
# drops or renames one of these, this test fails loudly.
REQUIRED_METHODS = [
    "autoconnect", "disconnect",
    "get_device_id", "info",
    "set_verbose", "set_error_byte_return",
    "pause", "hop",
]


@pytest.mark.parametrize("method_name", REQUIRED_METHODS)
def test_required_method_exists(tsa, method_name):
    """Each core method is present and callable on the composed class."""
    assert callable(getattr(tsa, method_name, None)), \
        f"missing required method: {method_name}"


def test_verbose_setting_round_trips(tsa):
    """Verbose toggle is a pure library-side setting: no device traffic, readable back."""
    tsa.set_verbose(True)
    assert tsa.get_verbose() is True
    tsa.set_verbose(False)
    assert tsa.get_verbose() is False
    assert tsa._recorder.count == 0


def test_error_byte_setting_round_trips(tsa):
    """Error-byte toggle decides what error_byte_return() hands back; no device traffic."""
    tsa.set_error_byte_return(True)
    assert tsa.get_error_byte_return() is True
    assert tsa.error_byte_return() == bytearray(b"ERROR")
    tsa.set_error_byte_return(False)
    assert tsa.get_error_byte_return() is False
    assert tsa.error_byte_return() == bytearray(b"")
    assert tsa._recorder.count == 0
