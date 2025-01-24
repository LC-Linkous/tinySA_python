
# TinySA_Python
A Non-GUI Python API class for the Tiny SA Ultra written to support several personal projects

This uses official resources and documentation but is NOT endorsed by the official tinySA product

# INPROGRESS

## Table of Contents
* [The tinySA Ultra](#the-tinysa-ultra)
* [Requirements](#requirements)
* [Usage](#usage)
* [Error Handling](#error-handling)
* [Example Implementations](#example-implementations)
    * [Opening Serial Port](#opening-serial-port)
    * [Getting Device Info](#getting-device-info)
    * [Setting tinySA Ultra Parameters](#setting-tinysa-ultra-parameters)
    * [Getting Data from Active Screen](#getting-data-from-active-screen)
    * [Plotting Data with Matplotlib](#plotting-data-with-matplotlib)
    * [Realtime Graphing](#realtime-graphing)
    * [Saving Screen Images](#saving-screen-image)
    * [Saving Data to CSV](#saving-data-to-csv)
* [List of tinySA Commands and Their Library Commands](#list-of-tinysa-commands-and-their-library-commands)
* [List of All Library Commands](#list-of-all-library-commands)
* [Table of Command and Device Compatibility](#table-of-command-and-device-compatibility)
* [Notes for Beginners](#notes-for-beginners)
    * [Vocab Check](#vocab-check)
    * [Calibration Setup](#calibration-setup)
* [References](#references)
* [Publications and Integration](#publications-and-integration)
* [Licensing](#licensing)  

## The tinySA Ultra


## Requirements

This project requires numpy and pyserial. 

Use 'pip install -r requirements.txt' to install the following dependencies:

```python
pyserial
numpy

```

These dependencies cover only the API. Additional dependencies should be installed to follow the included examples and tests. These can be installed with 'pip install -r test_requirements.txt':

```python

```

## Library Usage

This library is currently only available as the tinySA class in 'tinySA_python.py' in this repository. It is very much under development and missing error checking and handling. 

Several usage examples are provided in the [Example Implementations](#example-implementations) section, including working with the hardware and plotting results with matplotlib. 




## Error Handling

Some error handling has been implemented for the individual functions. Most functions have a list of acceptable formats for input, which is included in the documentation and the 'libraryHelp' function. The 'tinySAHelp' function will get output from the current version of firmware running on the connected tinySA device.

Detailed error messages can be returned by toggling 'verbose' on.

From the [official wiki USB Interface page](https://tinysa-org.translate.goog/wiki/pmwiki.php?n=Main.USBInterface&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US):

    There is limited error checking against incorrect parameters of incorrect mode

    * Frequencies can be specified using an integer optionally postfixed with a the letter 'k' for kilo 'M' for Mega or 'G' for Giga. E.g. 0.1M (100kHz), 500k (0.5MHz) or 12000000 (12MHz)
    * Levels are specified in dB(m) and can be specified using a floating point notation. E.g. 10 or 2.5
    * Time is specified in seconds optionally postfixed with the letters 'm' for mili or 'u' for micro. E.g. 1 (1 second), 2.5 (2.5 seconds), 120m (120 milliseconds)


## Example Implementations

This library has been tested on Windows, but not yet on Unix systems. The primary difference should be the format of the serial port connection, but there may be smaller bugs in format that have not been detected yet. 

### Finding the Serial Port

There are several ways to list avilable serial ports.


#### Windows:
1)  Open _Device Manager_, scroll down to _Ports (COM & LPT)_, and epand the menu. There should be a _COM#_ port listing "USB Serial Device(COM #)". If your tinySA Ultra is set up to work with Serial, this will be it.


2) This uses the pyserial library requirement  already installed for this library. It probably also works on Linux systems, but has not been tested yet.

```python

import serial.tools.list_ports

ports = serial.tools.list_ports.comports()

for port, desc, hwid in ports:
    print(f"Port: {port}, Description: {desc}, Hardware ID: {hwid}")

```

Example output for this method (on Windows) is as follows:

```python

Port: COM4, Description: Standard Serial over Bluetooth link (COM4), Hardware ID: BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0000\7&D0D1EE&0&000000000000_00000000
Port: COM3, Description: Standard Serial over Bluetooth link (COM3), Hardware ID: BTHENUM\{00001101-0000-1000-8000-00805F9B34FB}_LOCALMFG&0002\7&D0D1EE&0&B8B3DC31CBA8_C00000000
Port: COM10, Description: USB Serial Device (COM10), Hardware ID: USB VID:PID=0483:5740 SER=400 LOCATION=1-3

```

"COM10" is the port location of the tinySA Ultra that is used in the examples in this README.




#### Linux

```python
TODO
```




### Serial Message Return Format

This library returns strings as cleaned bytearrays. The command and first `\r\n` pair are removed from the front, and the `ch>` is removed from the en of thetinySA serial return.

The original message format:

```python
bytearray(b'deviceid\r\ndeviceid 0\r\nch>')
```

Cleaned version:

```python
bytearray(b'deviceid 0\r')
```


### Connecting and Disconnecting
 Show the process for initializing, opening the serial port, getting device info, and disconnecting

```python

# import the library class
from src.tinySA_python import tinySA

# create a new tinySA object    
tsa = tinySA()

# attempt to connect to previously discovered serial port
success = tsa.connect(port='COM10')

# if port open, then get device information and disconnect
if success == False:
    print("ERROR: could not connect to port")
else:
    msg = tsa.info()
    print(msg)
    tsa.disconnect()

```
Example output for this method is as follows:

```python

bytearray(b'tinySA ULTRA\r\n2019-2024 Copyright @Erik Kaashoek\r\n2016-2020 Copyright @edy555\r\nSW licensed under GPL. See: https://github.com/erikkaashoek/tinySA\r\nVersion: tinySA4_v1.4-143-g864bb27\r\nBuild Time: Jan 10 2024 - 11:14:08\r\nKernel: 4.0.0\r\nCompiler: GCC 7.2.1 20170904 (release) [ARM/embedded-7-branch revision 255204]\r\nArchitecture: ARMv7E-M Core Variant: Cortex-M4F\r\nPort Info: Advanced kernel mode\r\nPlatform: STM32F303xC Analog & DSP\r')

```




### Toggle Error Messages

Currently, the following can be used to turn on or off returned error messages.


1) the 'verbose' option. When enabled, detailed messages are printed out. 

```python
# detailed messages are ON
tsa.setVerbose(True) 

# detailed messages are OFF
tsa.setVerbose(False) 
```

1) the 'errorByte' option. When enabled, if there is an error with the command or configuration, `b'ERROR'` is returned instead of the default `b''`. 

```python
# when an error occurs, b'ERROR' is returned
tsa.setErrorByteReturn(True) 

# when an error occurs, the default b'' might be returned
tsa.setErrorByteReturn(False) 
```

### Device and Library Help

There are three options for help() with this library.

```python
# the default help function
# 1 = help for this library, other values call the tinySA help function 
tsa.help(1)

# calling the library help function directly
tsa.libraryHelp()

# calling the tinySA help directly
tsa.tinySAHelp()

```

All three return a bytearray in the format `bytearray(b'commands:......')`


### Setting tinySA Ultra Parameters
TODO when error checking is complete to show multiple examples

```python

```
### Getting Data from Active Screen

See other sections for the following examples:
* [Saving Screen Images](#saving-screen-images)
* [Plotting Data with Matplotlib](#plotting-data-with-matplotlib)

This example shows several examples for common data requests:

```python

# import the library class for the tinySA
from src.tinySA_python import tinySA

# create a new tinySA object    
tsa = tinySA()
# attempt to connect to previously discovered serial port
success = tsa.connect(port='COM10')

# if port open, then complete task(s) and disconnect
if success == False:
    print("ERROR: could not connect to port")
else:
    #detailed messages
    tsa.setVerbose(True) #detailed messages

    # get current trace data on screen
    msg = tsa.data(val=2) 
    print(msg)

    # set current device ID
    msg = tsa.deviceid(3) 
    print(msg)

    # get current device ID
    msg = tsa.deviceid() 
    print(msg)
    
    # get device information
    msg = tsa.info() 
    print(msg)

    # pause sweeping
    msg = tsa.pause() 
    print(msg)

    # resume sweeping
    msg = tsa.resume() 
    print(msg)

    # get current battery voltage (mV)
    msg = tsa.vbat() 
    print(msg)

    tsa.disconnect()

```



### Saving Screen Images
 
 The `capture()` function can be used to capture the screen and output it to an image file. Note that the screen size varies by device, and the serial read

 This example trunactes the last hex value, so a single padding `x00` value has been added. This will eventually be investigated, but it's not hurting the output right now.


```python
# import the library class for the tinySA
from src.tinySA_python import tinySA

# imports FOR THE EXAMPLE
import numpy as np
from PIL import Image
import struct

def convert_data_to_image(data_bytes, width, height):
    # this is not a particularly pretty example, and the data_bytes is sometimes a byte short (TODO:fix)

    # calculate the expected data size
    expected_size = width * height * 2  # 16 bits per pixel (RGB565), 2 bytes per pixel

    # error checking - brute force, but fine while developing
    if len(data_bytes) < expected_size:
        print(f"Data size is too small. Expected {expected_size} bytes, got {len(data_bytes)} bytes.")
        
        # if the data size is off by 1 byte, add a padding byte
        if len(data_bytes) == expected_size - 1:
            print("Data size is 1 byte smaller than expected. Adding 1 byte of padding.")
             # add a padding byte (0x00) to make the size match
            data_bytes.append(0) 
        else:
            return

    elif len(data_bytes) > expected_size:
        # truncate the data to the expected size (in case it's larger than needed)
        data_bytes = data_bytes[:expected_size]
        print("Data is larger than the expected size. trunacting. check data.")

    # unpack the byte array to get pixel values (RGB565 format)
    num_pixels = width * height
    # unpacking as unsigned shorts (2 bytes each)
    x = struct.unpack(f">{num_pixels}H", data_bytes)  

    # convert the RGB565 to RGBA
    arr = np.array(x, dtype=np.uint32)
    arr = 0xFF000000 + ((arr & 0xF800) >> 8) + ((arr & 0x07E0) << 5) + ((arr & 0x001F) << 19)

    # reshape array to match the image dimensions. (height, width) format
    arr = arr.reshape((height, width)) 

    # create the image
    img = Image.frombuffer('RGBA', (width, height), arr.tobytes(), 'raw', 'RGBA', 0, 1)

    # save the image
    img.save("capture_example.png")

    # show the image
    img.show()

# create a new tinySA object    
tsa = tinySA()
# attempt to connect to previously discovered serial port
success = tsa.connect(port='COM10')

# if port closed, then return error message
if success == False:
    print("ERROR: could not connect to port")
else: # port open, complete task(s) and disconnect
    # detailed messages turned on
    tsa.setVerbose(True) 
    # get the trace data
    data_bytes = tsa.capture() 
    print(data_bytes)
    tsa.disconnect()

    # processing after disconnect (just for this example)
    # test with 480x320 resolution for tinySA Ultra
    convert_data_to_image(data_bytes, 480, 320)

```


<p align="center">
        <img src="media/capture_example.png" alt="Capture of On-screen Trace Data" height="350">
</p>
   <p align="center">Capture On-Screen Trace Data of a Frequency Sweep from 100 kHz to 800 kHz</p>



### Plotting Data with Matplotlib

This example plots the last/current sweep of data from the tinySA device. 
`data()` gets the trace data. `frequencies()` gets the frequency values used. 
`byteArrayToNumArray(byteArr)` takes in the returned trace data and frequency 
bytearrays and converts them to arrays that are then plotted using `matplotlib`


```python
# import the library class for the tinySA
from src.tinySA_python import tinySA

# import matplotlib FOR THE EXAMPLE
import matplotlib.pyplot as plt


# functions used in this example
def byteArrayToNumArray(byteArr, enc="utf-8"):
    # decode the bytearray to a string
    decodedStr = byteArr.decode(enc)
    # split the string by newline characters
    stringVals = decodedStr.splitlines()
    # convert each value to a float
    floatVals = [float(val) for val in stringVals]
    return floatVals

# create a new tinySA object    
tsa = tinySA()
# attempt to connect to previously discovered serial port
success = tsa.connect(port='COM10')

# if port closed, then return error message
if success == False:
    print("ERROR: could not connect to port")
else: # port open, complete task(s) and disconnect
    # detailed messages turned on
    tsa.setVerbose(True) 
    # get the trace data
    data_bytes = tsa.data() 
    print(data_bytes)
    # get the frequencies used by the last sweep
    freq_bytes = tsa.frequencies() 
    tsa.disconnect()

    # processing after disconnect (just for this example)
    dataVals = byteArrayToNumArray(data_bytes)
    print(len(dataVals))  # length of 450 data points

    freqVals = byteArrayToNumArray(freq_bytes)
    print(len(freqVals))  # length of 450 data points


    # create the plot
    plt.plot(freqVals, dataVals)

    # add labels and title
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Signal Strength (dB)')
    plt.title('Plot of Last Data Sweep')

    # show the plot
    plt.show()


```


<p align="center">
        <img src="media/example_plot_SA_data.png" alt="Plot of On-screen Trace Data" height="350">
</p>
   <p align="center">Plotted On-Screen Trace Data of a Frequency Sweep from 100 kHz to 800 kHz</p>



## List of tinySA Ultra Commands and their Library Commands

This list and the following list in the [Additional Library Commands](#additional-library-commands) section describe the functions in this library.

This section is sorted by the tinySA (Ultra) commands, and includes:
* A brief description of what the command does
* What the original usage looked like
* The tinySA_Python function call, or calls if multiple options exist 
* Example return, or example format of return
* Any additional notes about the usage

All of the listed commands are included in this API to some degree, but error checking may be incomplete.

Quick Link Table:
|  |   |     |   |       |      |      |
|-------|-------|-------|-------|-------|-------|-------|
| [abort](#abort)   | [actual_freq](#actual_freq)  | [agc](#agc)      | [attenuate](#attenuate)  | [bulk](#bulk)       | [calc](#calc)        | [caloutput](#caloutput) |
| [capture](#capture) | [clearconfig](#clearconfig) | [color](#color)   | [correction](#correction) | [dac](#dac)        | [data](#data)        | [deviceid](#deviceid)  |
| [direct](#direct) | [ext_gain](#ext_gain)    | [fill](#fill)       | [freq](#freq)        | [freq_corr](#freq_corr) | [frequencies](#frequencies) | [help](#help)  |
| [hop](#hop)            | [if](#if)           | [if1](#if1)          | [info](#info)     | [level](#level)             | [levelchange](#levelchange) | [leveloffset](#leveloffset) |
| [line](#line) | [load](#load)   | [lna](#lna)          | [lna2](#lna2)     | [marker](#marker)           | [menu](#menu)     | [mode](#mode)           |
| [modulation](#modulation) | [output](#output)  | [pause](#pause)   | [rbw](#rbw)                 | [recall](#recall) | [refresh](#refresh)     | [release](#release) |
| [remark](#remark)    | [repeat](#repeat) | [reset](#reset)             | [restart](#restart) | [resume](#resume)      | [save](#save)       | [saveconfig](#saveconfig) |
| [scan](#scan)     | [scanraw](#scanraw)         | [sd_delete](#sd_delete) | [sd_list](#sd_list)   | [sd_read](#sd_read) | [selftest](#selftest) | [spur](#spur)     |
| [status](#status)           | [sweep](#sweep)   | [sweeptime](#sweeptime) | [sweep_voltage](#sweep_voltage) | [text](#text)   | [threads](#threads) | [touch](#touch)             |
| [touchcal](#touchcal) | [touchtest](#touchtest) | [trace](#trace)     | [trigger](#trigger)  | [ultra](#ultra)   | [usart_cfg](#usart_cfg)     | [vbat](#vbat)     |
| [vbat_offset](#vbat_offset) | [version](#version) | [wait](#wait)        | [zero](#zero)     |                         |                     |                      |


### **abort**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**  Sets the abortion enabled status (on/off) or aborts the previous command.
* **Original Usage:** `abort [off|on]`
* **Library Function Call:** `abort(val=None|"off"|"on")` 
* **Example Return:** ????
* **Notes:** When used without parameters the previous command still running will be aborted. Abort must be enabled before usage using the "abort on" command. Additional error checking has been added with the 'verbose' option. 


### **actual_freq**
* **Status:** Getting works, setting does not.
* **Description:**  Gets the frequency correction set by CORRECT FREQUENCY menu in the expert menu settings
* **Original Usage:** `actual_freq [{frequency in Hz}]`
* **Library Function Call:** `actual_freq(val=None|Int)`
* **Example Return:** 3000000000
* **Notes:**  freq in Hz going by the returns. Should be able to set the value with this, according to documentation, but its probably a format issue in the library.


### **agc**
* **Status:** Done
* **Description:**  Enables/disables the build in Automatic Gain Control
* **Original Usage:** `agc 0..7|auto`
* **Library Function Call:** `agc(val="auto"|0..7)`
* **Example Return:** no return
* **Notes:**


### **attenuate**
* **Status:** Done
* **Description:** Sets the internal attenuation
* **Original Usage:** `attenuate [auto|0-31]`
* **Library Function Call:** `attenuate(val="auto"|0..31)`
* **Example Return:** no return
* **Notes:**


### **bulk**
* **Status:** Needs more work before this is a stand alone func. 
* **Description:** Sent by tinySA when in auto refresh mode
* **Original Usage:** `????`
* **Library Function Call:** `bulk()`
* **Example Return:** `format: "bulk\r\n{X}{Y}{Width}{Height} {Pixeldata}\r\n"`
* **Notes:** where all numbers are binary coded 2 bytes little endian. The pixeldata is encoded as 2 bytes per pixel           
            

### **calc**
* **Status:** Done
* **Description:** Sets or cancels one of the measurement modes
* **Original Usage:** `calc off|minh|maxh|maxd|aver4|aver16|quasip`
* **Library Function Call:** `calc(val="off"|"minh"|"maxh"|"maxd"|"aver4"|"aver16"|"quasip")`
* **Example Return:** no return
* **Notes:** 
  * the commands are the same as those listed in the MEASURE menu
  * [tinySA Calc Menu](#https://tinysa.org/wiki/pmwiki.php?n=Main.CALC):
    * OFF disables any calculation 
    * MIN HOLD sets the display to hold the minimum value measured. Reset the hold by selecting again. This setting is used to see stable signals that are within the noise 
    * MAX HOLD sets the display to hold the maximum value measured. Reset the hold by selecting again. This setting can be used for many measurements such as showing the power envelope of a modulated signal. 
    * MAX DECAY sets the display to hold the maximum value measured for a certain amount of scans after which the maximum will start to decay. The default number of scans to hold is 20. This default can be changed in the SETTINGS menu. This setting is used instead of MAX HOLD to reduce the impact of spurious signals 
    * AVER 4 sets the averaging to new_measurement = old_measurement*3/4+measured_value/4. By default the averaging is linear power averaging 
    * AVER 16 sets the averaging to new_measurement = old_measurement*15/16+measured_value/16. By default the averaging is linear power averaging 


### **caloutput**
* **Status:** Done
* **Description:** Disables or sets the caloutput to a specified frequency in MHz
* **Original Usage:** `caloutput off|30|15|10|4|3|2|1`
* **Library Function :**  `caloutput(val="off"|30|15|10|4|3|2|1)`
* **Example Return:** no return
* **Notes:**


### **capture**
* **Status:** Done
* **Description:** Requests a screen dump to be sent in binary format of HEIGHTxWIDTH pixels of each 2 bytes
* **Original Usage:** `capture`
* **Library Function Call:** `capture()`
* **Example Return:** `format:'\x00\x00\x00\x00\x00\x00\x00\...x00\x00\x00'`
* **Notes:** tinySA original: 320x240, tinySA Ultra: 480x320 


### **clearconfig**
* **Status:** Done
* **Description:** Resets the configuration data to factory defaults
* **Original Usage:** `clearconfig`
* **Library Function Call:** `clearconfig()`
* **Example Return:** `b'Config and all cal data cleared. \r\nDo reset manually to take effect. Then do touch cal and save.\r'`
* **Notes:** Requires password '1234'. Hardcoded.


### **color**
* **Status:** Some error checking to be added
* **Description:** Sets or gets the colors used
* **Original Usage:** `color [{id} {rgb24}]`
* **Library Function Call:** `color(ID=None|0..31, RGB=None(default:'0xF8FCF8')|'0x000000'..'0xFFFFFF')`
* **Example Return:** If ID='None' used:  
`0: 0x000000\r\n  1: 0xF8FCF8\r\n  2: 0x808080\r\n  3: 0xE0E4E0\r\n  4: 0x000000\r\n  5: 0xD0D0D0\r\n  6: 0xF8FC00\r\n  7: 0x40FC40\r\n  8: 0xF800F8\r\n  9: 0xF84040\r\n 10: 0x18E000\r\n 11: 0xF80000\r\n 12: 0x0000F8\r\n 13: 0xF8FCF8\r\n 14: 0x808080\r\n 15: 0x00FC00\r\n 16: 0x808080\r\n 17: 0x000000\r\n 18: 0xF8FCF8\r\n 19: 0x0000F8\r\n 20: 0xF88080\r\n 21: 0x00FC00\r\n 22: 0x888C88\r\n 23: 0xD8DCD8\r\n 24: 0x282828\r\n 25: 0xC0C4C0\r\n 26: 0xF8FCF8\r\n 27: 0x00FC00\r\n 28: 0x00FCF8\r\n 29: 0xF8FC00\r\n 30: 0x000000\r\n 31: 0x000000\r'`
* **Notes:** the hex value currently must be passed in as a string. error checking for rgb24 format needs to be added


### **correction**
* **Status:** TODO
* **Description:** Sets or gets the frequency level correction table
* **Original Usage:** `correction [0..9 {frequency} {level}]`
* **Alternate Original:**  'correction  {table_name} [(0..9|0..19) {frequency} {level}]' 
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **dac**
* **Status:** Done
* **Description:** Sets or gets the dac value
* **Original Usage:** `dac [0..4095]`
* **Library Function Call(s):** `dac(val=None|0..4095)`
* **Example Return:** `b'usage: dac {value(0-4095)}\r\ncurrent value: 1922\r'`
* **Notes:**

### **data**
* **Status:** Done
* **Description:** Gets the trace data
* **Original Usage:** `data 0..2`
* **Library Function Call:** `data(val=0|1|2)`
* **Example Return:** `format bytearray(b'7.593750e+00\r\n-8.437500e+01\r\n-8.693750e+01\r\n...\r')`
* **Notes:**  0 = temp value, 1 = stored trace, 2 = measurement. strength in decibels (dB) 
       
          
### **deviceid**
* **Status:** Done
* **Description:** Sets or gets a user settable integer number ID that can be use to identify a specific tinySA connected to the PC
* **Original Usage:** `deviceid [{number}]`
* **Library Function Call:** `deviceid(id=None|{int number})`
* **Example Return:** 'deviceid 0\r'
* **Notes:**

### **direct**
* **Status:** TODO
* **Description:** ??
* **Original Usage:** `direct {start|stop|on|off} {freq(Hz)}`
* **Library Function Call:** `direct()`
* **Example Return:**
* **Notes:**

### **ext_gain**
* **Status:** Done
* **Description:** Sets the external attenuation/amplification
* **Original Usage:** `ext_gain -100..100`
* **Library Function Call:** `ext_gain(val=-100...100)`
* **Example Return:** no return
* **Notes:** Works in both input and output mode

### **fill**
* **Status:** TODO
* **Description:** Sent by tinySA when in auto refresh mode
* **Original Usage:**
* **Library Function Call:**
* **Example Return:** `format: "fill\r\n{X}{Y}{Width}{Height} {Color}\r\n"`
* **Notes:** All numbers returned are binary coded 2 bytes little endian. Similar to 'bulk'???

### **freq**
* **Status:** Done
* **Description:** Pauses the sweep and sets the measurement frequency.
* **Original Usage:** `freq {frequency}`
* **Library Function Call:** `freq()`
* **Example Return:** no return
* **Notes:**  

### **freq_corr**
* **Status:** Done
* **Description:** Gets the frequency correction.
* **Original Usage:** `freq_corr`
* **Library Function Call:**  `freq_corr()`
* **Example Return:** `b'0 ppb\r'`
* **Notes:** This command returns the frequency correction, in parts per billion (ppb).

### **frequencies**
* **Status:** Done
* **Description:** Gets the frequencies used by the last sweep
* **Original Usage:** `frequencies`
* **Library Function Call:**  `frequencies()`
* **Example Return:**  `b'1500000000\r\n... \r\n3000000000\r'`
* **Notes:**  

### **help**
* **Status:** TODO libraryHelp() 
* **Description:** Gets a list of the available commands
* **Original Usage:** `help`
* **Library Function Calls:**
    * `help(val=0|1)` 
    * `tinySAHelp()`
    * `libraryHelp()` 
* **Example Return:**  
* **Notes:** 0 = tinySAHelp(), 1=libraryHelp(). Both functions can also be called directly. libraryHelp() has more information about this library and the inputs. 

### **hop**
* **Status:** TODO. needs error checking added
* **Description:** Measures the input level at each of the indicated frequencies.
* **Original Usage:** `hop {start(Hz)} {stop(Hz)} {step(Hz) | points}  [outmask]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Ultra only. From [tinysa-org](https://tinysa-org.translate.goog/wiki/pmwiki.php?n=Main.USBInterface&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US): if the 3rd parameter is below 450 it is assumed to be points, otherwise as step frequency Outmask selects if the frequency (1) or level (2) is output. 

### **if**
* **Status:** Done
* **Description:** Sets the intermediate frequency (IF) to automatic or a specific value
* **Original Usage:** `if (0|433M..435M )`
* **Library Function Call:** `setIF(val=0|433M..435M|'auto')`
* **Example Return:**
* **Notes:** Val input of 0 is 'auto'. Added explicit 'auto' to match other library funcs.

### **if1**
* **Status:** Done
* **Description:** Sets intermediate frequency (IF) to a specific value
* **Original Usage:** `if1 (975M..979M )`
* **Library Function Call:** `setIF1(val=0|975M..979M|'auto')`
* **Example Return:**
* **Notes:** Val input of 0 is 'auto'. Added explicit 'auto' to match other library funcs.

### **info**
* **Status:** Done
* **Description:** Displays various software/firmware and hardware information
* **Original Usage:** `info`
* **Library Function Call:** `info()`
* **Example Return:** `b'tinySA ULTRA\r\n2019-2024 Copyright @Erik Kaashoek\r\n2016-2020 Copyright edy555\r\nSW licensed under GPL. See: https://github.com/erikkaashoek/tinySA\r\nVersion: tinySA4_v1.-143-g864bb27\r\nBuild Time: Jan 10 2024 - 11:14:08\r\nKernel: 4.0.0\r\nCompiler: GCC 7.2.1 20170904 (release) [ARM/embedded-7-branch revision 255204]\r\nArchitecture: ARMv7E-M Core Variant: Cortex-M4F\r\nPort Info: Advanced kernel mode\r\nPlatform:STM32F303xC Analog & DSP\r'`
* **Notes:**

### **level**
* **Status:** Done
* **Description:** Sets the output level
* **Original Usage:** `level -76..13`
* **Library Function Call:** `level(val=-76...13)`
* **Example Return:** `b''`, `b'ERROR'`
* **Notes:** Not all values in the range are available. Added a `b'ERROR'` return for when values are not available.

### **levelchange**
* **Status:** Done
* **Description:** Sets the output level delta for low output mode level sweep
* **Original Usage:** `levelchange -70..+70`
* **Library Function Call:** `levelchange(val=-70...70)`
* **Example Return:** `b''`, `b'ERROR'`
* **Notes:** Added a `b'ERROR'` return for when values are not available.

### **leveloffset**
* **Status:** TODO
* **Description:** Sets or gets the level calibration data
* **Original Usage:** `leveloffset low|high|switch [output] {error}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** For the output corrections first ensure correct output levels at maximum output level. For the low output set the output to -50dBm and measure and correct the level with "leveloffset switch error" where For all output leveloffset commands measure the level with the leveloffset to zero and calculate error = measured level - specified level

### **line**
* **Status:** TODO
* **Description:** 
* **Original Usage:**  `line off|{level}` 
* **Library Function Call:**
* **Example Return:**
* **Notes:**  

### **load**
* **Status:** Done
* **Description:** Loads a previously stored preset to the connected device
* **Original Usage:** `load 0..4`
* **Library Function Call:** `load(val=0|1|2|3|4)`
* **Example Return:**
* **Notes:** 0 is the startup preset

### **lna**
* **Status:** Done
* **Description:** Set lna usage off/on
* **Original Usage:** `lna off|on` 
* **Library Function Call:** `lna(val="off"|"on")`
* **Example Return:** no return
* **Notes:**

### **lna2**
* **Status:** TODO
* **Description:** ??
* **Original Usage:** `lna2 0..7|auto`
* **Library Function Call:** `lna2(val="auto"|0..7)`
* **Example Return:**
* **Notes:**

### **marker**
* **Status:** TODO
* **Description:** sets or dumps marker info
* **Original Usage:**  `marker {id} on|off|peak|{freq}| {index}`
* **Library Function Call:** `marker()`
* **Example Return:**
* **Notes:**  where id=1..4 index=0..num_points-1
Marker levels will use the selected unit Marker peak will activate the marker (if not done already), position the marker on the strongest signal and display the marker info The frequency must be within the selected sweep range mode 

### **menu**
* **Status:** TODO
* **Description:** The menu command can be used to activate any menu item based on the index of the menu item
* **Original Usage:** `menu {#} [{#} [{#} [{#}]]]`
* **Library Function Call:** `menu([])`
* **Example Return:**
* **Notes:** where # is the menu entry number starting with 1 at the top.
Example: menu 6 2 will toggle the waterfall option 

### **mode**
* **Status:** TODO
* **Description:** Sets the mode of the tinySA
* **Original Usage:** `mode low|high input|output`
* **Library Function Call:** `mode()`
* **Example Return:**
* **Notes:** Check documentation on this to see if more options

### **modulation**
* **Status:** TODO
* **Description:** Set the modulation in output mode
* **Original Usage:** `modulation off|AM_1kHz|AM_10Hz|NFM|WFM|extern`
* **Library Function Call:** `modulation()`
* **Example Return:**
* **Notes:**

### **nf**
* **Status:** TODO
* **Description:** ??
* **Original Usage:** ` `
* **Library Function Call:** ` `
* **Example Return:**
* **Notes:** Check documentation on this to see if more options

### **output**
* **Status:** TODO
* **Description:** Sets the output on or off
* **Original Usage:** `output on|off`
* **Library Function Call:** `output(val="off"|"on")`
* **Example Return:**
* **Notes:**

### **pause**
* **Status:** Done
* **Description:** Pauses the sweeping in either input or output mode
* **Original Usage:** `pause`
* **Library Function Call:** `pause()`
* **Example Return:** no return
* **Notes:**

### **rbw**
* **Status:** TODO: error checking
* **Description:** sets the rbw to either automatic or a specific value
* **Original Usage:** `rbw auto|3..600`
* **Library Function Call:** `rbw(val="auto"|3..600)`
* **Example Return:** 
* **Notes:** the number specifies the target rbw in kHz. Frequencies listed in official documentation: 3 kHz, 10 kHz, 30 kHz, 100 kHz, 300 kHz, 600 kHz     

### **recall**
* **Status:** Done
* **Description:** Loads a previously stored preset from the device
* **Original Usage:** ` recall 0..4`
* **Library Function Call:** `recal(val=0|1|2|3|4)`
* **Example Return:**
* **Notes:** Same functionality as `load()`. 0 is the startup preset.

### **refresh**
* **Status:** Done
* **Description:** Enables or disables the auto refresh mode
* **Original Usage:** `refresh on|off`
* **Library Function Call:** `refresh(val="off"|"on")`
* **Example Return:** no return
* **Notes:**

### **release**
* **Status:** Done
* **Description:** Triggers a signal for the removal/release of the touch screen
* **Original Usage:** `release`
* **Library Function Call:** `release()`
* **Example Return:**
* **Notes:**

### **remark**
* **Status:** TODO
* **Description:** does nothing
* **Original Usage:** `remark [use any text]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** ?? included due to documentation 

### **repeat**
* **Status:** TODO: input error checking
* **Description:** Sets the number of (re)measurements that should be taken at every frequency
* **Original Usage:** ` repeat 1..1000`
* **Library Function Call:**
* **Example Return:**
* **Notes:** increasing the repeat reduces the noise per frequency, repeat 1 is the normal scanning mode. 

### **reset**
* **Status:** Done
* **Description:** Resets the tinySA
* **Original Usage:** `reset`
* **Library Function Call:** `reset()`
* **Example Return:**
* **Notes:** Disconnects the serial.

### **restart**
* **Status:** TODO: test and add input
* **Description:** Restarts the  tinySA after the specified number of seconds
* **Original Usage:** `restart {seconds}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 seconds stops the restarting process


### **resume**
* **Status:** Done
* **Description:** Resumes the sweeping in either input or output mode
* **Original Usage:** `resume`
* **Library Function Call:** `resume()`
* **Example Return:**
* **Notes:**

### **save**
* **Status:** TODO: printout
* **Description:** Saves the current setting to a preset
* **Original Usage:** `save 0..4`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 is the startup preset

### **saveconfig**
* **Status:** TODO: printout
* **Description:** Saves the device configuration data
* **Original Usage:** `saveconfig`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
 

### **scan**
* **Status:** TODO: error checking
* **Description:** Performs a scan and optionally outputs the measured data
* **Original Usage:** `scan {start(Hz)} {stop(Hz)} [points] [outmask]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where the outmask is a binary OR of 1=frequencies, 2=measured data, 4=stored data and points is maximum 290

### **scanraw**
* **Status:** TODO: error checking
* **Description:** Performs a scan of unlimited amount of points and send the data in binary form
* **Original Usage:** `scanraw {start(Hz)} {stop(Hz)} [points][option]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** From Documentation 1: The measured data is send as '{' ('x' MSB LSB)*points '}' where the 16 bit data is scaled by 32.

From Documentation 2: The measured data is the level in dBm and is send as '{' ('x' MSB LSB)*points '}'. To get the dBm level from the 16 bit data, divide by 32 and subtract 128 for the tinySA and 174 for the tinySA Ultra. The option, when present, can be either 0,1,2 or 3 being the sum of 1=unbuffered and 2=continuous 

UNDERGROING TESTING
   
### **sd_delete**
* **Status:** TODO
* **Description:** Deletes a specific file on the sd card
* **Original Usage:** `sd_delete {filename}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **sd_list**
* **Status:** Done
* **Description:** Displays list of filenames with extension and sizes
* **Original Usage:** `sd_list`
* **Library Function Call:** `sd_list()`
* **Example Return:** -0.bmp 307322
* **Notes:**
  
### **sd_read**
* **Status:**  TODO: error checking
* **Description:** Reads a specific file on the sd card
* **Original Usage:** `sd_read {filename}`
* **Library Function Call:** `sd_read(filename)`
* **Example Return:**
* **Notes:**

### **selftest**
* **Status:** TODO: error checking + printout
* **Description:** performs one or all selftests
* **Original Usage:** `selftest 0 0..9`
* **Library Function Call:** `selftest(val=0..9)`
* **Example Return:**
* **Notes:**
  
    
### **spur**
* **Status:** TODO: test format, add print
* **Description:** Enables or disables spur reduction
* **Original Usage:** `spur on|off`
* **Library Function Call:** `spur(val="off"|"on")`
* **Example Return:**
* **Notes:**
 

### **status**
* **Status:** TODO: add printout
* **Description:** Displays the current device status (paused/resumed)
* **Original Usage:** `status`
* **Library Function Call:** `status()`
* **Example Return:** Resumed
* **Notes:**

### **sweep**
* **Status:** TODO: input error checking
* **Description:** Set sweep boundaries or execute a sweep
* **Original Usage:** `sweep [(start|stop|center|span|cw {frequency}) | ({start(Hz)} {stop(Hz)} [0..290] ) ]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** sweep without arguments lists the current sweep settings, the frequencies specified should be within the permissible range. The sweep commands apply both to input and output modes

### **sweeptime**
* **Status:** TODO: input error checking
* **Description:** Sets the sweeptime
* **Original Usage:** `sweep {time(Seconds)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** the time specified may end in a letter where  m=mili and u=micro

### **sweep_voltage**
* **Status:** TODO: testing
* **Description:** Sets the sweep voltage 
* **Original Usage:** `sweep_voltage {0-3.3}`
* **Library Function Call:** `sweep_voltage()`
* **Example Return:**
* **Notes:** Not sure if this should be included for manual override or not. testing needed.

### **text**
* **Status:**  TODO:write func
* **Description:** specifies the text entry for the active keypad 
* **Original Usage:** `text keypadtext `
* **Library Function Call:** `text()`
* **Example Return:**
* **Notes:** where keypadtext is the text used. Example: text 12M
Currently does not work for entering file names 

### **threads**
* **Status:** TODO: add printout
* **Description:** lists information of the threads in the tinySA
* **Original Usage:** `threads`
* **Library Function Call:** `threads()`
* **Example Return:**
* **Notes:**

### **touch**
* **Status:** TODO: error checking for screen
* **Description:** sends the coordinates of a touch
* **Original Usage:** `touch {X coordinate} {Y coordinate}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** The upper left corner of the screen is "0 0"

### **touchcal**
* **Status:** TODO: error checking
* **Description:** starts the touch calibration
* **Original Usage:** `touchcal`
* **Library Function Call:** `touchcal`
* **Example Return:**
* **Notes:** is there a way to cancel this?

### **touchtest**
* **Status:** TODO: error checking
* **Description:** starts the touch test
* **Original Usage:** `touchtest`
* **Library Function Call:** `touchtest()`
* **Example Return:**
* **Notes:**

### **trace**
* **Status:** TODO: error checking
* **Description:** displays all or one trace information or sets trace related information
* **Original Usage:** `trace [{0..2} | dBm|dBmV|dBuV| V|W |store|clear|subtract | (scale|reflevel) auto|{level}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **trigger**
* **Status:** TODO: error checking
* **Description:** sets the trigger type or level
* **Original Usage:** `trigger auto|normal|single|{level(dBm)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** the trigger level is always set in dBm

### **ultra**
* **Status:** TODO: error checking
* **Description:** turn on/config tiny SA ultra mode
* **Original Usage:** `ultra off|on|auto|start|harm {freq}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **usart_cfg**
* **Status:** TODO: printout
* **Description:** returns port current baud rate
* **Original Usage:** `usart_cfg`
* **Library Function Call:**
* **Example Return:**
* **Notes:**  default is 115,200

### **vbat**
* **Status:** TODO: printout
* **Description:** returns the current battery voltage
* **Original Usage:** `vbat`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **vbat_offset**
* **Status:** TODO: printout
* **Description:** returns or sets the battery offset value
* **Original Usage:** `vbat_offset [{0..4095}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **version**
* **Status:** TODO: printout
* **Description:** returns the version text
* **Original Usage:** `version`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **wait**
* **Status:** TODO: printout
* **Description:** wait for a single sweep to finish and pauses sweep or waits for specified number of seconds
* **Original Usage:** `wait [{seconds}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **zero**
* **Status:** TODO: documentation
* **Description:**
* **Original Usage:** `zero {level}\r\n174dBm`
* **Library Function Call:**
* **Example Return:**
* **Notes:**




''' Full list of help commands
commands: freq time dac nf saveconfig clearconfig zero sweep pause resume wait repeat status caloutput save recall trace trigger marker line usart_cfg vbat_offset color if if1 lna2 agc actual_freq freq_corr attenuate level sweeptime leveloffset levelchange modulation rbw mode spur lna direct ultra load ext_gain output deviceid correction calc menu text remark

Other commands: version reset data frequencies scan hop scanraw test touchcal touchtest usart capture refresh touch release vbat help info selftest sd_list sd_read sd_delete threads
'''

The list of commands from 'help' that are still 'unknown' or don’t appear to have an impact on the tinySA via this Python API:

'''
usart

'''

## Additional Library Commands

## Table of Command and Device Compatibility

This library was developed with the tinySA Ultra, and there's some commands that might have been added/dropped between devices. This table is a record of CURRENT known compatibility with THIS library, and to what level the PC can interact with the device. It is HIGHLY likely to NOT be complete. 

If a last checked firmware version is known, that is included in the header in the parenthesis. 

?? is for an unfinished TODO list item, not an unknown. When a function is complete its compatibility is added.

|  Device Command  | tinySA ()   | tinySA Ultra ()| tinySA Ultra + ()|
|------------------|-------------|----------------|------------------|
| abort | |??| |
| actual_freq| | Get Only | |
| agc| | Set | |
| attenuate| | Set | |
| bulk| | ??| |
| calc| | Set | |
| caloutput| | Set | |
| capture| | Get| |
| clearconfig| | Reset | |
| color| | Set and Get | |
| correction| |??| |
| dac| |Set and Get | |
| data| | Get | |
| deviceid|| Set and Get | |
| direct| |??| |
| ext_gain| | Set | |
| fill| |??| |
| freq| |Set| |
| freq_corr| |Get | |
| frequencies| |Get | |
| help| |Get | |
| hop| No | ?? | |
| if| | Set | |
| if1| | Set | |
| info| | Get| |
| level| | Set | |
| levelchange| | Set| |
| leveloffset| | ??| |
| line| | ??| |
| load| |Load to Device| |
| lna| | Set | |
| lna2| |?? | |
| marker| | ??| |
| menu| |?? | |
| mode| |??| |
| modulation| | ??| |
| nf| | ??| |
| output| |?? | |
| pause| | Set| |
| rbw| | ??| |
| recall| |Load to Device| |
| refresh| | | |
| release| | | |
| remark| | | |
| repeat| | | |
| reset| | | |
| restart| | | |
| resume| | | |
| save| | | |
| saveconfig| | | |
| scan| | | |
| scanraw| | | |
| sd_delete| | | |
| sd_list| | | |
| sd_read| | | |
| selftest| | | |
| spur| | | |
| status| | | |
| sweep| | | |
| sweeptime| | | |
| sweep_voltage| | | |
| text| | | |
| threads| | | |
| touch| | | |
| touchcal| | | |
| touchtest| | | |
| trace| | | |
| trigger| | | |
| ultra| | | |
| usart_cfg| | | |
| vbat| | | |
| vbat_offset| | | |
| version| | | |
| wait| | | |
| zero| | | |



## Notes for Beginners

### Vocab Check

### Calibration Setup

## References

* [tinySA HomePage](https://tinysa.org/wiki/)  https://www.tinysa.org/wiki/
    * [tinySA PC control](https://tinysa.org/wiki/pmwiki.php?n=Main.PCSW) 
        * https://tinysa.org/wiki/pmwiki.php?n=Main.PCSW 
    * [tinySA list of general pages](https://tinysa.org/wiki/pmwiki.php?n=Main.PageList) 
        * https://tinysa.org/wiki/pmwiki.php?n=Main.PageList

* [http://athome.kaashoek.com/tinySA/python/ ]( http://athome.kaashoek.com/tinySA/python/ )
* [official pyserial](https://pypi.org/project/pyserial/) https://pypi.org/project/pyserial/
* https://groups.io/g/tinysa/topic/tinysa_screen_capture_using/82218670
* The firmware on github at https://github.com/erikkaashoek/tinySA
    * https://github.com/erikkaashoek/tinySA/blob/main/main.c


## Publications and Integration
This API was written to support the work in:

L. Linkous, E. Karincic, M. Suche and E. Topsakal, "Reinforcement Learning Controlled Mechanically Reconfigurable Antennas," 2025 United States National Committee of URSI National Radio Science Meeting (USNC-URSI NRSM), Boulder, CO, USA, 2025

Other publications featuring the code in this repo will be added as they become public.

## Licensing

The code in this repository has been released under GPL-2.0, but licensing will be updated to match whatever the tinySA products and code are released under. This licensing does not take priority over the official releases.


