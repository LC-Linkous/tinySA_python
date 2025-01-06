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

TODO: turn this in to a table with format:
<br>
library command | tinySA comment | input | example output



''' tinySA commands list

actual_freq
            ???
            example return: 3000000000
agc
            usage: agc 0..7|auto
attenuate
            sets the internal attenuation to
            automatic or a specific value
            usage: attenuate [auto|0-31]
bulk
            send by tinySA when in auto refresh
            mode
            format: "bulk\r\n{X}{Y}{Width}{Height}
            {Pixeldata}\r\n"
            where all numbers are binary coded 2
            bytes little endian. The Pixeldata is
            encoded as 2 bytes per pixel
calc
            sets or cancels one of the measurement
            modes
            usage: calc off|minh|maxh|maxd|aver4|
            aver16|quasip
            the commands are the same as those
            listed in the MEASURE menu
caloutput
            disables or sets the caloutput to a
            specified frequency in MHz
            usage: caloutput off|30|15|10|4|3|2|1
capture
            requests a screen dump to be send in
            binary format of 320x240 pixels of
            each 2 bytes
clearconfig
            resets the configuration data to
            factory defaults
            usage: clearconfig 1234
color
            sets or dumps the colors used
            usage: color [{id} {rgb24}]
            correction
            sets or dumps the frequency level
            correction table
            usage: correction [0..9 {frequency}
            {level}]
correction
            usage: correction low|lna|ultra|ultra_lna|direct|direct_lna|harm|harm_lna|out|out_direct|out_adf|out_ultra|off|on 0-19 frequency(Hz) value(dB)
        
dac
            sets or dumps the dac value
            usage: dac [0..4095]
data
            dumps the trace data
            usage: data 0..2
            0=temp value, 1=stored trace,
            2=measurement
deviceid
            sets of dumps a user settable number
            that can be use to identify a specific
            tinySA
            usage: deviceid [{number}]
direct
            usage: direct {start|stop|on|off} {freq(Hz)}
ext_gain
            sets the external
            attenuation/amplification
            usage: ext_gain -100..100
            Works in both input and output mode
fill
            send by tinySA when in auto refresh
            mode
            format: "fill\r\n{X}{Y}{Width}{Height}
            {Color}\r\n"
            where all numbers are binary coded 2
            bytes little endian.
freq
            pauses the sweep and sets the
            measurement frequency
            usage: freq {frequency}
freq_corr
            get frequency correction
            example return: 0 ppb
frequencies
            dumps the frequencies used by the last
            sweep
            usage: frequencies
help
            dumps a list of the available commands
            usage: help
hop
            ??
            usage: hop {start(Hz)} {stop(Hz)} {step(Hz) | points} [outmask]
if 
            sets the IF to automatic or a specific
            value
            usage: if ( 0 | 433M..435M )
            where 0 means automatic
if1
            sets if to a specific value
            usage: if1 (975M..979M )
            where 0 means automatic
info
            displays various SW and HW information
level
            sets the output level
            usage: level -76..13
            Not all values in the range are
            available
levelchange
            sets the output level delta for low
            output mode level sweep
            usage: levelchange -70..+70
leveloffset
            sets or dumps the level calibration
            data
            usage: leveloffset low|high|switch
            [output] {error}
            For the output corrections first
            ensure correct output levels at
            maximum output level. For the low
            output set the output to -50dBm and
            measure and correct the level with
            "leveloffset switch error" where
            For all output leveloffset commands
            measure the level with the leveloffset
            to zero and calculate
            error = measured level - specified
            level
load
            loads a previously stored preset
            usage: load 0..4
            where 0 is the startup preset
lna
            toggle lna usage off/on
            usage: lna off|on   
lna2            
            usage: lna2 0..7|auto
marker
            sets or dumps marker info
            usage: marker {id} on|off|peak|{freq}|
            {index}
            where id=1..4 index=0..num_points-1
            Merker levels will use the selected
            unit
            Marker peak will activate the marker
            (if not done already), position the
            marker on the strongest signal and
            display the marker info
            The frequency must be within the
            selected sweep range
mode
            sets the mode of the tinySA
            usage: mode low|high input|output
modulation
            sets the modulation in output mode
            usage: modulation off|AM_1kHz|AM_10Hz|
            NFM|WFM|extern
output
            sets the output on or off
            usage: output on|off
pause
            pauses the sweeping in either input or
            output mode
            usage: pause
rbw
            sets the rbw to either automatic or a
            specific value
            usage: rbw auto|3..600
            the number specifies the target rbw in
            kHz            
recall
            same as load
refresh
            enables/disables the auto refresh mode
            Usage refresh on|off
release
            signals a removal of the touch
            usage: release
reset
            resets the tinySA
            usage: reset
resume
            resumes the sweeping in either input
            or output mode
            usage: resume
save
            saves the current setting to a preset
            usage: save 0..4
            where 0 is the startup preset
saveconfig
            saves the device configuration data
            usage: saveconfig
scan
            performs a scan and optionally outputs
            the measured data
            usage: scan {start(Hz)} {stop(Hz)}
            [points] [outmask]
            where the outmask is a binary OR of
            1=frequencies, 2=measured data,
            4=stored data and points is maximum
            290
scanraw
            performs a scan of unlimited amount of
            points and send the data in binary
            form
            usage: scanraw {start(Hz)} {stop(Hz)}
            [points]
            The measured data is send as '{' ('x'
            MSB LSB)*points '}' where the 16 bit
            data is scaled by 32.
sd_delete
            delete a specific file on the sd card
            usage: sd_delete {filename}
sd_list
            displays list of filenames with extension 
            and sizes
            ex: -0.bmp 307322
sd_read
            read a specific file on the sd_card
            usage: sd_read {filename}
selftest
            performs one or all selftests
            usage: selftest 0 0..9
spur
            enables or disables spur reduction
            usage: spur on|off
status
            displays the current device status 
            (paused/resumed)
            example return: Resumed
sweep
            set sweep boundaries or execute a
            sweep
            usage: sweep [ ( start|stop|center|
            span|cw {frequency} ) | ( {start(Hz)}
            {stop(Hz)} [0..290] ) ]
            sweep without arguments lists the
            current sweep settings, the
            frequencies specified should be within
            the permissible range. The sweep
            commands apply both to input and
            output modes
sweeptime
            sets the sweeptime
            usage: sweep {time(Seconds)}the time
            specified may end in a letter where
            m=mili and u=micro
threads
            lists information of the threads in
            the tinySA
touch
            sends the coordinates of a touchusage:
            touch {X coordinate} {Y coordinate}
            The upper left corner of the screen is
            "0 0"
touchcal
            starts the touch calibration
touchtest
            starts the touch test
trace
            displays all or one trace information
            or sets trace related information
            usage: trace [ {0..2} | dBm|dBmV|dBuV|
            V|W |store|clear|subtract | (scale|
            reflevel) auto|{level}
trigger
            sets the trigger type or level
            usage: trigger auto|normal|single|
            {level(dBm)}
            the trigger level is always set in dBm
ultra
        turn on/config tiny SA ultra mode
        usage: ultra off|on|auto|start|harm {freq}
vbat
            displays the battery voltage
vbat_offset
            displays or sets the battery offset
            value
            usage: vbat_offset [{0..4095}]
version
            displays the version text
wait
            same as pause(?)
zero
            usage: zero {level}\r\n174dBm

'''



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

