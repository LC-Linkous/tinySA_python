# tsapython

**An Unofficial Python API for the tinySA Device Series**

A Non-GUI Python API for the tinySA series of spectrum analyzer devices. This library provides programmatic control over tinySA devices for automated measurements, data collection, and analysis.

[![PyPI version](https://badge.fury.io/py/tsapython.svg)](https://badge.fury.io/py/tsapython)
[![License: GPL v2](https://img.shields.io/badge/License-GPL_v2-blue.svg)](https://www.gnu.org/licenses/old-licenses/gpl-2.0.en.html)

> **Note**: This repository uses official resources and documentation but is NOT endorsed by the official tinySA product, owner, or company. Refer to official resources and support for product information.

## Quick Start

### Installation

```bash
pip install tsapython
```

### Basic Usage

```python
from tsapython import TinySA

# Create and connect to device
tsa = TinySA()
tsa.set_verbose(True)
tsa.set_error_byte_return(True)

# Attempt to connect
found, connected = tsa.autoconnect()

if connected:
    print("Device connected!")
    
    # Get device info
    device_id = tsa.get_device_id()
    print(f"Device ID: {device_id}")
    
    # Collect frequency sweep data
    start_freq = 100e6  # 100 MHz
    stop_freq = 500e6   # 500 MHz
    n_pts = 101
    
    tsa.pause()
    freq_vals = tsa.hop(start_freq, stop_freq, n_pts, 1)  # Get frequencies
    power_vals = tsa.hop(start_freq, stop_freq, n_pts, 2)  # Get power data
    
    tsa.disconnect()
    print("Data collection complete!")
else:
    print("Could not connect to device")
```

### Plotting Example

```python
import matplotlib.pyplot as plt

# Convert data for plotting
x_val = [float(x) for x in freq_vals.decode('utf-8').split()]
y_val = [float(x) for x in power_vals.decode('utf-8').split()]

# Create plot
plt.plot(x_val, y_val)
plt.xlabel("Frequency (Hz)")
plt.ylabel("Power (dBm)")
plt.title("tinySA Frequency Sweep")
plt.show()
```

### Full Code Examples:

Examples are provided for all of the following:

* Direct device interfacing and control
* Realtime and static waterfall plots
* Exporting data to CSV files
* Plotting live scan data

## Features

- **Device Discovery**: Automatic detection and connection to tinySA devices
- **Frequency Sweeps**: Collect data across specified frequency ranges
- **Multiple Modes**: Support for both input and output modes
- **Data Export**: Easy integration with matplotlib, pandas, and numpy
- **Error Handling**: Error checking and verbose output options
- **Device Control**: Full programmatic control of tinySA settings and measurements

## Supported Devices

- tinySA Basic
- tinySA Ultra  
- (other devices pending testing)

## Core Functions
Sample functions for device operation. See [GitHub]( https://github.com/LC-Linkous/tinySA_python) for more examples.
### Connection Management
- `autoconnect()` - Automatic device discovery and connection
- `disconnect()` - Clean disconnection from device

### Data Collection
- `hop(start, stop, points, outmask)` - Collect measurement data over frequency range
- `scan(start, stop, points, outmask)` - Perform frequency scans
- `data()` - Get trace data from device screen
- `capture()` - Requests a screen dump to be sent in binary format of HEIGHTxWIDTH pixels of each 2 bytes

### Device Control
- `pause()` / `resume()` - Control measurement sweeps
- `set_marker_color(ID, RGB24color)` - Sets colors of traces
- `marker_on(ID)` / marker_off(ID)` - Turn marker on or off
- `restart_device()` - reset the device

### Configuration
- `set_verbose(enabled)` - Enable/disable detailed output
- `get_device_id()` / `set_device_id(id)` - Device identification
- `info()` - Get device firmware and hardware information

## Requirements

- Python 3.8+
- numpy
- pandas  
- matplotlib

## Documentation & Examples

For comprehensive documentation, advanced examples, and troubleshooting:

- **GitHub Repository**: [https://github.com/yourusername/tsapython](https://github.com/yourusername/tsapython)
- **Official tinySA Documentation**: [https://tinysa.org/wiki/](https://tinysa.org/wiki/)

## Device Connection Tips

1. **Windows**: Check Device Manager for COM port
2. **Linux**: Look for `/dev/ttyACM0` or similar, may need permissions: `sudo chmod a+rw /dev/ttyACM0`
3. **Multiple Devices**: Library will connect to first device found

## Error Handling

```python
try:
    found, connected = tsa.autoconnect()
    if not connected:
        print("No device found")
        return
        
    # Your measurement code here
    
except Exception as e:
    print(f"Error: {e}")
finally:
    tsa.disconnect()
```

## Contributing

This is an unofficial community project. Contributions welcome!

- Report bugs and request features on [GitHub]( https://github.com/LC-Linkous/tinySA_python)
- Check the official tinySA community at [https://groups.io/g/tinysa](https://groups.io/g/tinysa)
 - Please do NOT request features or report bugs on the official community! This is an unofficial project and they do not maintain it.

## License

GPL-2.0 - This is unofficial software with no warranty, offered AS-IS. Use at your own risk.

The licensing of this software does NOT take priority over the official releases and the decisions of the official tinySA team. This licensing does NOT take priority for any of their products, including the devices that can be used with this software.


## Acknowledgments

- tinySA device creators and community, who have created an awesome device
- Official tinySA documentation and resources, especially www.tinysa.org/wiki/
- All contributors to this library, including those who have contributed code and reached out with questions.

---

**Disclaimer**: This software is unofficial and not supported by the tinySA team. For official software and support, visit [tinysa.org](https://tinysa.org). The tinySA team does not offer tech support for this software, does not maintain it, and has no responsibility for any of the contents. 

