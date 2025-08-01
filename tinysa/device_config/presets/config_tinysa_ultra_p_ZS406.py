#! /usr/bin/python3

##--------------------------------------------------------------------\
#   tinySA_python  config_tinysa_ultra_p_ZS406.py
#   
#   Configurations for the tinySA Ultra Plus ZS406. Refer to the 
#   README for information on format and arguments. 
#   Format based on device library. 
#
#   See https://www.tinysa.org/wiki/ for official documentation.
#   https://tinysa.org/wiki/pmwiki.php?n=TinySA4.Specification
#   https://tinysa.org/wiki/pmwiki.php?n=TinySA4.Comparison
#
#   Author(s): Lauren Linkous
#   Last update: May 30, 2025
##--------------------------------------------------------------------\

DEVICE_TYPE = "ULTRA_P_ZS406"

## screen
SCREEN_WIDTH = 480      # size in pixels
SCREEN_HEIGHT = 320     # size in pixels
SCREEN_SIZE_IN = 4      # size in inches
DISPLAY_PTS = 450       # max num scan points displayed on screen
    #  5 
#16 bits per RGB pixel

## battery
MAX_DEVICE_BATTERY = 4095  # val read from device. analogue

## storage
HAS_SD_CARD = True

# operation configs
## does device have ultra?
ULTRA_MODE_OPTION = True
MAX_LEVEL_CAIBRATION = 6e9 #6 GHz
HARMONIC_MODE_OPTION = True


## NOTE from documention:
## input/output specification of the tinySA is split over the 4 modes
## OUPUT: LOW/ HIGH
## INOUT: LOW/HIGH

## INPUT 
# spectrum analyzer
SA_INPUT_FREQS = {"low":[100e3, 900e6], "high":[100e3, 5.4e9], "all":[100e3, 10e9]}
SA_INPUT_FREQS_ULTRA = {"all":[100e3,  5.4e9]}
SA_HARMONIC_MODE_FREQS = {"all":[100e3, 10e9]}


# OUTPUT  MODE
# signal generator
# [[100 kHz, 960 MHz], [240MHz, 960MHz]]
MAX_LOW_OUTPUT_FREQ = {"sine": 900e6, "square": 4.4e9} # Sine wave up to 800MHz, Square wave up to 4.4GHz 
MAX_HIGH_OUTPUT_FREQ = {"sine": 900e6, "square": 4.4e9} #none specified, but high and low share range for Ultra/+
OUTPUT_LEVEL = {"low":[-115, -19], "high":[-115, -19]} #dBm


SG_DEVICE_FREQS_SINE = {"low":[100e3, 900e6], "high":[100e3, 900e6], "all":[100e3, 900e6]}
SG_DEVICE_FREQS_SQUARE = {"low":[100e3, 4.4e9], "high":[100e3, 4.4e9], "all":[100e3, 4.4e9]}
SG_DEVICE_FREQS_TEST = {"low":[], "high":[ ], "all":[]}


RESOLUTION_FILTERS = [200e3, 850e3] # 200Hz to 850kHz
RES_FILTER_STEPS  = [1, 3, 10]

## built in LNA?
HAS_INTERNAL_LNA = True
NUM_INTERNAL_LNA = 1
LNA_RANGE = {"1": [100e3, 4e9]} #100 kHz to 4GHz
LNA_GAIN_DB = {"1":[20]} #dB
 
INTERNAL_STEP_ATTENUATOR_NORMAL = [0, 31] #dB
INTERNAL_STEP_ATTENUATOR_HIGH = [] #dB


MODULATION_FREQ = [50, 3.5e3] #50Hz to 3.5kHz


# OTHERS
## bandpass filters
SWITCHABLE_BANDPASS = False
# TODO: more info needed here for if it should be a distinct check/toggle