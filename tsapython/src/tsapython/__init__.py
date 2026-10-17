"""
tsapython - Unofficial Python package for tinySA spectrum analyzer
"""

from importlib.metadata import PackageNotFoundError, version as _package_version

try:
    # single source of truth: the version in pyproject.toml
    __version__ = _package_version("tsapython")
except PackageNotFoundError:  # running from a source tree that was never installed
    __version__ = "unknown"

# In __init__.py
from .core import tinySA

__all__ = ["tinySA"]
