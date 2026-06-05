# tsapython

**An Unofficial Python API for the tinySA Device Series**

[![PyPI version](https://badge.fury.io/py/tsapython.svg)](https://badge.fury.io/py/tsapython)
[![Python versions](https://img.shields.io/pypi/pyversions/tsapython.svg)](https://pypi.org/project/tsapython/)
[![PyPI - Wheel](https://img.shields.io/pypi/wheel/tsapython.svg)](https://pypi.org/project/tsapython/)
[![Downloads](https://static.pepy.tech/badge/tsapython)](https://pepy.tech/project/tsapython)
[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.20546764.svg)](https://doi.org/10.5281/zenodo.20546764)

A non-GUI Python API for the tinySA series of spectrum analyzer devices. This library provides programmatic control over tinySA devices for automated measurements, data collection, and analysis.

This repository uses official resources and documentation but is **NOT** endorsed by the official tinySA product, owner, or company. Refer to official resources and support for product information. This library was built for the official tinySA device line(s); knock-off or custom devices may not be compatible and have not been tested.

## Features

- **Device Discovery** — automatic detection and serial connection to tinySA devices
- **Frequency Sweeps** — collect data across specified frequency ranges
- **Multiple Modes** — support for both input and output modes (device dependent)
- **Data Export** — easy integration with `matplotlib` and `numpy`
- **Error Handling** — input checking and verbose output options
- **Device Control** — full programmatic control of tinySA settings and measurements

## Installation

```bash
pip install tsapython
```

The library itself depends only on `numpy` and `pyserial`. The plotting examples need an optional extra:

```bash
pip install "tsapython[plotting]"
```

## Quick Start

```python
from tsapython import tinySA

tsa = tinySA()
found, connected = tsa.autoconnect()
if connected:
    print(tsa.device_id())
    tsa.disconnect()
```

## Examples

The [main GitHub repository](https://github.com/LC-Linkous/tinySA_python) provides runnable examples, grouped by what they demonstrate.

**Getting started / device control**

- `using_autoconnect.py` — detect and connect to a tinySA, read the device ID
- `identifying_serial_ports.py` — manually identify serial ports (useful if autoconnect has trouble)
- `using_command_func.py` — send raw device commands for functionality not yet wrapped by the library
- `hardware_walkthrough.py` — a guided walkthrough of connecting and reading device info/data
- `complete_workflow.py` — end-to-end: connect, read info, collect a sweep, and plot it

**Plotting scan data**

- `plotting_scan.py` — plot a single `scan`
- `plotting_scanraw.py` — compare `scan` vs. the binary `scanraw` (with decoding to dBm)
- `plotting_waterfall_static.py` — collect several sweeps and render a static waterfall plot
- `plotting_waterfall_realtime.py` — a live, continuously updating waterfall plot

**Continuous acquisition**

- `continuous_scanraw_live.py` — loop `scan_raw` and live-plot each frame
- `continuous_scanraw_collect.py` — loop `scan_raw`, decode to dBm, and save sweeps to CSV

**Analysis**

- `find_peaks.py` — find the strongest signal(s) two ways: the device's marker peak, and a Python multi-peak finder over scan data
- `filtering_scan_artifacts.py` — show the `:` firmware artifact and compare a median filter against a moving average on one figure

**Exporting data**

- `save_scan_csv.py` — run a scan and write frequency/power pairs to a CSV file

> Most plotting examples require the optional plotting dependencies:
> `pip install "tsapython[plotting]"`

## Documentation

For comprehensive documentation, advanced examples, and troubleshooting:

- **Library GitHub repository**: [https://github.com/LC-Linkous/tinySA_python/](https://github.com/LC-Linkous/tinySA_python/)
- **Official tinySA documentation**: [https://tinysa.org/wiki/](https://tinysa.org/wiki/) (not associated with this library)

## Contributing

This is an unofficial community project. Contributions welcome!

- Report bugs and request features on [GitHub](https://github.com/LC-Linkous/tinySA_python)
- For device information and OFFICIAL resources, see the official tinySA community at [https://groups.io/g/tinysa](https://groups.io/g/tinysa)
  - Please do **NOT** request features or report bugs on the official community! This is an unofficial project and they do not maintain it.

## Citing

If you use this library in your work, citation details are in the repository's `CITATION.cff`, or use the Zenodo DOI: [10.5281/zenodo.20546764](https://doi.org/10.5281/zenodo.20546764).

## License

GPL-2.0 — this is unofficial software with no warranty, offered AS-IS. Use at your own risk.

The licensing of this software does NOT take priority over the official releases and the decisions of the official tinySA team. This licensing does NOT take priority for any of their products, including the devices that can be used with this software.

## Acknowledgments

- The tinySA device creators and community, who have created an awesome device
- Official tinySA documentation and resources, especially [www.tinysa.org/wiki/](https://www.tinysa.org/wiki/)
- All contributors to this library, including those who have contributed code and reached out with questions

---

**Disclaimer**: This software is unofficial and not supported by the tinySA team. For official software and support, visit [tinysa.org](https://tinysa.org). The tinySA team does not offer tech support for this software, does not maintain it, and has no responsibility for any of the contents.