#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   './src/tsapython/core.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   references:
#       https://tinysa.org/wiki/pmwiki.php?n=TinySA4.ConsoleCommands  (NOTE: backwards compat not tested!)
#       http://athome.kaashoek.com/tinySA/python/tinySA.py  (existing library with some examples)
#
#   This class was previously named tinySA_python. The rename is to cover the CORE device functionalities,
#   with the device specifics being added as extra modules.
#
#   The per-command methods live in mixin classes under ./_commands/ and are composed onto the
#   tinySA class below. core.py holds shared state, serial management, and reusable helpers.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

import serial
import serial.tools.list_ports # COM search method wants full path
import numpy as np
import re
import time

from ._commands.acquisition import AcquisitionMixin
from ._commands.markers_traces import MarkersTracesMixin
from ._commands.levels_gain import LevelsGainMixin
from ._commands.output_signal import OutputSignalMixin
from ._commands.calibration import CalibrationMixin
from ._commands.presets_config import PresetsConfigMixin
from ._commands.display_ui import DisplayUIMixin
from ._commands.system_info import SystemInfoMixin

class tinySA(
    AcquisitionMixin,
    MarkersTracesMixin,
    LevelsGainMixin,
    OutputSignalMixin,
    CalibrationMixin,
    PresetsConfigMixin,
    DisplayUIMixin,
    SystemInfoMixin,
):
    def __init__(self, parent=None):
        # serial port
        self.ser = None

        # message feedback
        self.verboseEnabled = False
        self.returnErrorByte = False


        # VARS BELOW HERE will be largely replaced with device class config calls
        # # this will allow for user settings and device presets
        
        # other overrides
        self.ultraEnabled = False
        self.abortEnabled = False
        self.harmonicEnabled = False

        #select device vars - hardcoding for the Ultra for now
        # device params
        self.maxPoints = 450
        # spectrum analyzer
        self.minSADeviceFreq = 100e3  #100 kHz
        self.maxSADeviceFreq = 15e9 #5.3 GHz for normal operation, but 12 GHz for edge of harmonics.
        # signal generator
        self.minSGDeviceFreq = 100e3  #100 kHz
        self.maxSGDeviceFreq = 960e6 #960 MHz
        # battery
        self.maxDeviceBattery = 4095
        # screen 
        self.screenWidth = 480
        self.screenHeight = 320

######################################################################
# Error and information printout
# set/get_verbose()  - set how detailed the error printouts are
# print_message()  - deal with the bool in one place
######################################################################

    def set_verbose(self, verbose=False):
        self.verboseEnabled = verbose

    def get_verbose(self):
        return self.verboseEnabled

    def print_message(self, msg):
        if self.verboseEnabled == True:
            print(msg)

######################################################################
# Explicit error return
# set_error_byte_return()  - set if explicit b'ERROR' is returned
# get_error_byte_return()  - get the return mode True/False
# error_byte_return()  - return 'ERROR' message or empty. 
######################################################################

    def set_error_byte_return(self, errByte=False):
        self.returnErrorByte = errByte

    def get_error_byte_return(self):
        return self.returnErrorByte

    def error_byte_return(self):
        if self.returnErrorByte == True:
            return bytearray(b'ERROR')
        else:
            return bytearray(b'') # the default

######################################################################
# Set Device Params
#   Library specific functions. These set the boundaries & features for
#   error checking in the library 
#    
# WARNING: these DO NOT change the settings on the DEVICE. just the library.
######################################################################

    def select_existing_device(self, tinySAModel):
        # uses pre-set config files. 
        # tinySAModel var must be one of the following:
        # "BASIC", "ZS405", "ZS406", "ZS407"
        try:
            noErrors = self.dev.select_preset_model(tinySAModel)
            if noErrors == False:
                print("ERROR: device configuration unable to be set.This feature is underdevelopment")
                return

            # set variables from device configs.
            # these are placeholders  tes for now
            # device params
            self.maxPoints = 450
            # spectrum analyzer
            self.minSADeviceFreq = 100e3  #100 kHz
            self.maxSADeviceFreq = 12e9 #5.3 GHz for normal operation, but 12 GHz for edge of harmonics
            # signal generator
            self.minSGDeviceFreq = 100e3  #100 kHz
            self.maxSGDeviceFreq = 960e6 #960 MHz
            # battery
            self.maxDeviceBattery = 4095
            # screen 
            self.screenWidth = 480
            self.screenHeight = 320


        except:
            print("ERROR: device configuration unable to be set.This feature is underdevelopment")

    def load_custom_config(self, configFile):
        # TODO: for loading modified or other devices working on the same firmware
        pass

######################################################################
# Direct overrides
#   These are used during DEBUG or when device state/model is already known
#   Not recommended unless you are sure of the device state
#   and which settings each device has
# WARNING: these DO NOT change the settings on the DEVICE. just the library.
######################################################################

    # error check bools

    def set_ultra_mode(self, ultraMode=False):
        self.ultraEnabled = ultraMode

    def set_abort_mode(self, abortMode=False):
        self.abortEnabled = abortMode

    def set_harmonic_mode(self, harmonicMode=False):
        self.harmonicEnabled = harmonicMode

    
    # error check boundaries
    ## signal analyzer specific

    def set_min_SA_freq(self, f):
        self.minSADeviceFreq = float(f)

    def get_min_SA_freq(self):
        return self.minSADeviceFreq 

    def set_max_SA_freq(self, f):
        self.maxSADeviceFreq = float(f)

    def get_max_SA_freq(self):
        return self.maxSADeviceFreq

    ## signal generator specific 

    def set_min_SG_freq(self, f):
        self.minSGDeviceFreq = float(f)

    def get_min_SG_freq(self):
        return self.minSGDeviceFreq 

    def set_max_SG_freq(self, f):
        self.maxSGDeviceFreq = float(f)

    def get_max_SG_freq(self):
        return self.maxSGDeviceFreq

######################################################################
# Serial management and message processing
######################################################################

    def autoconnect(self, timeout=1):
        # attempt to autoconnect to a detected port. 
        # returns: found_bool, connected_bool
        # True if successful, False otherwise

        # List all available serial ports
        ports = serial.tools.list_ports.comports()
        # loop through the ports and print out info
        for port_info in ports:

            # print out which port we're trying
            port = port_info.device 
            self.print_message(f"Checking port: {port}")
            vid = port_info.vid
            pid = port_info.pid

            # check if it's a tinySA or nanoVNA:
            if (vid==None):
                pass 
            elif (hex(vid) == '0x483') and (hex(pid)=='0x5740'):
                self.print_message(f"tinySA device identified at port: {port}")
                connected_bool = self.connect(port, timeout)

                return True, connected_bool


        return False, False # no tinySA found, not connected

    def connect(self, port, timeout=1):
        # attempt connection to provided port. 
        # returns: True if successful, False otherwise

        try:
            self.ser = serial.Serial(port=port, timeout=timeout)
            return True
        except Exception as err:
            self.print_message("ERROR: cannot open port at " + str(port))
            self.print_message(err)
            return False

    def disconnect(self):
        # closes the serial port
        self.ser.close()

    def tinySA_serial(self, writebyte, printBool=False, pts=None):
        # write out to serial, get message back, clean up, return
        
        # clear INPUT buffer
        self.ser.reset_input_buffer()
        # clear OUTPUT buffer
        self.ser.reset_output_buffer()


        self.ser.write(bytes(writebyte, 'utf-8'))
        msgbytes = self.get_serial_return()
        msgbytes = self.clean_return(msgbytes)

        if printBool == True:
            print(msgbytes) #overrides verbose for debug

        return msgbytes

    def get_serial_return(self):
        # while there's a buffer, read in the returned message
        # original buffer reading from: https://groups.io/g/tinysa/topic/tinysa_screen_capture_using/82218670

        buffer = bytes()
        while True:
            if self.ser.in_waiting > 0:
                buffer += self.ser.read(self.ser.in_waiting)
                try:
                    # split the stream to take a chunk at a time
                    # get up to '>' of the prompt
                    complete = buffer[:buffer.index(b'>')+1]  
                    # leave the rest in buffer
                    buffer = buffer[buffer.index(b'ch>')+1:]  
                except ValueError:
                    # this is an acceptable err, so can skip it and keep looping
                    continue 
                except Exception as err:
                    # otherwise, something else is wrong
                    self.print_message("ERROR: exception thrown while reading serial")
                    self.print_message(err)
                    return None
                break
            
        return bytearray(complete)

    def read_until_end_marker(self, end_marker=b'}', timeout=10.0):
        # scan and scan raw might return early with tinySA_serial
        # so this is written to 
        import time
        
        buffer = bytes()
        start_time = time.time()
        
        while True:
            if self.ser.in_waiting > 0:
                buffer += self.ser.read(self.ser.in_waiting)
                
                # Check if we have the end marker
                if end_marker in buffer:
                    # Find the position after the end marker
                    end_pos = buffer.find(end_marker) + len(end_marker)
                    complete = buffer[:end_pos]
                    # Keep any remaining data for next read
                    self.remaining_buffer = buffer[end_pos:]
                    return bytearray(complete)
            
            # Timeout check
            if time.time() - start_time > timeout:
                self.print_message(f"WARNING: Timeout waiting for end marker {end_marker}")
                break
            
            time.sleep(0.01)
        
        return bytearray(buffer)

    def clean_return(self, data):
        # takes in a bytearray and removes 1) the text up to the first '\r\n' (includes the command), an 2) the ending 'ch>'
        # Find the first occurrence of \r\n (carriage return + newline)
        first_newline_index = data.find(b'\r\n')
        if first_newline_index != -1:
            # Slice the bytearray to remove everything before and including the first '\r\n'
            data = data[first_newline_index + 2:]  # Skip past '\r\n'
        # Check if the message ends with 'ch>'
        if data.endswith(b'ch>'):
            # Remove 'ch>' from the end
            data = data[:-4]  # Remove the last 4 bytes ('ch>')
        return data

######################################################################
# Reusable format checking functions
######################################################################

    def convert_frequency(self, txtstr):
        # this takes the user input (as text) and converts it. 
        #  From documentation:
        #       Frequencies can be specified using an integer optionally postfixed with a the letter 
        #       'k' for kilo 'M' for Mega or 'G' for Giga. E.g. 0.1M (100kHz), 500k (0.5MHz) or 12000000 (12MHz)
        # However the abbreviation makes error checking with numerics more difficult. so convert everything to Hz.
        #  e notation is fine
        pass

    def convert_time(self, txtstr):
        # this takes the user input (as text) and converts it. 
        #  From documentation:        
        #        Time is specified in seconds optionally postfixed with the letters 'm' for mili 
        #        or 'u' for micro. E.g. 1 (1 second), 2.5 (2.5 seconds), 120m (120 milliseconds)



        pass

    def is_rgb24(self, hexStr):
        # check if the string matches the pattern 0xRRGGBB
        pattern = r"^0x[0-9A-Fa-f]{6}$"
        return bool(re.match(pattern, hexStr))