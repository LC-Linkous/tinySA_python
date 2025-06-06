#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python 
#   './tinySA_python.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   references:
#       https://tinysa.org/wiki/pmwiki.php?n=TinySA4.ConsoleCommands  (NOTE: backwards compat not tested!)
#       http://athome.kaashoek.com/tinySA/python/tinySA.py  (existing library with some examples)
#
#
#
#
#   Author(s): Lauren Linkous
#   Last update: June 3, 2025
##--------------------------------------------------------------------------------------------------\

import serial
import numpy as np
import re


try:
    from src.device_config.device_config import deviceConfig
except:
    from device_config.device_config import deviceConfig


class tinySA():
    def __init__(self, parent=None):
        # serial port
        self.ser = None

        # user device class (to account for custom settings) 
        self.dev = deviceConfig #TODO, finish this class and integrate

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
        self.deviceType = "ULTRA_ZS405"
        # spectrum analyzer
        self.minSADeviceFreq = 100e3  #100 kHz
        self.maxSADeviceFreq = 5.3e9 #5.3 GHz
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
# Direct overrides
#   These are used during DEBUG or when device state is already known
#   Not recommended unless you are sure of the device state
#   and which settings each device has
# WARNING: these DO NOT change the settings on the DEVICE. just the library.
######################################################################

    def set_ultra_mode(self, ultraMode=False):
        self.ultraEnabled = ultraMode

    def set_abort_mode(self, abortMode=False):
        self.abortEnabled = abortMode

    def set_harmonic_mode(self, harmonicMode=False):
        self.harmonicEnabled = harmonicMode
    

######################################################################
# Serial management and message processing
######################################################################

    def autoconnect(self, timeout=1):
        # TODO
        # attempt to autoconnect to a detected port. 
        # returns: True if successful, False otherwise

        return False


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


    def tinySA_serial(self, writebyte, printBool=False):
        # write out to serial, get message back, clean up, return
        
        self.ser.write(bytes(writebyte, 'utf-8'))
        msgbytes = self.get_serial_return()
        msgbytes = self.clean_return(msgbytes)

        if printBool == True:
            print(msgbytes) #overrides verbose for debug

        return msgbytes

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


######################################################################
# Serial command config, input error checking
######################################################################

    def abort(self, val=None):
        # Sets the abort enabled status (on/off)
        # usage: abort [off|on]
        # example return: bytearray(b'')

        # #explicitly allowed vals
        accepted_vals =  ["off", "on"]        

        #check input
        if (val in accepted_vals): #toggle state
            writebyte = 'abort '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            if val == "on":
                self.print_message("ABORT option ENABLED")
                self.abortEnabled = True
            elif val == "off":
                self.print_message("ABORT option DISABLED")
                self.abortEnabled = False
        elif val == None: #action
            if self.abortEnabled == True:
                writebyte = 'abort\r\n'
                msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            else:
                self.print_message("ABORT option must be ENABLED before use")
                msgbytes = bytearray(b'')
        else:
            self.print_message("ERROR: abort() takes NONE|\"off\"|\"on\" as arguments")
            msgbytes = bytearray(b'')
        return msgbytes
    
    def enable_abort(self):
        # alias for abort()
        return self.abort( "on")
    def disable_abort(self):
        # alias for abort()
        return self.abort("off")
    def abort_action(self):
        # alias for abort()
        return self.abort()

    def actual_freq(self, val=None):
        # Sets or gets the frequency correction set by CORRECT FREQUENCY menu in the expert menu settings
        # related to freq_corr
        # usage: actual_freq [{frequency}]
        # example return: bytearray(b'3000000000\r')

        if val == None:
            #get the dac       
            writebyte = 'actual_freq\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (self.minSADeviceFreq <= val <=self.maxSADeviceFreq ):
            writebyte = 'actual_freq '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("actual_freq set to " + str(val))
        else:
            self.print_message("ERROR: actual_freq() takes either None or integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_actual_freq(self, val):
        # alias for actual_freq()
        return self.actual_freq(val)      
    def get_actual_freq(self):
        # alias for actual_freq()
        return self.actual_freq(None)
    

    def agc(self, val='auto'):
        # Enables/disables the build in Automatic Gain Control
        # usage: agc 0..7|auto
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 8, 1) # max exclusive
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'agc '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)     
            self.print_message("agc() set with " + str(val))
        else:
            self.print_message("ERROR: agc() takes vals [0 - 7]|\"auto\"")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_agc(self, val):
        # alias for agc()
        return self.agc(val)

    def attenuate(self, val='auto'):
        # sets the internal attenuation to automatic or a specific value
        # usage: attenuate [auto|0-31]
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 31, 1) # max exclusive
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'attenuate '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("attenuate() set with " + str(val))           
        else:
            self.print_message("ERROR: attenuate() takes vals [0 - 31]|\"auto\"")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_attenuation(self, val):
        # alias for attenuate()
        return self.attenuate(val)

    def bulk(self):
        # sent by tinySA when in auto refresh mode
        # format: "bulk\r\n{X}{Y}{Width}{Height}
        # {Pixeldata}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian. The Pixeldata is
        # encoded as 2 bytes per pixel

        writebyte = 'bulk\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("capture() called for screen data")   
        return msgbytes

    def get_bulk_data(self):
        # alias for bulk()
        return self.bulk()

    def calc(self, val="off"):
        # sets or cancels one of the measurement modes
        # the commands are the same as those listed 
        # in the MEASURE menu
        # usage: calc off|minh|maxh|maxd|aver4|aver16|quasip
        # example return:

        #explicitly allowed vals
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]
        #check input
        if (val in accepted_vals):
            writebyte = 'calc '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)     
            self.print_message("calc() set with " + str(val))
        else:
            self.print_message("ERROR: calc() takes vals \"off\"|\"minh\"|\"maxh\"|\"maxd\"|\"aver4\"|\"aver16\"|\"quasip\"")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_calc_off(self):
        return self.calc("off")
    def set_calc_minh(self):
        return self.calc("minh")
    def set_calc_maxh(self):
        return self.calc("maxh")
    def set_calc_maxd(self):
        return self.calc("maxd")
    def set_calc_aver4(self):
        return self.calc("aver4")
    def set_calc_aver16(self):
        return self.calc("aver16")
    def set_calc_quasip(self):
        return self.calc("quasip")

    def cal_output(self, val="off"):
        # disables or sets the caloutput to a specified frequency in MHz
        # usage: caloutput off|30|15|10|4|3|2|1
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  ["off", 1,2,3,4,10,15,30]
        #check input
        if (val in accepted_vals):
            writebyte = 'caloutput '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("caloutput() set with " + str(val))        
        else:
            self.print_message("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_cal_output_off(self):
        # alias for cal_output()
        return self.caloutput("off")
    def set_cal_output_30(self):
        # alias for cal_output()
        return self.caloutput(30)
    def set_cal_output_15(self):
        # alias for cal_output()
        return self.caloutput(15)
    def set_cal_output_10(self):
        # alias for cal_output()
        return self.caloutput(10)       
    def set_cal_output_4(self):
        # alias for cal_output()
        return self.caloutput(4)
    def set_cal_output_3(self):
        # alias for cal_output()
        return self.caloutput(3)
    def set_cal_output_2(self):
        # alias for cal_output()
        return self.caloutput(2)
    def set_cal_output_1(self):
        # alias for cal_output()
        return self.caloutput(1)

    
    def capture(self):
        # requests a screen dump to be sent in binary format 
        # of 320x240 pixels of each 2 bytes
        # usage: capture
        # example return: bytearray(b'\x00 ...\x00\x00\x00')
        writebyte = 'capture\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("capture() called for screen data")   
        return msgbytes
    
    def capture_screen(self):
        return self.capture()

    def clear_config(self):
        # resets the configuration data to factory defaults. requires password
        # NOTE: does take other commands to fully clear all
        # usage: clearconfig 1234
        # example return: bytearray(b'Config and all cal data cleared.
        # \r\nDo reset manually to take effect. 
        # Then do touch cal and save.\r')
        writebyte = 'clearconfig 1234\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("clear_config() with password. Config and all cal data cleared. \
                          Reset manually to take effect.")
        return msgbytes
    
    def clear_and_reset(self):
        # alias function for full clear and reset process
        self.clear_config()
        self.reset()

    def color(self, ID=None, RGB='0xF8FCF8'):
        # sets or dumps the colors used
        # usage: color [{id} {rgb24}]
        # example return: 
         
        # explicitly allowed vals
        accepted_ID = np.arange(0, 31, 1) # max exclusive

        if ID == None:
            # get the color       
            writebyte = 'color\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        elif (ID in accepted_ID) and (self.is_rgb24(RGB)==True):
            # set the color based on ID       
            writebyte = 'color ' + str(ID) + ' ' + str(RGB) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("color() set with ID: " +str(ID) + " RGB: " + str(RGB))
        else:
            self.print_message("ERROR: color() takes either None, or ID as int 0..31 and RGB as a hex value")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def get_all_colors(self):
        # alias for color(). returns array of all colors
        return self.color()
    
    def get_color(self, ID):
        # alias for color(). val must be int 1-31
        msgbytes = self.color()
        # check if something has been returned, otherwise pass the error through
        if len(msgbytes) > 10:
            # Use regex to find the value at index ID
            pattern = rf'\b{int(ID)}:\s*0x([0-9A-Fa-f]+)'
            match = re.search(pattern, msgbytes)
            if match:
                return f"0x{match.group(1)}" #return rgb24 value if found
        
            # if not found, then 
            self.print_message("ERROR: color() takes either None, or ID as int 0..31 and RGB as a hex value")
            msgbytes = self.error_byte_return()
        return msgbytes
   
    def set_color(self, ID, val):
        # alias for color()
        return self.color(ID, val)


    def command(self, val):
        # if the command isn't already a function,
        #  use existing func setup to send command
        writebyte = str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("command() called with ::" + str(val))   


    def correction(self, argName="low", slot=None, freq=None, val=None):
        # sets or dumps the frequency level orrection table
        # usage: correction [0..9 {frequency} {level dB}]
        # usage: correction low|lna|ultra|ultra_lna|direct|direct_lna|harm|harm_lna|out|out_direct|out_adf|out_ultra|off|on 0-19 frequency(Hz) value(dB)
        # example return:  

        # explicitly allowed vals
        accepted_table_args = ["low", "lna", "ultra", "ultra_lna", 
                               "direct", "direct_lna",  "harm", 
                               "harm_lna", "out", "out_direct", 
                               "out_adf", "out_ultra", "off", "on"]

        accepted_slots = np.arange(0, 20, 1) # max exclusive. 

        if (argName in accepted_table_args) and (slot==None):
            # prints out the table as it currently is
            writebyte = 'correction ' + str(argName)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            # check error conditions quickly since there's 4
            if not(argName in accepted_table_args):
                self.print_message("ERROR: correction() requires a table indicator. see documentation")
                msgbytes = self.error_byte_return()
                return msgbytes
            if not(slot in accepted_slots):
                self.print_message("ERROR: correction() requires a slot from ["+ str(accepted_slots) + "]. see documentation")
                msgbytes = self.error_byte_return()
                return msgbytes
            if not(self.minSADeviceFreq<=freq) and not(freq<=self.maxSADeviceFreq):
                self.print_message("ERROR: correction() frequency outside of device specs. see documentation")
                msgbytes = self.error_byte_return()
                return msgbytes
            if not(-10<=val) and not(val<=35):
                self.print_message("ERROR: correction() val dB outside of  specs. see documentation")
                msgbytes = self.error_byte_return()
                return msgbytes
            writebyte = 'correction ' + str(argName) + ' ' + str(slot) +\
                    ' ' + str(freq) + ' ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("correction() set with " + str(argName) + " " + str(slot) +\
                    " " + str(freq) + " " + str(val))
        return msgbytes


        #TODO ADD the CORRECTION setter shortcuts here.     


    def dac(self, val=None):
        # sets or dumps the dac value
        # usage: dac [0..4095]
        # example return: bytearray(b'usage: dac {value(0-4095)}\r\ncurrent value: 1922\r')  

        if val == None:
            #get the dac       
            writebyte = 'dac\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (0<= val <=4095):
            writebyte = 'dac '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("dac set to " + str(val))
        else:
            self.print_message("ERROR: dac() takes either None or integers")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_dac(self, val):
        # alias for dac()
        return self.dac(val)
    def get_dac(self):
        # alias for dac()
        return self.dac()
    


    def data(self, val=0):
        # dumps the trace data. 
        # usage: data [0-2]
        # 0=temp value, 1=stored trace, 2=measurement
        # example return: bytearray(b'-8.671875e+01\r\n... -8.337500e+01\r\n-8.237500e+01\r')
        
        #explicitly allowed vals
        accepted_vals = [0,1,2]
        #check input
        if val in accepted_vals:
            writebyte = 'data '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)  
            if val == 0:
                self.print_message("returning temp value data") 
            elif val == 1:
                self.print_message("returning stored trace data") 
            elif val == 2:
                self.print_message("returning measurement data") 
        else:
            self.print_message("ERROR: data() takes vals [0-2]")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def get_temp_data(self):
        # alias func for data()
        return self.data(val=0)
    def get_stored_trace_data(self):
        # alias func for data()
        return self.data(val=1)
    def dump_measurement_data(self):
        # alias func for data()
        return self.data(val=2)


    def device_id(self, ID=None):
        # sets or dumps a user settable number that can be used to identify a specific tinySA
        # usage: deviceid [{number}]
        # example return: bytearray(b'deviceid 12\r')

        if id == None:
            #get the device ID        
            writebyte = 'deviceid\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif isinstance(id, int):
            writebyte = 'deviceid '+str(ID)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("device ID set to " + str(ID))
        else:
            self.print_message("ERROR: device_id() takes either None or integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def get_device_id(self):
        # alias for device_id()
        return self.device_id()

    def set_device_id(self, ID):
        # alias for device_id()
        return self.device_id(ID)


    def direct(self):
        # ??
        # usage: direct {start|stop|on|off} {freq(Hz)}
        # example return: ''

        self.print_message("Function does not exist yet. error checking needed")
        return None

    def ext_gain(self, val):
        # sets the external attenuation/amplification.
        # Works in both input and output mode
        # usage: ext_gain -100..100
        # example return: ''        
        
        #check input
        if (isinstance(val, int)) and (-100<= val <=100):
            writebyte = 'ext_gain '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("ext_gain() set to " + str(val))       
        else:
            self.print_message("ERROR: ext_gain() takes vals [-100 - 100]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def fill(self):
        # sent by tinySA when in auto refresh mode
        # format: "fill\r\n{X}{Y}{Width}{Height}
        # {Color}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian.

        self.print_message("Function does not exist yet. error checking needed")
        return None

    def freq(self, val):
        # pauses the sweep and sets the measurement frequency.
        # usage: freq {frequency}
        # example return: bytearray(b'')

        #check input
        if (isinstance(val, int)) and (self.minSADeviceFreq<= val <=self.maxSADeviceFreq):
            writebyte = 'freq '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("freq() set to " + str(val))       
        else:
            self.print_message("ERROR: freq() takes integer vals [100 kHz - 5.3 GHz] as Hz for the tinySA Ultra")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_freq(self, val):
        # freq() alias
        return self.freq(val)


    def freq_corr(self):
        # get frequency correction
        # usage: freq_corr
        # example return: bytearray(b'0 ppb\r')

        writebyte = 'freq_corr\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("getting frequency correction")
        return msgbytes
    
    def get_frequency_correction(self):
        # alias for freq_corr()
        return self.freq_corr()

    def frequencies(self):
        # gets the frequencies used by the last sweep
        # usage: frequencies
        # example return: bytearray(b'1500000000\r\n... \r\n3000000000\r')

        writebyte = 'frequencies\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("getting frequencies from the last sweep")
        return msgbytes

    def get_frequencies(self):
        # get frequencies of last sweep
        return self.frequencies()
    


    def hop(self):
        # this is a measurement, maybe a sample measurement. format looks like hop freqval integer
        # TODO: get documentation def of what the function is and the limits   
        # usage: hop {start(Hz)} {stop(Hz)} {step(Hz) | points} [outmask]
        # example return: ''

        self.print_message("Function does not exist yet. error checking needed")
        return None
    


    def set_IF(self, val=0):
        # the IF call, but avoiding reserved keywords
        # sets the IF to automatic or a specific value. 0 means automatic
        # usage: if ( 0 | 433M..435M )
        # example return: ''

        #check input
        if (val == 0) or (val=='auto'):
            writebyte = 'if '+str(0)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)        
            self.print_message("setIF() set to auto")
        elif ((433*10**6) <=val <=(435*10**6)):
            writebyte = 'if '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)                 
            self.print_message("setIF() set to "  + str(val))       
        else:
            self.print_message("ERROR: if() takes vals ['auto'|0|433M...435M] in Hz as integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_IF1(self, val):
        # TODO: get official documentation blurb
        # usage: if1 {975M..979M}\r\n977.555902MHz
        # example return: ''

        #check input
        if (val == 0) or (val=='auto'):
            writebyte = 'if1 '+str(0)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)      
            self.print_message("setIF1() set to auto")         
        elif ((975*10**6) <=val <=(979*10**6)):
            writebyte = 'if1 '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("setIF() set to "  + str(val))          
        else:
            self.print_message("ERROR: if1() takes vals ['auto'|0|975M...979M] in Hz as integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def info(self):
        # displays various SW and HW information
        # usage: info
        # example return: bytearray(b'tinySA ...\r')

        writebyte = 'info\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("returning device info()")
        return msgbytes 
    
    def level(self, val):
        # sets the output level. Not all values in the range are available
        # usage: level -76..13
        # example return: b''

        # explicitly allowed vals
        accepted_vals =  np.arange(-76, 14, 1) # max exclusive
        #check input
        if val in accepted_vals:
            writebyte = 'level '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("level() set to " + str(val))   
        else:
            self.print_message("ERROR: level() takes vals [-76 to 13]")
            self.print_message("ERROR: value given: " + str(val))
            msgbytes =  self.error_byte_return()
        return msgbytes

    def level_change(self, val):
        # sets the output level delta for low output mode level sweep
        # usage: levelchange -70..+70
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  np.arange(-70, 71, 1) # max exclusive
        #check input
        if (val in accepted_vals):
            writebyte = 'levelchange '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("levelchange() set to " + str(val))           
        else:
            self.print_message("ERROR: levelchange() takes vals [-70 - 70]")
            self.print_message("ERROR: value set to" + str(val))
            msgbytes =  self.error_byte_return()
        return msgbytes

    def level_offset(self):
        # sets or dumps the level calibration data.
        # For the output corrections first ensure correct output 
        # levels at maximum output level. 
        # For the low output set the output to -50dBm and
        # measure and correct the level with 
        # "leveloffset switch error" where for all output 
        # leveloffset commands measure the level with the
        # leveloffset to zero and calculate
        # error = measured level - specified level


        #explicitly allowed vals
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]

        # usage: leveloffset low|high|switch [output] {error}
        msgbytes =  self.error_byte_return()
        self.print_message("Function does not exist yet. error checking needed")
        return None

    def line(self):
        # TODO: get documentation blurb for error checking
        # usage: line off|{level}\
        # example return: ''
        msgbytes =  self.error_byte_return()        
        self.print_message("Function does not exist yet. error checking needed")
        return None

    def load(self, val=0):
        # loads a previously stored preset,where 0 is the startup preset 
        # usage: load [0-4]
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4]
        #check input
        if (val in accepted_vals):
            writebyte = 'load '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)    
            self.print_message("load() called for preset # " + str(val))       
        else:
            self.print_message("ERROR: load() takes vals [0 - 4]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def lna(self, val):
        # toggle lna usage off/on
        # usage: lna off|on
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'lna '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("lna() set to " + str(val))        
        else:
            self.print_message("ERROR: lna() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_lna1_on(self):
        #alias for lna1()
        return self.lna("on")
    def set_lna1_off(self):
        #alias for lna1()
        return self.lna("off")   


    def lna2(self, val="auto"):
        self.print_message("ERROR: lna2() removed until more documentation found")
        return self.error_byte_return()
        # # TODO: get documentation details for any error checking
        # # usage: lna2 0..7|auto
        # # example return: ''

        # #explicitly allowed vals
        # accepted_vals =  [0,1,2,3,4,5,6,7]
        # #check input
        # if (val == "auto") or (val in accepted_vals):
        #     writebyte = 'lna2 '+str(val)+'\r\n'
        #     msgbytes = self.tinySA_serial(writebyte, printBool=False)     
        #     self.print_message("lna2() set to " + str(val))      
        # else:
        #     self.print_message("ERROR: lna2() takes vals [0 - 7]|auto")
        #     msgbytes = self.error_byte_return()
        # return msgbytes

    def set_lna2(self, val):
        #alias for lna2()
        return self.lna2(val) 
    

    def marker(self):
        # TODO 
        # sets or dumps marker info.
        # where id=1..4 index=0..num_points-1
        # Marker levels will use the selected unit.
        # Marker peak will:
        # 1) activate the marker (if not done already), 
        # 2) position the marker on the strongest signal, and
        # 3) display the marker info.
        # The frequency must be within the selected sweep range

        # usage: marker {id} on|off|peak|{freq}|{index}
        # example return: ''
                #explicitly allowed vals
        accepted_vals =  ["on", "off", "peak"]


        msgbytes =  self.error_byte_return()
        self.print_message("Function does not exist yet. error checking needed")
        return None
    
    def set_marker_at_freq(self, marker, freq):
        # by freq
        pass
    def get_marker_value(self, val):
        # by marker val 1-4
        pass

    def turn_on_marker(self, val):
        # turn off marker by number
        pass

    def turn_off_marker(self, val):
        pass




    def menu(self):
        # The menu command can be used to activate any menu item
        # usage: menu {#} [{#} [{#} [{#}]]]
        # example return: ''

        #TODO: check documentation to see if there's any min/max vals 
        # with those settings
        self.print_message("Function does not exist yet. error checking needed")
        return self.error_byte_return()

    def mode(self, val1="low", val2="input"):
        # sets the mode of the tinySA
        # usage: mode low|high input|output
        # example return: ''

        #explicitly allowed vals
        accepted_val1 =  ["low", "high"]
        accepted_val2= ["input", "output"]
        #check input
        if (val1 in accepted_val1) and (val2 in accepted_val2):
            writebyte = 'mode '+str(val1)+ + ' ' +str(val2)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)           
        else:
            self.print_message("ERROR: output() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_low_input_mode(self):
        # alias for mode()
        return self.mode("low", "input")

    def set_low_output_mode(self):
        # alias for mode()
        return self.mode("low", "output")

    def set_high_input_mode(self):
        # alias for mode()
        return self.mode("high", "input")

    # def set_high_output_mode(self):
    #     # alias for mode()
    #     # TODO: ERROR CHECKING
    #     return self.mode("high", "output")

    def modulation(self):
        # sets the modulation in output mode
        # usage: modulation off|AM_1kHz|AM_10Hz|NFM|WFM|extern
        # example return: ''


        #explicitly allowed vals
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]


        msgbytes =  self.error_byte_return()
        self.print_message("Function does not exist yet. error checking needed")
        return None

    def nf(self):
        # TODO: get documentation blurb to see if any error checking
        # usage: nf {value}\r\n5.000000000
        # example return: ''
        self.print_message("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'nf\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        return msgbytes

    def output(self, val):
        # sets the output on or off
        # usage: output on|off
        # example return: ''

        # explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'output '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)           
        else:
            self.print_message("ERROR: output() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_output_on(self):
        #alias for output()
        return self.output("on") 
    
    def set_output_off(self):
        #alias for output()
        return self.output("off")     

    def pause(self):
        # pauses the sweeping in either input or output mode
        # usage: pause
        # example return: ''

        writebyte = 'pause\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("pausing tinySA device")
        return msgbytes 

    def rbw(self, val="auto"):
        # sets the rbw to either automatic or a specific value.
        # the number specifies the target rbw in kHz
        # usage: rbw auto|3..600 
        # example return: ''

        #check input
        if (val == "auto"):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)                
        elif (isinstance(val, int)) and (3*10**3<= val <=600*10**3):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)           
        else:
            self.print_message("ERROR: rbw() takes vals [auto |0 - 600] in kHz as integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def recall(self, val=0):
        # loads a previously stored preset,where 0 is the startup preset 
        # usage: recall [0-4]
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4]
        #check input
        if (val in accepted_vals):
            writebyte = 'recall '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("recall() set to value " + str(val))           
        else:
            self.print_message("ERROR: recall() takes vals [0 - 4]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def refresh(self, val):
        # enables/disables the auto refresh mode
        # usage: refresh on|off
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'refresh '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("refresh() set to " + str(val))           
        else:
            self.print_message("ERROR: refresh() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_refresh_on(self):
        # alias for refresh()
        return self.refresh("on")

    def set_refresh_off(self):
        # alias for refresh()
        return self.refresh("off")

    def release(self):
        # signals a removal of the touch
        # usage: release
        # example return: bytearray(b'')

        writebyte = 'release\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("sending touch release signal")
        return msgbytes 

    def remark(self):
        # TODO: get info on exactly what this is, does, and the format
        # usage: repeat
        # example return: bytearray(b'')
        self.print_message("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'remark\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        return msgbytes 

    def repeat(self, val=1):
        # Sets the number of (re)measurements that should be taken at every frequency
        # usage: repeat
        # example return: bytearray(b'')

        val = int(val)
        if (1<=val) and (val<=1000):
            writebyte = 'repeat ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("setting the repeat() measurement to " + str(val))
        else:
            self.print_message("ERROR: repeat() takes integer vals [0 - 1000]")
            msgbytes = self.error_byte_return()
        return msgbytes 

    def reset(self):
        # reset the tinySA Ultra. NOTE: will disconnect and fully reset
        # usage: reset
        # example return: throws error. raise SerialException

        writebyte = 'reset\r\n'
        self.print_message("sending reset() signal. Serial will disconnect...")
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        return msgbytes 

    def restart(self, val=0):
        # TODO: add this back with some error checking
        # had an oops to fix
        # restarts the  tinySA after the specified number of seconds
        # usage: restart {seconds}
        # example return: ''
        # val = int(val)
        # if val == 0:
        #     writebyte = 'restart ' + str(val) + '\r\n'
        #     msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        #     self.print_message("restarting cancelled.")       
        # elif (0<val):
        #     writebyte = 'restart ' + str(val) + '\r\n'
        #     msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        #     self.print_message("restarting the device in " + str(val) + " seconds.")
        # else:
        #     self.print_message("ERROR: restart() takes vals 0 or greater")
        #     msgbytes = self.error_byte_return()

        # # not recognized by device
        # if (msgbytes == b'restart?\r'):
        #     print("!!")

        self.print_message("ERROR: restart() funciton REMOVED")
        return self.error_byte_return() 

    def resume(self):
        # resumes the sweeping in either input or output mode
        # usage: resume
        # example return: ''

        writebyte = 'resume\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("resuming sweep")
        return msgbytes 

    def save(self, val=1):
        # saves the current setting to a preset, where 0 is the startup preset
        # usage: save [0-4]
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4]
        #check input
        if (val in accepted_vals):
            writebyte = 'save '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("saving to preset " + str(val))           
        else:
            self.print_message("ERROR: save() takes vals [0 - 4] as integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def save_config(self):
        # saves the device configuration data
        # usage: saveconfig
        # example return: bytearray(b'Config saved.\r')

        writebyte = 'saveconfig\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("save_config() called")
        return msgbytes

    def scan(self):
        # TODO: documentation for err checking
        # Performs a scan and optionally outputs the measured data.
        # usage: scan {start(Hz)} {stop(Hz)} [points] [outmask]
            # where the outmask is a binary OR of:
            # 1=frequencies, 2=measured data,
            # 4=stored data and points is maximum is 290
        self.print_message("Function does not exist yet. error checking needed")
        return None
    
    def run_scan(self):
        # 
        pass




    def scan_raw(self):
        # TODO: documentation for err checking
        # performs a scan of unlimited amount of points 
        # and send the data in binary form
        # usage: scanraw {start(Hz)} {stop(Hz)} [points]
            # The measured data is send as:
            #  '{' ('x' MSB LSB)*points '}' 
            # where the 16 bit data is scaled by 32.

        self.print_message("Function does not exist yet. error checking needed")
        return None
    
    def sd_delete(self):
        # delete a specific file on the sd card
        # usage: sd_delete {filename}
        # example return:

        self.print_message("Function does not exist yet. error checking needed")
        return None
    
    def sd_list(self):
        # displays list of filenames with extension and sizes
        # usage: sd_list
        # example return: bytearray(b'-0.bmp 307322\r')

        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("listing files from sd card")
        return msgbytes 

    def sd_read(self):
        # read a specific file on the sd_card
        # usage: sd_read {filename}
        # example return: 

        self.print_message("Function does not exist yet. error checking needed")
        return None

    def self_test(self, val=0):
        # performs one or all selftests
        # usage: selftest 0 0..9
        # 0 appears to be 'run all'
        # example return: msgbytes = bytearray(b'')

        # explicitly allowed vals
        accepted_vals =  np.arange(0, 15, 1) # max exclusive
        #check input
        if (val in accepted_vals):
            writebyte = 'selftest ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("SELFTEST RUNNING. CHECK CONNECTION CAL to RF")           
        else:
            self.print_message("ERROR: self_test() takes vals [0-15]")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def spur(self, val):
        # enables or disables spur reduction
        # usage: spur on|off
        # example return:

        # explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (val in accepted_vals):
            writebyte = 'spur '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("spur() set to " + str(val))           
        else:
            self.print_message("ERROR: spur() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def set_spur_on(self):
        # alias for spur()
        return self.spur("on")
    def set_spur_off(self):
        # alias for spur()
        return self.spur("off")
    
    def status(self):
        # displays the current device status (paused/resumed)
        # usage: status
        # example return: bytearray(b'Resumed\r')
       
        writebyte = 'status\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("getting device status() paused/resumed")
        return msgbytes

    
    def sweep(self, argName=None, val=None): # pts=None):
            # Set sweep boundaries or execute a sweep.
            # Sweep without arguments lists the current sweep 
            # settings. The frequencies specified should be 
            # within the permissible range. The sweep commands 
            # apply both to input and output modes        
            # usage: 
            # sweep [(start|stop|center|span|cw {frequency}) | 
            #   ({start(Hz)} {stop(Hz)} [0..290])]
            # # example return:  

        # explicitly allowed vals
        accepted_table_args = ["start", "stop", "center", 
                               "span", "cw"]

        if (argName==None) and (val==None):
            # do sweep
            writebyte = 'sweep\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)

        elif (argName in accepted_table_args): 
            if val == None:
                #error
                self.print_message("ERROR: sweep " + str(argName) + " needs a value")
                msgbytes = self.error_byte_return()
            else:
                #do stuff, error checking needed
                writebyte = 'sweep ' + str(argName)+ ' ' + str(val)+ '\r\n'
                self.print_message("sweep " +str(argName) + " is " + str(val))
                msgbytes = self.tinySA_serial(writebyte, printBool=False)

        else: #not in table of accepted args, so doesn't matter what val is
            self.print_message("ERROR: " + str(argName) + " invalid argument for sweep")
            msgbytes = self.error_byte_return()

        return msgbytes

    def set_sweep_start(self, val):
        return self.sweep("start", val)
    
    def set_sweep_stop(self, val):
        return self.sweep("stop", val)
    
    def set_sweep_center(self, val):
        return self.sweep("center", val)
    
    def set_sweep_span(self, val):
        return self.sweep("span", val)
    
    def set_sweep_cw(self, val):
        return self.sweep("cw", val)    

    def set_sweep_range(self, startVal=None, stopVal=None):
        if (startVal==None) or (stopVal==None):
            self.print_message("ERROR: sweep start and stop need non-empty values")
            msgbytes = self.error_byte_return()
        elif (int(startVal) >= int(stopVal)):
            self.print_message("ERROR: sweep start must be less than sweep stop value")
            msgbytes = self.error_byte_return()
        else:
            # start
            msgbytes1 = self.set_sweep_start(startVal)
            # stop
            msgbytes2 = self.set_sweep_stop(stopVal)
            # combine (for now)
            msgbytes = msgbytes1 + "\n" + msgbytes2
        return msgbytes 

    def sweep_time(self):
        # TODO
        # sets the sweeptime
        # usage: sweep {time(Seconds)}the time
        # specified may end in a letter where
        # m=mili and u=micro
        self.print_message("Function does not exist yet. error checking needed")
        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("listing files from sd card")
        return msgbytes 


    def text(self, val=""):
        # TODO
        self.print_message("Function does not exist yet. error checking needed")
        
        if len(str(val))>0:
            writebyte = 'text ' + str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("text() entered is " + str(val))
        else:
            self.print_message("ERROR: text needs non-empty values")
            msgbytes = self.error_byte_return()
        return msgbytes 

    def threads(self):
        # lists information of the threads in the tinySA
        # usage: threads
        # example return:
        # bytearray(b'stklimit| ...\r')
        
        writebyte = 'threads\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("returning thread information for device")
        return msgbytes

    def touch(self, x=0, y=0):
        # sends the coordinates of a touch. 
        # The upper left corner of the screen is 0 0
        # usage: touch {X coordinate} {Y coordinate}
        # example return:

        # check if valid x
        if (x<0) or (self.screenWidth<x):
            self.print_message("ERROR: touch() needs a valid x coordinate")
            msgbytes = self.error_byte_return()
            return msgbytes 
        # check if valid y
        if (y<0) or (self.screenHeight<y):
            self.print_message("ERROR: touch() needs a valid y coordinate")
            msgbytes = self.error_byte_return()
            return msgbytes 
        writebyte = 'touch ' + str(x) + ' ' + str(y) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("setting the touch() (" + str(x)+"," + str(y) + ")")
        return msgbytes 

    def touch_cal(self):
        # starts the touch calibration
        # usage: touchcal
        # example return: bytearray(b'')
        writebyte = 'touchcal\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("starting touchcal")
        return msgbytes
    
    def start_touch_cal(self):
        return self.touch_cal()

    def touch_test(self):
        # starts the touch test
        # usage: touchtest
        # example return: bytearray(b'')
        
        writebyte = 'touchtest\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("starting the touch_test()")
        return msgbytes
    
    def start_touch_test(self):
        return self.touch_test()

    def trace(self):
        # TODO: get documentation for err checking
        # displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 
        self.print_message("Function does not exist yet. error checking needed")
        return None

    def trigger(self):
        #TODO
        # sets the trigger type or level
        # usage: trigger auto|normal|single| 
        # {level(dBm)}
        # the trigger level is always set in dBm
        # example return:  

        self.print_message("Function does not exist yet. error checking needed")
        return None

    def ultra(self, val="off", freq=None):
        # turn on/config tiny SA ultra mode
        # usage: ultra off|on|auto|start|harm {freq}
        # example return: bytearray(b'')

        # #explicitly allowed vals
        accepted_vals =  ["off", "on"] #, "auto", "start", "harm"]        

        if val in accepted_vals:
            writebyte = 'ultra ' + str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("configuring ultra() " + str(val))
        else:
            self.print_message("ERROR: ultra() currently only takes on/off as args")
            msgbytes = self.error_byte_return()

        return msgbytes
    
    def set_ultra_on(self):
        return self.ultra("on")
    
    def set_ultra_off(self):
        return self.ultra("off")
    
    def set_ultra_auto(self):
        return self.ultra("auto")
    
    def set_ultra_start(self):
        return self.ultra("start")
       
    def set_ultra_harmonic(self):
        return self.ultra("harm")

    def usart_cfg(self):
        # gets the current serial config
        # usage: usart_cfg
        # example return: bytearray(b'Serial: 115200 baud\r')
        
        writebyte = 'usart_cfg\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("usart_cfg() returning config vals")
        return msgbytes

    def vbat(self):
        # displays the battery voltage
        # usage: vbat
        # example return: bytearray(b'4132 mV\r')
        writebyte = 'vbat\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("returning current battery voltage")
        return msgbytes

    def get_vbat(self):
        # alias for vbat
        return self.vbat()

    def vbat_offset(self, val=None):
        # displays or sets the battery offset value
        # usage: vbat_offset [{0..4095}]
        # example return: bytearray(b'300\r')

        if val == None:
            #get the offset       
            writebyte = 'vbat_offset\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (0<= val <=4095):
            writebyte = 'vbat_offset '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("vbat_offset set to " + str(val))
        else:
            self.print_message("ERROR: vbat_offset() takes either None or [0 - 4095] integers")
            msgbytes = self.error_byte_return()
        return msgbytes
    
    def get_vbat_offset(self):
        # alias for vbat_offset()
        return self.vbat_offset()

    def version(self):
        # displays the version text
        # usage: version
        # example return: tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1
       
        writebyte = 'version\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("getting device version information")
        return msgbytes
    
    def get_version(self):
        # alias for version()
        return self.version()

    def wait(self, val=0):
        # TODO

        if val == None:
            writebyte = 'wait\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("device in wait() state. manually resume")
        elif val>0:
            writebyte = 'wait ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("device wait() trigged for " + str(val) + " seconds.")
        else:
            self.print_message("ERROR: wait() takes None or positive ints")
            msgbytes = self.error_byte_return()


    def zero(self):
        # TODO: get info on exactly what this is, does, and the format
        # usage: zero {level}\r\n174dBm
        # example return:

        self.print_message("Function does not exist yet. error checking needed")
        return None


######################################################################
# Device and library help
######################################################################

    def help(self, val=0):
        # val controls if the tinySA help is called or the 
        # 1 = library_help(), everything else is the tinySA_help()

        if val == 1:
            msgbytes = self.library_help() 
        else:
            msgbytes = self.tinySA_help()    
        return msgbytes

    def library_help(self):
        self.print_message("Returning command options for this library")
        self.print_message("IN PROGRESS. Include tinySA_help.py")

        return b''

    def tinySA_help(self):
        # dumps a list of the available commands
        # usage: help
        # example return: bytearray(b'commands: freq time dac 
        # nf saveconfig clearconfig zero sweep pause resume wait
        #  repeat status caloutput save recall trace trigger
        #  marker line usart_cfg vbat_offset color if if1 lna2 
        # agc actual_freq freq_corr attenuate level sweeptime
        #  leveloffset levelchange modulation rbw mode spur 
        # lna direct ultra load ext_gain output deviceid 
        # correction calc menu text remark\r\nOther commands:
        #  version reset data frequencies scan hop scanraw test 
        # touchcal touchtest usart capture refresh touch release
        #  vbat help info selftest sd_list sd_read sd_delete 
        # threads\r')

        writebyte = 'help\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("Returning command options for tinySA device")
        return msgbytes



######################################################################
# Device Selection and Config Functions
# TODO LATER
# This is a quick template. there's more options that need to 
# be researched
######################################################################




######################################################################
# Unit testing
######################################################################

if __name__ == "__main__":
    # unit testing. not recomended to write program from here

    # create a new tinySA object    
    tsa = tinySA()
    # attempt to connect to previously discovered serial port
    success = tsa.connect(port='COM10')

    # if port open, then complete task(s) and disconnect
    if success == True:
        tsa.set_verbose(True) #detailed messages
        tsa.set_error_byte_return(True) #get explicit b'ERROR'
        msg = tsa.wait() 
        print(msg)
        

        tsa.disconnect()
    else:
        print("ERROR: could not connect to port")

