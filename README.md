# TinySA_Python
A Non-GUI Python API class for the Tiny SA Ultra written to support several personal projects


This uses official resources and documentation but is NOT endorsed by the official tinySA product

# INPROGRESS

## Table of Contents
* [The TinySA Ultra](#the-tinysa-ultra)
* [Requirements](#requirements)
* [Usage](#usage)
* [Error Handling](#error-handling)
* [Example Implementations](#example-implementations)
    * [Opening Serial Port](#opening-serial-port)
    * [Getting Device Info](#getting-device-info)
    * [Setting TinySA Ultra Parameters](#setting-tinysa-ultra-parameters)
    * [Getting Data from Active Screen](#getting-data-from-active-screen)
    * [Plotting Data with Matplotlib](#plotting-data-with-matplotlib)
    * [Realtime Graphing](#realtime-graphing)
    * [Saving Screen Images](#saving-screen-image)
    * [Saving Data to CSV](#saving-data-to-csv)
* [List tinySA Commands](#list-of-tinysa-commands)
* [References](#references)
* [Publications and Integration](#publications-and-integration)
* [Licensing](#licensing)  


## The TinySA Ultra



## Requirements

This project requires numpy and pyserial. 

Use 'pip install -r requirements.txt' to install the following dependencies:

```python
pyserial
numpy

```

These dependencies cover only the API. Additional dependencies should be installed to follow the included examples and tests. These can be installed with 'pip install -r test_requirements.txt':

```python
matplotlib

```

## Usage


## Error Handling

## Example Implementations

### Opening Serial Port

### Getting Device Info

### Setting TinySA Ultra Parameters

### Getting Data from Active Screen

### Plotting Data with Matplotlib

### Realtime Graphing

### Saving Screen Images

### Saving Data to CSV


## List of tinySA Commands

This is a partial list that is being expanded. All of these are included in this API to some degree, but error checking may be incomplete
 

### **actual_freq**
* **Description:**  ???
* **Original Usage:** `actual_freq`
* **Library Function Call:**
* **Example Return:** 3000000000
* **Notes:**

### **agc**
* **Description:**
* **Original Usage:** `agc 0..7|auto`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **attenuate**
* **Description:** sets the internal attenuation
* **Original Usage:** `attenuate [auto|0-31]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **bulk**
* **Description:** sent by tinySA when in auto refresh mode
* **Original Usage:** 
* **Library Function Call:**
* **Example Return:** format: "bulk\r\n{X}{Y}{Width}{Height} {Pixeldata}\r\n"
* **Notes:** where all numbers are binary coded 2 bytes little endian. The pixeldata is encoded as 2 bytes per pixel           
            

### **calc**
* **Description:** sets or cancels one of the measurement modes
* **Original Usage:** `calc off|minh|maxh|maxd|aver4|aver16|quasip`
* **Library Function Call:**
* **Example Return:**
* **Notes:** the commands are the same as those listed in the MEASURE menu


### **caloutput**
* **Description:** disables or sets the caloutput to a specified frequency in MHz
* **Original Usage:** `caloutput off|30|15|10|4|3|2|1`
* **Library Function :**
* **Example Return:**
* **Notes:**

### **capture**
* **Description:**requests a screen dump to be sent in binary format of  320x240 pixels of each 2 bytes
* **Original Usage:** ``
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **clearconfig**
* **Description:** resets the configuration data to factory defaults
* **Original Usage:** ``
* **Library Function Call:**
* **Example Return:**
* **Notes:** Requires password '1234'

### **color**
* **Description:** sets or dumps the colors used
* **Original Usage:** `color [{id} {rgb24}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **correction**
* **Description:** sets or dumps the frequency level correction table
* **Original Usage:** `correction [0..9 {frequency} {level}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **dac**
* **Description:** sets or dumps the dac value
* **Original Usage:** `dac [0..4095]`
* **Library Function Call(s):**
* **Example Return:**
* **Notes:**

### **data**
* **Description:**
* **Original Usage:** `data 0..2`
* **Library Function Call:**
* **Example Return:**
* **Notes:**  0 = temp value, 1 = stored trace, 2 = measurement
       
          
### **deviceid**
* **Description:** sets of dumps a user settable number that can be use to identify a specific tinySA
* **Original Usage:** `deviceid [{number}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **direct**
* **Description:** ??
* **Original Usage:** `direct {start|stop|on|off} {freq(Hz)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **ext_gain**
* **Description:** sets the external attenuation/amplification
* **Original Usage:** `ext_gain -100..100`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Works in both input and output mode


### **fill**
* **Description:**send by tinySA when in auto refresh mode
* **Original Usage:**
* **Library Function Call:**
* **Example Return:** `format: "fill\r\n{X}{Y}{Width}{Height} {Color}\r\n"`
* **Notes:**where all numbers are binary coded 2 bytes little endian.

### **freq**
* **Description:** Pauses the sweep and sets the measurement frequency.
* **Original Usage:** `freq {frequency}`
* **Library Function Call:** 
* **Example Return:** 
* **Notes:**  

### **freq_corr**
* **Description:** Gets the frequency correction.
* **Original Usage:** (not specified, but inferred to be a command like `freq_corr`)
* **Library Function Call:**  
* **Example Return:** `0 ppb`
* **Notes:** This command returns the frequency correction, typically in parts per billion (ppb).

### **frequencies**
* **Description:** Dumps the frequencies used by the last sweep.
* **Original Usage:** `frequencies`
* **Library Function Call:**  
* **Example Return:** 
* **Notes:**  

### **help**
* **Description:** Dumps a list of the available commands.
* **Original Usage:** `help`
* **Library Function Call:**  
* **Example Return:**  
* **Notes:** 


### **hop**
* **Description:**
* **Original Usage:** `hop {start(Hz)} {stop(Hz)} {step(Hz) | points}  [outmask]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **if**
* **Description:**sets the IF to automatic or a specific value
* **Original Usage:** `if ( 0 | 433M..435M )`
* **Library Function Call:**
* **Example Return:**
* **Notes:**where 0 means automatic


### **if1**
* **Description:**sets if to a specific value
* **Original Usage:** `if1 (975M..979M )`
* **Library Function Call:**
* **Example Return:**
* **Notes:**where 0 means automatic


### **info**
* **Description:** displays various SW and HW information
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **level**
* **Description:** sets the output level
* **Original Usage:** `level -76..13`
* **Library Function Call:**
* **Example Return:**
* **Notes:** Not all values in the range are    available

### **levelchange**
* **Description:** sets the output level delta for low output mode level sweep
* **Original Usage:** `levelchange -70..+70`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **leveloffset**
* **Description:** sets or dumps the level calibration data
* **Original Usage:** `leveloffset low|high|switch [output] {error}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** For the output corrections first ensure correct output levels at maximum output level. For the low output set the output to -50dBm and measure and correct the level with "leveloffset switch error" where For all output leveloffset commands measure the level with the leveloffset
to zero and calculate error = measured level - specified level


### **load**
* **Description:**loads a previously stored preset
* **Original Usage:** `load 0..4`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 is the startup preset


### **lna**
* **Description:** toggle lna usage off/on
* **Original Usage:** `lna off|on  ` 
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **lna2**
* **Description:**
* **Original Usage:** `lna2 0..7|auto`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **marker**
* **Description:** sets or dumps marker info
* **Original Usage:**  `marker {id} on|off|peak|{freq}| {index}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**  where id=1..4 index=0..num_points-1
Merker levels will use the selected unit Marker peak will activate the marker (if not done already), position the marker on the strongest signal and display the marker info The frequency must be within the selected sweep range mode 

### **mode**
* **Description:** sets the mode of the tinySA
* **Original Usage:** `mode low|high input|output`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **modulation**
* **Description:** sets the modulation in output mode
* **Original Usage:** `modulation off|AM_1kHz|AM_10Hz| NFM|WFM|extern`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **output**
* **Description:** sets the output on or off
* **Original Usage:** `output on|off`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **pause**
* **Description:** pauses the sweeping in either input or output mode
* **Original Usage:** `pause`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **rbw**
* **Description:** sets the rbw to either automatic or a specific value
* **Original Usage:** `rbw auto|3..600`
* **Library Function Call:**
* **Example Return:** 
* **Notes:** the number specifies the target rbw in kHz     


### **recall**
* **Description:**
* **Original Usage:** ``
* **Library Function Call:** 
* **Example Return:**
* **Notes:** same as load


### **refresh**
* **Description:** enables/disables the auto refresh mode
* **Original Usage:** `refresh on|off`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **release**
* **Description:** signals a removal of the touch
* **Original Usage:** `release`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

 
### **reset**
* **Description:** resets the tinySA
* **Original Usage:** `reset`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **resume**
* **Description:** resumes the sweeping in either input or output mode
* **Original Usage:** `resume`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **save**
* **Description:** saves the current setting to a preset
* **Original Usage:** `save 0..4`
* **Library Function Call:**
* **Example Return:**
* **Notes:** where 0 is the startup preset


### **saveconfig**
* **Description:** saves the device configuration data
* **Original Usage:** `saveconfig`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
 
### **scan**
* **Description:**performs a scan and optionally outputs the measured data
* **Original Usage:** `scan {start(Hz)} {stop(Hz)} [points] [outmask]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**where the outmask is a binary OR of 1=frequencies, 2=measured data, 4=stored data and points is maximum 290


### **scanraw**
* **Description:**performs a scan of unlimited amount of points and send the data in binary form
* **Original Usage:** `scanraw {start(Hz)} {stop(Hz)} [points]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**The measured data is send as '{' ('x' MSB LSB)*points '}' where the 16 bit data is scaled by 32.

   
### **sd_delete**
* **Description:** delete a specific file on the sd card
* **Original Usage:** `sd_delete {filename}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **sd_list**
* **Description:**displays list of filenames with extension and sizes
* **Original Usage:**
* **Library Function Call:** `sd_list`
* **Example Return:** -0.bmp 307322
* **Notes:**
  
### **sd_read**
* **Description:** read a specific file on the sd_card
* **Original Usage:** `sd_read {filename}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **selftest**
* **Description:** performs one or all selftests
* **Original Usage:** `selftest 0 0..9`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
  
    
### **spur**
* **Description:**enables or disables spur reduction
* **Original Usage:** `spur on|off`
* **Library Function Call:**
* **Example Return:**
* **Notes:**
 

### **status**
* **Description:**displays the current device status (paused/resumed)
* **Original Usage:**
* **Library Function Call:** `status`
* **Example Return:** Resumed
* **Notes:**

### **sweep**
* **Description:**set sweep boundaries or execute a sweep
* **Original Usage:** `sweep [(start|stop|center|span|cw {frequency}) | ({start(Hz)} {stop(Hz)} [0..290] ) ]`
* **Library Function Call:**
* **Example Return:**
* **Notes:** sweep without arguments lists the current sweep settings, the frequencies specified should be within the permissible range. The sweep commands apply both to input and output modes


### **sweeptime**
* **Description:** sets the sweeptime
* **Original Usage:** `sweep {time(Seconds)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**the time specified may end in a letter where  m=mili and u=micro

### **threads**
* **Description:** lists information of the threads in the tinySA
* **Original Usage:** ``
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **touch**
* **Description:** sends the coordinates of a touch
* **Original Usage:** `touch {X coordinate} {Y coordinate}`
* **Library Function Call:**
* **Example Return:**
* **Notes:** The upper left corner of the screen is "0 0"

### **touchcal**
* **Description:**starts the touch calibration
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **touchtest**
* **Description:**starts the touch test
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **trace**
* **Description:**displays all or one trace  information or sets trace related information
* **Original Usage:** `trace [{0..2} | dBm|dBmV|dBuV| V|W |store|clear|subtract | (scale|reflevel) auto|{level}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **trigger**
* **Description:**sets the trigger type or level
* **Original Usage:** `trigger auto|normal|single|{level(dBm)}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**the trigger level is always set in dBm


### **ultra**
* **Description:** turn on/config tiny SA ultra mode
* **Original Usage:** `ultra off|on|auto|start|harm {freq}`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **vbat**
* **Description:**displays the battery voltage
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **vbat_offset**
* **Description:**displays or sets the battery offset value
* **Original Usage:** `vbat_offset [{0..4095}]`
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **version**
* **Description:** displays the version text
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**

### **wait**
* **Description:**  same as pause(?)
* **Original Usage:**
* **Library Function Call:**
* **Example Return:**
* **Notes:**


### **zero**
* **Description:**
* **Original Usage:** `zero {level}\r\n174dBm`
* **Library Function Call:**
* **Example Return:**
* **Notes:**


''' Full list of help commands
commands: freq time dac nf saveconfig clearconfig zero sweep pause resume wait repeat status caloutput save recall trace trigger marker line usart_cfg vbat_offset color if if1 lna2 agc actual_freq freq_corr attenuate level sweeptime leveloffset levelchange modulation rbw mode spur lna direct ultra load ext_gain output deviceid correction calc menu text 
remark

Other commands: version reset data frequencies scan hop 
scanraw test touchcal touchtest usart capture refresh touch release vbat help info selftest sd_list sd_read sd_delete threads
'''

The list of commands from 'help' that are still 'unknown' or dont appear to have an impact on the tinySA via this Python API:

'''
menu
remark
text
usart

'''


## References

* [tinySA HomePage](https://tinysa.org/wiki/)  https://www.tinysa.org/wiki/
* [tinySA PC control](https://tinysa.org/wiki/pmwiki.php?n=Main.PCSW)  https://tinysa.org/wiki/pmwiki.php?n=Main.PCSW 
* [http://athome.kaashoek.com/tinySA/python/ ]( http://athome.kaashoek.com/tinySA/python/ )
* [official pyserial](https://pypi.org/project/pyserial/) https://pypi.org/project/pyserial/
* https://groups.io/g/tinysa/topic/tinysa_screen_capture_using/82218670
* 

## Publications and Integration
This API was written to support the work in:

L. Linkous, E. Karincic, M. Suche and E. Topsakal, "Reinforcement Learning Controlled Mechanically Reconfigurable Antennas," 2025 United States National Committee of URSI National Radio Science Meeting (USNC-URSI NRSM), Boulder, CO, USA, 2025

Other publications featuring the code in this repo will be added as they become public.

## Licensing

The code in this repository has been released under GPL-2.0, but licensing will be updated to match whatever the tinySA products and code are released under. 

