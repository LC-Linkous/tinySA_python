#! /usr/bin/python3

##--------------------------------------------------------------------\
#   tinySA_python  config_tinysa_basic.py
#   
#   Configurations for the tinySA Ultra ZS405. Refer to the 
#   README for information on format and arguments. 
#   Format based on device library. 
#
#   See https://www.tinysa.org/wiki/ for official documentation.
#   https://tinysa.org/wiki/pmwiki.php?n=Main.Specification
#   https://tinysa.org/wiki/pmwiki.php?n=TinySA4.Comparison
#
#   Author(s): Lauren Linkous
#   Last update: May 30, 2025
##--------------------------------------------------------------------\

DEVICE_TYPE = "BASIC"

## screen
SCREEN_WIDTH = 320      # size in pixels
SCREEN_HEIGHT = 240     # size in pixels
SCREEN_SIZE_IN = 2.8    # size in inches
DISPLAY_PTS = 290       # max num scan points displayed on screen
    #  51, 101, 145 or 290 
#16 bits per RGB pixel

## battery
MAX_DEVICE_BATTERY = 4095  # val read from device. analogue

## storage
HAS_SD_CARD = False

# operation configs
## does device have ultra?
ULTRA_MODE_OPTION = False
MAX_LEVEL_CAIBRATION = None # no max, full range probably
HARMONIC_MODE_OPTION = False


## NOTE from documention:
## input/output specification of the tinySA is split over the 4 modes
## OUPUT: LOW/ HIGH
## INOUT: LOW/HIGH

## INPUT 
# spectrum analyzer
# [[100 kHz, 350 MHz], [240MHz, 960MHz]]
SA_INPUT_FREQS = {"low":[100e3, 350e6], "high":[240e6, 960e6], "all":[100e3, 960e6]}
SA_INPUT_FREQS_ULTRA = {"all":[]} # NO ultra mode
SA_HARMONIC_MODE_FREQS = {"all":[]} #no harmonic mode

# OUTPUT  MODE
# signal generator
# [[100 kHz, 960 MHz], [240MHz, 960MHz]]
MAX_LOW_OUTPUT_FREQ = {"all": 350e6} # 350MHz 
MAX_HIGH_OUTPUT_FREQ = {"all":960e6} # 960MHz 
OUTPUT_LEVEL = {"low":[-76, -7], "high":[-32, 16]} #dBm

SG_DEVICE_FREQS_SINE = {"low":[100e3, 350e6], "high":[], "all":[100e3, 350e6]}
SG_DEVICE_FREQS_SQUARE = {"low":[], "high":[240e6, 960e6], "all":[240e6, 960e6]}
SG_DEVICE_FREQS_TEST = {"low":[], "high":[ ], "all":[]}


RESOLUTION_FILTERS = [3e3, 600e3] # 3kHz to 600kHz
RES_FILTER_STEPS  = [1, 3, 10]

## built in LNA?
HAS_INTERNAL_LNA = False
NUM_INTERNAL_LNA = 0
LNA_RANGE = [] 
LNA_GAIN_DB = [] 

INTERNAL_STEP_ATTENUATOR_NORMAL = [0, 31] #dB
INTERNAL_STEP_ATTENUATOR_HIGH = [] #dB


MODULATION_FREQ = [50, 5e3] #50Hz to 5kHz


# OTHERS
## bandpass filters
SWITCHABLE_BANDPASS = False
# TODO: more info needed here 