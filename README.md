
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

From the [official wiki USB Interface page](#https://tinysa-org.translate.goog/wiki/pmwiki.php?n=Main.USBInterface&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US):

    There is limited error checking against incorrect parameters of incorrect mode

    * Frequencies can be specified using an integer optionally postfixed with a the letter 'k' for kilo 'M' for Mega or 'G' for Giga. E.g. 0.1M (100kHz), 500k (0.5MHz) or 12000000 (12MHz)
    * Levels are specified in dB(m) and can be specified using a floating point notation. E.g. 10 or 2.5
    * Time is specified in seconds optionally postfixed with the letters 'm' for mili or 'u' for micro. E.g. 1 (1 second), 2.5 (2.5 seconds), 120m (120 milliseconds)


## Example Implementations

This library has been tested on Windows, but not yet on Unix systems. The primary difference should be the format of the serial port connection, but there may be smaller bugs in format that have not been detected yet. 

### Finding the Serial Port

### Connecting and Disconnecting
 Show the process for initializing, opening the serial port, getting device info, and disconnecting


### Toggle Error Messages

### Device and Library Help


### Setting tinySA Ultra Parameters

### Getting Data from Active Screen

### Saving Screen Images

### Saving Data to CSV

### Plotting Data with Matplotlib

### Realtime Graphing



## List of tinySA Ultra Commands and Their Library Commands

This list and the following list in the [List of All Library Commands](#list-of-all-library-commands) section have considerable overlap for documentation during development purposes.

This section is sorted by the tinySA (Ultra) commands, and includes:
* A brief description of what the command does
* What the original usage looked like
* The tinySA_Python function call, or calls if multiple options exist 
* Example return, or example format of return
* Any additional notes about the usage

All of the listed commands are included in this API to some degree, but error checking may be incomplete.

Quick Link Table:
|  |   |     |   |       |      |
|-------|-------|-------|-------|-------|-------|
| [abort](#abort)   | [actual_freq](#actual_freq)  | [agc](#agc)      | [attenuate](#attenuate)  | [bulk](#bulk)       | [calc](#calc)        |
| [caloutput](#caloutput) | [capture](#capture)  | [clearconfig](#clearconfig) | [color](#color)   | [correction](#correction) | [dac](#dac)        |
| [data](#data)     | [deviceid](#deviceid)       | [direct](#direct) | [ext_gain](#ext_gain)    | [fill](#fill)       | [freq](#freq)        |
| [freq_corr](#freq_corr) | [frequencies](#frequencies) | [help](#help)    | [hop](#hop)            | [if](#if)           | [if1](#if1)          |
| [info](#info)     | [level](#level)             | [levelchange](#levelchange) | [leveloffset](#leveloffset) | [load](#load)   | [lna](#lna)          |
| [lna2](#lna2)     | [marker](#marker)           | [menu](#menu)     | [mode](#mode)           | [modulation](#modulation) | [output](#output)  |
| [pause](#pause)   | [rbw](#rbw)                 | [recall](#recall) | [refresh](#refresh)     | [release](#release) | [remark](#remark)    |
| [repeat](#repeat) | [reset](#reset)             | [restart](#restart) | [resume](#resume)      | [save](#save)       | [saveconfig](#saveconfig) |
| [scan](#scan)     | [scanraw](#scanraw)         | [sd_delete](#sd_delete) | [sd_list](#sd_list)   | [sd_read](#sd_read) | [selftest](#selftest) |
| [spur](#spur)     | [status](#status)           | [sweep](#sweep)   | [sweeptime](#sweeptime) | [sweep_voltage](#sweep_voltage) | [text](#text)   |
| [threads](#threads) | [touch](#touch)             | [touchcal](#touchcal) | [touchtest](#touchtest) | [trace](#trace)     | [trigger](#trigger)  |
| [ultra](#ultra)   | [usart_cfg](#usart_cfg)     | [vbat](#vbat)     | [vbat_offset](#vbat_offset) | [version](#version) | [wait](#wait)        |
| [zero](#zero)     |        |     |        |        |       |



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
* **Example Return:** format: "bulk\r\n{X}{Y}{Width}{Height} {Pixeldata}\r\n"
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
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** requests a screen dump to be sent in binary format of  320x240 pixels of each 2 bytes
* **Original Usage:** `capture`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **clearconfig**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** resets the configuration data to factory defaults
* **Original Usage:** `clearconfig`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Requires password '1234'


### **color**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets or dumps the colors used
* **Original Usage:** `color [{id} {rgb24}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **correction**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets or dumps the frequency level correction table
* **Original Usage:** `correction [0..9 {frequency} {level}]`
* **Alternate Original:**  'correction  {table_name} [(0..9|0..19) {frequency} {level}]' 
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **dac**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets or dumps the dac value
* **Original Usage:** `dac [0..4095]`
* **Library Function Call(s):**
* **Example Return:**
* **Notes:**

### **data**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** dumps the trace data
* **Original Usage:** `data 0..2`
* **Library Function Call:**
* **Example Return:**
* **Notes:**  0 = temp value, 1 = stored trace, 2 = measurement
       
          
### **deviceid**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets or dumps a user settable integer number ID that can be use to identify a specific tinySA connected to the PC
* **Original Usage:** `deviceid [{number}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **direct**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** ??
* **Original Usage:** `direct {start|stop|on|off} {freq(Hz)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **ext_gain**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the external attenuation/amplification
* **Original Usage:** `ext_gain -100..100`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Works in both input and output mode

### **fill**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sent by tinySA when in auto refresh mode
* **Original Usage:**
* **Library Function Call:**
* **Example Return:** `format: "fill\r\n{X}{Y}{Width}{Height} {Color}\r\n"`
* **Notes:** All numbers returned are binary coded 2 bytes little endian.

### **freq**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** Pauses the sweep and sets the measurement frequency.
* **Original Usage:** `freq {frequency}`
* **Library Function Call:** 
* **Example Return:** 
* **Notes:**  

### **freq_corr**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** Gets the frequency correction.
* **Original Usage:** (not specified, but inferred to be a command like `freq_corr`)
* **Library Function Call:**  
* **Example Return:** `0 ppb`
* **Notes:** This command returns the frequency correction, typically in parts per billion (ppb).

### **frequencies**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** Dumps the frequencies used by the last sweep.
* **Original Usage:** `frequencies`
* **Library Function Call:**  
* **Example Return:** 
* **Notes:**  

### **help**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** Dumps a list of the available commands.
* **Original Usage:** `help`
* **Library Function Call:**  
* **Example Return:**  
* **Notes:** 

### **hop**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** Measures the input level at each of the indicated frequencies.
* **Original Usage:** `hop {start(Hz)} {stop(Hz)} {step(Hz) | points}  [outmask]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Ultra only. From [tinysa-org](https://tinysa-org.translate.goog/wiki/pmwiki.php?n=Main.USBInterface&_x_tr_sl=auto&_x_tr_tl=en&_x_tr_hl=en-US): if the 3rd parameter is below 450 it is assumed to be points, otherwise as step frequency Outmask selects if the frequency (1) or level (2) is output. 

### **if**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the intermediate frequency (IF) to automatic or a specific value
* **Original Usage:** `if ( 0 | 433M..435M )`
* **Library Function Call:**
* **Example Return:**
* **Notes:**where 0 means automatic

### **if1**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**sets intermediate frequency (IF) to a specific value
* **Original Usage:** `if1 (975M..979M )`
* **Library Function Call:**
* **Example Return:**
* **Notes:**where 0 means automatic

### **info**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** displays various SW and HW information
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **level**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the output level
* **Original Usage:** `level -76..13`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Not all values in the range are available

### **levelchange**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the output level delta for low output mode level sweep
* **Original Usage:** `levelchange -70..+70`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **leveloffset**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets or dumps the level calibration data
* **Original Usage:** `leveloffset low|high|switch [output] {error}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** For the output corrections first ensure correct output levels at maximum output level. For the low output set the output to -50dBm and measure and correct the level with "leveloffset switch error" where For all output leveloffset commands measure the level with the leveloffset to zero and calculate error = measured level - specified level

### **load**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**loads a previously stored preset
* **Original Usage:** `load 0..4`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 is the startup preset

### **lna**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** toggle lna usage off/on
* **Original Usage:** `lna off|on  ` 
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **lna2**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**
* **Original Usage:** `lna2 0..7|auto`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **marker**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets or dumps marker info
* **Original Usage:**  `marker {id} on|off|peak|{freq}| {index}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**  where id=1..4 index=0..num_points-1
Merker levels will use the selected unit Marker peak will activate the marker (if not done already), position the marker on the strongest signal and display the marker info The frequency must be within the selected sweep range mode 

### **menu**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** The menu command can be used to activate any menu item
* **Original Usage:** `menu {#} [{#} [{#} [{#}]]]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where # is the menu entry number starting with 1 at the top.
Example: menu 6 2 will toggle the waterfall option 

### **mode**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the mode of the tinySA
* **Original Usage:** `mode low|high input|output`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **modulation**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the modulation in output mode
* **Original Usage:** `modulation off|AM_1kHz|AM_10Hz|NFM|WFM|extern`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **output**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the output on or off
* **Original Usage:** `output on|off`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **pause**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** pauses the sweeping in either input or output mode
* **Original Usage:** `pause`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **rbw**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the rbw to either automatic or a specific value
* **Original Usage:** `rbw auto|3..600`
* **Library Function Call:**
* **Example Return:** 
* **Notes:** the number specifies the target rbw in kHz. Frequencies listed in official documentation: 3 kHz, 10 kHz, 30 kHz, 100 kHz, 300 kHz, 600 kHz     

### **recall**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** loads a previously stored preset
* **Original Usage:** ` recall 0..4`
* **Library Function Call:** 
* **Example Return:**
* **Notes:** same as load.  0 is the startup preset 

### **refresh**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** enables/disables the auto refresh mode
* **Original Usage:** `refresh on|off`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **release**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** signals a removal of the touch
* **Original Usage:** `release`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **remark**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** does nothing
* **Original Usage:** `remark [use any text]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** ?? 

### **repeat**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the number of measurements that should be taken at every frequency
* **Original Usage:** ` repeat 1..1000`
* **Library Function Call:**
* **Example Return:**
* **Notes:** increasing the repeat reduces the noise per frequency, repeat 1 is the normal scanning mode. 

### **reset**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** resets the tinySA
* **Original Usage:** `reset`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **restart**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** restarts the  tinySA after the specified number of seconds
* **Original Usage:** `restart {seconds}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 seconds stops the restarting process


### **resume**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** resumes the sweeping in either input or output mode
* **Original Usage:** `resume`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **save**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** saves the current setting to a preset
* **Original Usage:** `save 0..4`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 is the startup preset

### **saveconfig**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** saves the device configuration data
* **Original Usage:** `saveconfig`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
 

### **scan**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**performs a scan and optionally outputs the measured data
* **Original Usage:** `scan {start(Hz)} {stop(Hz)} [points] [outmask]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**where the outmask is a binary OR of 1=frequencies, 2=measured data, 4=stored data and points is maximum 290

### **scanraw**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**performs a scan of unlimited amount of points and send the data in binary form
* **Original Usage:** `scanraw {start(Hz)} {stop(Hz)} [points][option]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** From Documentation 1: The measured data is send as '{' ('x' MSB LSB)*points '}' where the 16 bit data is scaled by 32.

From Documentation 2: The measured data is the level in dBm and is send as '{' ('x' MSB LSB)*points '}'. To get the dBm level from the 16 bit data, divide by 32 and subtract 128 for the tinySA and 174 for the tinySA Ultra. The option, when present, can be either 0,1,2 or 3 being the sum of 1=unbuffered and 2=continuous 

UNDERGROING TESTING
   
### **sd_delete**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** delete a specific file on the sd card
* **Original Usage:** `sd_delete {filename}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **sd_list**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**displays list of filenames with extension and sizes
* **Original Usage:**
* **Library Function Call:** `sd_list`
* **Example Return:** -0.bmp 307322
* **Notes:**
  
### **sd_read**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** read a specific file on the sd_card
* **Original Usage:** `sd_read {filename}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **selftest**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** performs one or all selftests
* **Original Usage:** `selftest 0 0..9`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
  
    
### **spur**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** enables or disables spur reduction
* **Original Usage:** `spur on|off`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
 

### **status**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:**displays the current device status (paused/resumed)
* **Original Usage:**
* **Library Function Call:** `status`
* **Example Return:** Resumed
* **Notes:**

### **sweep**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** set sweep boundaries or execute a sweep
* **Original Usage:** `sweep [(start|stop|center|span|cw {frequency}) | ({start(Hz)} {stop(Hz)} [0..290] ) ]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** sweep without arguments lists the current sweep settings, the frequencies specified should be within the permissible range. The sweep commands apply both to input and output modes

### **sweeptime**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the sweeptime
* **Original Usage:** `sweep {time(Seconds)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**the time specified may end in a letter where  m=mili and u=micro

### **sweep_voltage**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the sweep voltage. 
* **Original Usage:** `sweep {0-3.3}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Not sure if this should be included for manual override or not. testing needed.

### **text**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** specifies the text entry for the active keypad 
* **Original Usage:** `text keypadtext `
* **Library Function Call:**
* **Example Return:**
* **Notes:** where keypadtext is the text used. Example: text 12M
Currently does not work for entering file names 

### **threads**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** lists information of the threads in the tinySA
* **Original Usage:** `threads`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **touch**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sends the coordinates of a touch
* **Original Usage:** `touch {X coordinate} {Y coordinate}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** The upper left corner of the screen is "0 0"

### **touchcal**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** starts the touch calibration
* **Original Usage:** `touchcal`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **touchtest**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** starts the touch test
* **Original Usage:** `touchtest`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **trace**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** displays all or one trace information or sets trace related information
* **Original Usage:** `trace [{0..2} | dBm|dBmV|dBuV| V|W |store|clear|subtract | (scale|reflevel) auto|{level}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **trigger**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** sets the trigger type or level
* **Original Usage:** `trigger auto|normal|single|{level(dBm)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** the trigger level is always set in dBm

### **ultra**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** turn on/config tiny SA ultra mode
* **Original Usage:** `ultra off|on|auto|start|harm {freq}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **usart_cfg**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** returns port current baud rate
* **Original Usage:** `usart_cfg`
* **Library Function Call:**
* **Example Return:**
* **Notes:**  default is 115,200

### **vbat**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** returns the current battery voltage
* **Original Usage:** `vbat`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **vbat_offset**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** returns or sets the battery offset value
* **Original Usage:** `vbat_offset [{0..4095}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **version**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** returns the version text
* **Original Usage:** `version`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **wait**
* **Status:** NOT ON DEVELOPER'S DUT
* **Description:** wait for a single sweep to finish and pauses sweep or waits for specified number of seconds
* **Original Usage:** `wait [{seconds}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **zero**
* **Status:** NOT ON DEVELOPER'S DUT
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

## List of All Library Commands

## Table of Command and Device Compatibility

This library was developed with the tinySA Ultra, and there's some commands that might have been added/dropped between devices. This table is a record of CURRENT known compatibility. It is HIGHLY likely to NOT be complete. 

If a last checked firmware version is known, that is included in the header in the parenthesis. 

|  Device Command  | tinySA ()   | tinySA Ultra ()| tinySA Ultra + ()|
|------------------|-------------|----------------|------------------|
| abort | |??| |
| actual_freq| | Get only | |
| agc| | Set | |
| attenuate| | Set | |
| bulk| | ??| |
| calc| | Set | |
| caloutput| | Set | |
| capture| | | |
| clearconfig| | | |
| color| | | |
| correction| | | |
| dac| | | |
| data| | | |
| deviceid| | | |
| direct| | | |
| ext_gain| | | |
| fill| | | |
| freq| | | |
| freq_corr| | | |
| frequencies| | | |
| help| | | |
| hop| | | |
| if| | | |
| if1| | | |
| info| | | |
| level| | | |
| levelchange| | | |
| leveloffset| | | |
| load| | | |
| lna| | | |
| lna2| | | |
| marker| | | |
| menu| | | |
| mode| | | |
| modulation| | | |
| output| | | |
| pause| | | |
| rbw| | | |
| recall| | | |
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


