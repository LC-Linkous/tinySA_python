#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python 
#   './tinySA_python.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Author(s): Lauren Linkous
#   Last update: January 24, 2025
##--------------------------------------------------------------------------------------------------\

import serial
import numpy as np
import re

class tinySA():
    def __init__(self, parent=None):
        # serial port
        self.ser = None 

        # message feedback
        self.verboseEnabled = False
        self.returnErrorByte = False

        # other overrides
        self.ultraEnabled = False
        self.abortEnabled = False

        #select device vars - hardcoding for the Ultra for now
        self.deviceType = "ultra"
        # spectrum analyzer
        self.minSADeviceFreq = 100000  #100 kHz
        self.maxSADeviceFreq = 5300000000 #5.3 GHz
        # signal generator
        self.minSGDeviceFreq = 100000  #100 kHz
        self.maxSGDeviceFreq = 960000000 #960 MHz
        # battery
        self.maxDeviceBattery = 4095
        # screen 
        self.screenWidth = 320
        self.screenHeight = 240


######################################################################
# Error and information printout
# set/getVerbose()  - set how detailed the error printouts are
# printMessage()  - deal with the bool in one place
######################################################################

    def setVerbose(self, verbose=False):
        self.verboseEnabled = verbose

    def getVerbose(self):
        return self.verboseEnabled

    def printMessage(self, msg):
        if self.verboseEnabled == True:
            print(msg)

######################################################################
# Explicit error return
# set/getErrorByteReturn()  - set how detailed the error printouts are
# printMessage()  - deal with the bool in one place
######################################################################

    def setErrorByteReturn(self, errByte=False):
        self.returnErrorByte = errByte

    def getErrorByteReturn(self):
        return self.returnErrorByte

    def errorByteReturn(self):
        if self.returnErrorByte == True:
            return bytearray(b'ERROR')
        else:
            return bytearray(b'') # the default

######################################################################
# Direct error checking overrides
#   These are used during DEBUG or when device state is already known
#   Not recommended unless you are sure of the device state
######################################################################

    def setUltraMode(self, ultraMode=False):
        self.ultraEnabled = ultraMode

    def setAbortMode(self, abortMode=False):
        self.abortEnabled = abortMode

######################################################################
# Device Selection and Config Functions
# TODO
# This is a quick template. there's more options that need to 
# be researched
######################################################################

    def setDevice(self, val="ultra"):
        self.deviceType = val
        if val == "original":
            self.setDeviceOriginal()
        elif val == "ultra":
            self.setDeviceUltra()
        elif val == "plus":
            self.setDeviceUltraPlus()
        else:
            self.printMessage("ERROR: unrecognized device type")

    def setDeviceOriginal(self):
        # pull the device configs and set vals
        self.printMessage("IN PROGRESS. device config not available yet")
        # spectrum analyzer
        self.minSADeviceFreq = 100000  #100 kHz
        self.maxSADeviceFreq = 5300000000 #5.3 GHz
        # signal generator
        # MF/HF/VHF sin wave 100 kHz - 350 MHz
        # UHF Square wave 240 MHz - 960 MHz
        # mixing signal output ??
        self.minSGDeviceFreq = 100000  #100 kHz
        self.maxSGDeviceFreq = 960000000 #960 MHz
        # battery
        self.maxDeviceBattery = 4095
        # screen 
        self.screenWidth = 320
        self.screenHeight = 240

    def setDeviceUltra(self):
        # pull the device configs and set vals
        self.printMessage("IN PROGRESS. device config not available yet")
        # spectrum analyzer
        self.minSADeviceFreq = 100000  #100 kHz
        self.maxSADeviceFreq = 5300000000 #5.3 GHz
        # signal generator
        # MF/HF/VHF sin wave 100 kHz - 800 MHz
        # UHF Square wave 800 MHz - 4.4 GHz
        # mixing signal output 4.4 GHz - 5.4 GHz
        self.minSGDeviceFreq = 100000  #100 kHz
        self.maxSGDeviceFreq = 5400000000 #5.4 GHz
        # battery
        self.maxDeviceBattery = 4095
        # screen 
        self.screenWidth = 480
        self.screenHeight = 320

    def setDeviceUltraPlus(self):
        # pull the device configs and set vals
        self.printMessage("IN PROGRESS. device config not available yet")
        return

######################################################################
# Serial management and message processing
######################################################################

    def connect(self, port, timeout=1):
        # attempt connection to provided port. 
        # returns: True if successful, False otherwise

        try:
            self.ser = serial.Serial(port=port, timeout=timeout)
            return True
        except Exception as err:
            self.printMessage("ERROR: cannot open port at " + str(port))
            self.printMessage(err)
            return False

    def disconnect(self):
        # closes the serial port
        self.ser.close()

    def tinySASerial(self, writebyte, printBool=False):
        # write out to serial, get message back, clean up, return
        
        self.ser.write(bytes(writebyte, 'utf-8'))
        msgbytes = self.getSerialReturn()
        msgbytes = self.cleanReturn(msgbytes)

        if printBool == True:
            print(msgbytes) #overrides verbose for debug

        return msgbytes

    def getSerialReturn(self):
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
                    self.printMessage("ERROR: exception thrown while reading serial")
                    self.printMessage(err)
                    return None
                break
        return bytearray(complete)

    def cleanReturn(self, data):
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
# Device and library help
######################################################################

    def help(self, val=0):
        # val controls if the tinySA help is called or the 
        # 1 = libraryHelp(), everything else is the tinySAHelp()

        if val == 1:
            msgbytes = self.libraryHelp() 
        else:
            msgbytes = self.tinySAHelp()    
        return msgbytes

    def libraryHelp(self):
        self.printMessage("Returning command options for this library")
        self.printMessage("IN PROGRESS. Include tinySA_help.py")

        return b''

    def tinySAHelp(self):
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
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("Returning command options for tinySA device")
        return msgbytes

######################################################################
# Reusable format checking functions
######################################################################

    def is_rgb24(self, hexStr):
        # check if the string matches the pattern 0xRRGGBB
        pattern = r"^0x[0-9A-Fa-f]{6}$"
        return bool(re.match(pattern, hexStr))


######################################################################
# Serial command config, input error checking
######################################################################

    def abort(self, val=None):
        # Sets the abortion enabled status (on/off)
        # usage: abort [off|on]
        # example return: bytearray(b'')

        self.printMessage("ABORT function not enabled in developer's DUT")
        msgbytes = bytearray(b'')
        return msgbytes

        # #explicitly allowed vals
        # accepted_vals =  ["off", "on"]        

        # #check input
        # if (val in accepted_vals): #toggle state
        #     writebyte = 'abort '+str(val)+'\r\n'
        #     msgbytes = self.tinySASerial(writebyte, printBool=False) 
        #     if val == "on":
        #         self.printMessage("ABORT option ENABLED")
        #         self.abortEnabled = True
        #     elif val == "off":
        #         self.printMessage("ABORT option DISABLED")
        #         self.abortEnabled = False
        # elif val == None: #action
        #     if self.abortEnabled == True:
        #         writebyte = 'abort\r\n'
        #         msgbytes = self.tinySASerial(writebyte, printBool=False) 
        #     else:
        #         self.printMessage("ABORT option must be ENABLED before use")
        #         msgbytes = bytearray(b'')
        # else:
        #     self.printMessage("ERROR: abort() takes NONE|\"off\"|\"on\" as arguments")
        #     msgbytes = bytearray(b'')
        # return msgbytes

    def actual_freq(self, val=None):
        # Gets the frequency correction set by CORRECT FREQUENCY 
        #   menu in the expert menu settings
        # usage: actual_freq [{frequency in Hz}]
        # example return: bytearray(b'3000000000\r')

        if val == None:
            #get the dac       
            writebyte = 'actual_freq\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (self.minSADeviceFreq <= val <=self.maxSADeviceFreq ):
            writebyte = 'actual_freq '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("actual_freq set to " + str(val))
        else:
            self.printMessage("ERROR: actual_freq() takes either None or integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def agc(self, val='auto'):
        # Enables/disables the build in Automatic Gain Control
        # usage: agc 0..7|auto
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 8, 1) # max exclusive
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'agc '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)     
            self.printMessage("agc() set with " + str(val))
        else:
            self.printMessage("ERROR: agc() takes vals [0 - 7]|\"auto\"")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def attenuate(self, val='auto'):
        # sets the internal attenuation to automatic or a specific value
        # usage: attenuate [auto|0-31]
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 31, 1) # max exclusive
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'attenuate '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("attenuate() set with " + str(val))           
        else:
            self.printMessage("ERROR: attenuate() takes vals [0 - 31]|\"auto\"")
            msgbytes = self.errorByteReturn()
        return msgbytes
    
    def bulk(self):
        # sent by tinySA when in auto refresh mode
        # format: "bulk\r\n{X}{Y}{Width}{Height}
        # {Pixeldata}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian. The Pixeldata is
        # encoded as 2 bytes per pixel

        self.printMessage("BULK function not enabled in developer's DUT")
        msgbytes = bytearray(b'')
        return msgbytes

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
            msgbytes = self.tinySASerial(writebyte, printBool=False)     
            self.printMessage("calc() set with " + str(val))
        else:
            self.printMessage("ERROR: calc() takes vals \"off\"|\"minh\"|\"maxh\"|\"maxd\"|\"aver4\"|\"aver16\"|\"quasip\"")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def caloutput(self, val="off"):
        # disables or sets the caloutput to a specified frequency in MHz
        # usage: caloutput off|30|15|10|4|3|2|1
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  ["off", 1,2,3,4,10,15,30]
        #check input
        if (val in accepted_vals):
            writebyte = 'caloutput '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("caloutput() set with " + str(val))        
        else:
            self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
            msgbytes = self.errorByteReturn()
        return msgbytes
    
    def capture(self):
        # requests a screen dump to be sent in binary format 
        # of 320x240 pixels of each 2 bytes
        # usage: capture
        # example return: bytearray(b'\x00 ...\x00\x00\x00')
        writebyte = 'capture\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("capture() called for screen data")   
        return msgbytes

    def clearconfig(self):
        # resets the configuration data to factory defaults. requires password
        # NOTE: does take other commands to fully clear all
        # usage: clearconfig 1234
        # example return: bytearray(b'Config and all cal data cleared.
        # \r\nDo reset manually to take effect. 
        # Then do touch cal and save.\r')
        writebyte = 'clearconfig 1234\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("clearconfig() with password. Config and all cal data cleared. \
                          Reset manually to take effect.")
        return msgbytes

    def color(self, ID=None, RGB='0xF8FCF8'):
        # sets or dumps the colors used
        # usage: color [{id} {rgb24}]
        # example return: 
         
        # explicitly allowed vals
        accepted_ID = np.arange(0, 31, 1) # max exclusive

        if ID == None:
            # get the color       
            writebyte = 'color\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
        elif (ID in accepted_ID) and (self.is_rgb24(RGB)==True):
            # set the color based on ID       
            writebyte = 'color ' + str(ID) + ' ' + str(RGB) + '\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("color() set with ID: " +str(ID) + " RGB: " + str(RGB))
        else:
            self.printMessage("ERROR: color() takes either None, or ID as int 0..31 and RGB as a hex value")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def correction(self, tableName="low", slot=None, freq=None, val=None):
        # sets or dumps the frequency level orrection table
        # usage: correction [0..9 {frequency} {level dB}]
        # usage: correction low|lna|ultra|ultra_lna|direct|direct_lna|harm|harm_lna|out|out_direct|out_adf|out_ultra|off|on 0-19 frequency(Hz) value(dB)
        # example return:  

        # explicitly allowed vals
        accepted_table_name = ["low", "lna", "ultra", "ultra_lna", 
                               "direct", "direct_lna",  "harm", 
                               "harm_lna", "out", "out_direct", 
                               "out_adf", "out_ultra", "off", "on"]

        accepted_slots = np.arange(0, 20, 1) # max exclusive. 

        if (tableName in accepted_table_name) and (slot==None):
            # prints out the table as it currently is
            writebyte = 'correction ' + str(tableName)+ '\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
        else:
            # check error conditions quickly since there's 4
            if not(tableName in accepted_table_name):
                self.printMessage("ERROR: correction() requires a table indicator. see documentation")
                msgbytes = self.errorByteReturn()
                return msgbytes
            if not(slot in accepted_slots):
                self.printMessage("ERROR: correction() requires a slot from ["+ str(accepted_slots) + "]. see documentation")
                msgbytes = self.errorByteReturn()
                return msgbytes
            if not(self.minSADeviceFreq<=freq) and not(freq<=self.maxSADeviceFreq):
                self.printMessage("ERROR: correction() frequency outside of device specs. see documentation")
                msgbytes = self.errorByteReturn()
                return msgbytes
            if not(-10<=val) and not(val<=35):
                self.printMessage("ERROR: correction() val dB outside of  specs. see documentation")
                msgbytes = self.errorByteReturn()
                return msgbytes
            writebyte = 'correction ' + str(tableName) + ' ' + str(slot) +\
                    ' ' + str(freq) + ' ' + str(val) + '\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("correction() set with " + str(tableName) + " " + str(slot) +\
                    " " + str(freq) + " " + str(val))
 
        return msgbytes

    def dac(self, val=None):
        # sets or dumps the dac value
        # usage: dac [0..4095]
        # example return: bytearray(b'usage: dac {value(0-4095)}\r\ncurrent value: 1922\r')  

        if val == None:
            #get the dac       
            writebyte = 'dac\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (0<= val <=4095):
            writebyte = 'dac '+str(id)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("dac set to " + str(id))
        else:
            self.printMessage("ERROR: dac() takes either None or integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

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
            msgbytes = self.tinySASerial(writebyte, printBool=False)  
            if val == 0:
                self.printMessage("returning temp value data") 
            elif val == 1:
                self.printMessage("returning stored trace data") 
            elif val == 2:
                self.printMessage("returning measurement data") 
        else:
            self.printMessage("ERROR: data() takes vals [0-2]")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def deviceid(self, id=None):
        # sets or dumps a user settable number that can be used to identify a specific tinySA
        # usage: deviceid [{number}]
        # example return: bytearray(b'deviceid 12\r')

        if id == None:
            #get the device ID        
            writebyte = 'deviceid\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif isinstance(id, int):
            writebyte = 'deviceid '+str(id)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("device ID set to " + str(id))
        else:
            self.printMessage("ERROR: deviceid() takes either None or integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def direct(self):
        # ??
        # usage: direct {start|stop|on|off} {freq(Hz)}
        # example return: ''

        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def ext_gain(self, val):
        # sets the external attenuation/amplification.
        # Works in both input and output mode
        # usage: ext_gain -100..100
        # example return: ''        
        
        #check input
        if (isinstance(val, int)) and (-100<= val <=100):
            writebyte = 'ext_gain '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("ext_gain() set to " + str(val))       
        else:
            self.printMessage("ERROR: ext_gain() takes vals [-100 - 100]")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def fill(self):
        # sent by tinySA when in auto refresh mode
        # format: "fill\r\n{X}{Y}{Width}{Height}
        # {Color}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian.

        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def freq(self, val):
        # pauses the sweep and sets the measurement frequency.
        # usage: freq {frequency}
        # example return: bytearray(b'')

        #check input
        if (isinstance(val, int)) and (self.minSADeviceFreq<= val <=self.maxSADeviceFreq):
            writebyte = 'freq '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("freq() set to " + str(val))       
        else:
            self.printMessage("ERROR: freq() takes integer vals [100 kHz - 5.3 GHz] as Hz for the tinySA Ultra")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def freq_corr(self):
        # get frequency correction
        # usage: freq_corr
        # example return: bytearray(b'0 ppb\r')

        writebyte = 'freq_corr\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("getting frequency correction")
        return msgbytes

    def frequencies(self):
        # gets the frequencies used by the last sweep
        # usage: frequencies
        # example return: bytearray(b'1500000000\r\n... \r\n3000000000\r')

        writebyte = 'frequencies\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("getting frequencies from the last sweep")
        return msgbytes

    def hop(self):
        # TODO: get documentation def of what the function is and the limits   
        # usage: hop {start(Hz)} {stop(Hz)} {step(Hz) | points} [outmask]
        # example return: ''

        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def setIF(self, val=0):
        # the IF call, but avoiding reserved keywords
        # sets the IF to automatic or a specific value. 0 means automatic
        # usage: if ( 0 | 433M..435M )
        # example return: ''

        #check input
        if (val == 0) or (val=='auto'):
            writebyte = 'if '+str(0)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)        
            self.printMessage("setIF() set to auto")
        elif ((433*10**6) <=val <=(435*10**6)):
            writebyte = 'if '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)                 
            self.printMessage("setIF() set to "  + str(val))       
        else:
            self.printMessage("ERROR: if() takes vals ['auto'|0|433M...435M] in Hz as integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def setIF1(self, val):
        # TODO: get official documentation blurb
        # usage: if1 {975M..979M}\r\n977.555902MHz
        # example return: ''

        #check input
        if (val == 0) or (val=='auto'):
            writebyte = 'if1 '+str(0)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)      
            self.printMessage("setIF1() set to auto")         
        elif ((975*10**6) <=val <=(979*10**6)):
            writebyte = 'if1 '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("setIF() set to "  + str(val))          
        else:
            self.printMessage("ERROR: if1() takes vals ['auto'|0|975M...979M] in Hz as integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def info(self):
        # displays various SW and HW information
        # usage: info
        # example return: bytearray(b'tinySA ...\r')

        writebyte = 'info\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("returning device info()")
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("level() set to " + str(val))   
        else:
            self.printMessage("ERROR: level() takes vals [-76 to 13]")
            self.printMessage("ERROR: value given: " + str(val))
            msgbytes =  self.errorByteReturn()
        return msgbytes

    def levelchange(self, val):
        # sets the output level delta for low output mode level sweep
        # usage: levelchange -70..+70
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  np.arange(-70, 71, 1) # max exclusive
        #check input
        if (val in accepted_vals):
            writebyte = 'levelchange '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("levelchange() set to " + str(val))           
        else:
            self.printMessage("ERROR: levelchange() takes vals [-70 - 70]")
            self.printMessage("ERROR: value set to" + str(val))
            msgbytes =  self.errorByteReturn()
        return msgbytes

    def leveloffset(self):
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
        msgbytes =  self.errorByteReturn()
        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def line(self):
        # TODO: get documentation blurb for error checking
        # usage: line off|{level}\
        # example return: ''
        msgbytes =  self.errorByteReturn()        
        self.printMessage("Function does not exist yet. error checking needed")
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)    
            self.printMessage("load() called for preset # " + str(val))       
        else:
            self.printMessage("ERROR: load() takes vals [0 - 4]")
            msgbytes = self.errorByteReturn()
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("lna() set to " + str(val))        
        else:
            self.printMessage("ERROR: lna() takes vals [on|off]")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def lna2(self, val="auto"):
        self.printMessage("ERROR: lna2() removed until more documentation found")
        return self.errorByteReturn()
        # # TODO: get documentation details for any error checking
        # # usage: lna2 0..7|auto
        # # example return: ''

        # #explicitly allowed vals
        # accepted_vals =  [0,1,2,3,4,5,6,7]
        # #check input
        # if (val == "auto") or (val in accepted_vals):
        #     writebyte = 'lna2 '+str(val)+'\r\n'
        #     msgbytes = self.tinySASerial(writebyte, printBool=False)     
        #     self.printMessage("lna2() set to " + str(val))      
        # else:
        #     self.printMessage("ERROR: lna2() takes vals [0 - 7]|auto")
        #     msgbytes = self.errorByteReturn()
        # return msgbytes

    def marker(self):
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
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]

        msgbytes =  self.errorByteReturn()
        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def menu(self):
        # The menu command can be used to activate any menu item
        # usage: menu {#} [{#} [{#} [{#}]]]
        # example return: ''

        #TODO: check documentation to see if there's any min/max vals 
        # with those settings
        self.printMessage("Function does not exist yet. error checking needed")
        return self.errorByteReturn()

    def mode(self, val="low", devMode="input"):
        # sets the mode of the tinySA
        # usage: mode low|high input|output
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]


        writebyte = 'mode\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes
        # self.printMessage("Function does not exist yet. error checking needed")
        # return self.errorByteReturn()

    def modulation(self):
        # sets the modulation in output mode
        # usage: modulation off|AM_1kHz|AM_10Hz|NFM|WFM|extern
        # example return: ''


        #explicitly allowed vals
        accepted_vals =  ["off", "minh", "maxh", "maxd", 
                          "aver4", "aver16", "quasip"]


        msgbytes =  self.errorByteReturn()
        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def nf(self):
        # TODO: get documentation blurb to see if any error checking
        # usage: nf {value}\r\n5.000000000
        # example return: ''
        self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'nf\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            self.printMessage("ERROR: output() takes vals [on|off]")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def pause(self):
        # pauses the sweeping in either input or output mode
        # usage: pause
        # example return: ''

        writebyte = 'pause\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("pausing tinySA device")
        return msgbytes 

    def rbw(self, val="auto"):
        # sets the rbw to either automatic or a specific value.
        # the number specifies the target rbw in kHz
        # usage: rbw auto|3..600 
        # example return: ''

        #check input
        if (val == "auto"):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)                
        elif (isinstance(val, int)) and (3*10**3<= val <=600*10**3):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)           
        else:
            self.printMessage("ERROR: rbw() takes vals [auto |0 - 600] in kHz as integers")
            msgbytes = self.errorByteReturn()
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("recall() set to value " + str(val))           
        else:
            self.printMessage("ERROR: recall() takes vals [0 - 4]")
            msgbytes = self.errorByteReturn()
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("refresh() set to " + str(val))           
        else:
            self.printMessage("ERROR: refresh() takes vals [on|off]")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def release(self):
        # signals a removal of the touch
        # usage: release
        # example return: bytearray(b'')

        writebyte = 'release\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("sending touch release signal")
        return msgbytes 

    def remark(self):
        # TODO: get info on exactly what this is, does, and the format
        # usage: repeat
        # example return: bytearray(b'')
        self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'remark\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 

    def repeat(self, val=1):
        # Sets the number of (re)measurements that should be taken at every frequency
        # usage: repeat
        # example return: bytearray(b'')

        val = int(val)
        if (1<=val) and (val<=1000):
            writebyte = 'repeat ' + str(val) + '\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False) 
            self.printMessage("setting the repeat() measurement to " + str(val))
        else:
            self.printMessage("ERROR: repeat() takes integer vals [0 - 1000]")
            msgbytes = self.errorByteReturn()
        return msgbytes 

    def reset(self):
        # reset the tinySA Ultra. NOTE: will disconnect and fully reset
        # usage: reset
        # example return: throws error. raise SerialException

        writebyte = 'reset\r\n'
        self.printMessage("sending reset() signal. Serial will disconnect...")
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes 

    def restart(self, val=0):
        # restarts the  tinySA after the specified number of seconds
        # usage: restart {seconds}
        # example return: ''
        # val = int(val)
        # if val == 0:
        #     writebyte = 'restart ' + str(val) + '\r\n'
        #     msgbytes = self.tinySASerial(writebyte, printBool=False) 
        #     self.printMessage("restarting cancelled.")       
        # elif (0<val):
        #     writebyte = 'restart ' + str(val) + '\r\n'
        #     msgbytes = self.tinySASerial(writebyte, printBool=False) 
        #     self.printMessage("restarting the device in " + str(val) + " seconds.")
        # else:
        #     self.printMessage("ERROR: restart() takes vals 0 or greater")
        #     msgbytes = self.errorByteReturn()

        # # not recognized by device
        # if (msgbytes == b'restart?\r'):
        #     print("!!")

        self.printMessage("ERROR: restart() funciton REMOVED")
        return self.errorByteReturn() 

    def resume(self):
        # resumes the sweeping in either input or output mode
        # usage: resume
        # example return: ''

        writebyte = 'resume\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("resuming sweep")
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("saving to preset " + str(val))           
        else:
            self.printMessage("ERROR: save() takes vals [0 - 4] as integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def saveconfig(self):
        # saves the device configuration data
        # usage: saveconfig
        # example return: bytearray(b'Config saved.\r')

        writebyte = 'saveconfig\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("saveconfig() called")
        return msgbytes

    def scan(self):
        # TODO: documentation for err checking
        # Performs a scan and optionally outputs the measured data.
        # usage: scan {start(Hz)} {stop(Hz)} [points] [outmask]
            # where the outmask is a binary OR of:
            # 1=frequencies, 2=measured data,
            # 4=stored data and points is maximum is 290
        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def scanraw(self):
        # TODO: documentation for err checking
        # performs a scan of unlimited amount of points 
        # and send the data in binary form
        # usage: scanraw {start(Hz)} {stop(Hz)} [points]
            # The measured data is send as:
            #  '{' ('x' MSB LSB)*points '}' 
            # where the 16 bit data is scaled by 32.

        self.printMessage("Function does not exist yet. error checking needed")
        return None
    
    def sd_delete(self):
        # delete a specific file on the sd card
        # usage: sd_delete {filename}
        # example return:

        self.printMessage("Function does not exist yet. error checking needed")
        return None
    
    def sd_list(self):
        # displays list of filenames with extension and sizes
        # usage: sd_list
        # example return: bytearray(b'-0.bmp 307322\r')

        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("listing files from sd card")
        return msgbytes 

    def sd_read(self):
        # read a specific file on the sd_card
        # usage: sd_read {filename}
        # example return: 

        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def selftest(self, val=0):
        # performs one or all selftests
        # usage: selftest 0 0..9
        # 0 appears to be 'run all'
        # example return: msgbytes = bytearray(b'')

        # explicitly allowed vals
        accepted_vals =  np.arange(0, 15, 1) # max exclusive
        #check input
        if (val in accepted_vals):
            writebyte = 'selftest ' + str(val) + '\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("SELFTEST RUNNING. CHECK CONNECTION CAL to RF")           
        else:
            self.printMessage("ERROR: selftest() takes vals [0-15]")
            msgbytes = self.errorByteReturn()
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
            msgbytes = self.tinySASerial(writebyte, printBool=False)
            self.printMessage("spur() set to " + str(val))           
        else:
            self.printMessage("ERROR: spur() takes vals [on|off]")
            msgbytes = self.errorByteReturn()
        return msgbytes
    
    def status(self):
        # displays the current device status (paused/resumed)
        # usage: status
        # example return: bytearray(b'Resumed\r')
       
        writebyte = 'status\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("getting device status() paused/resumed")
        return msgbytes
    
    def sweep(self):
        # TODO: get info on the format and err checking
        # Set sweep boundaries or execute a sweep.
        # Sweep without arguments lists the current sweep 
        # settings. The frequencies specified should be 
        # within the permissible range. The sweep commands 
        # apply both to input and output modes        
        # usage: 
        # sweep [(start|stop|center|span|cw {frequency}) | 
        #   ({start(Hz)} {stop(Hz)} [0..290])]


        self.printMessage("Function does not exist yet. error checking needed")
        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("listing files from sd card")
        return msgbytes 


    def sweeptime(self):
        # sets the sweeptime
        # usage: sweep {time(Seconds)}the time
        # specified may end in a letter where
        # m=mili and u=micro
        self.printMessage("Function does not exist yet. error checking needed")
        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("listing files from sd card")
        return msgbytes 


    def text(self, val=""):
        # sets the sweeptime
        # usage: sweep {time(Seconds)}the time
        # specified may end in a letter where
        # m=mili and u=micro
        self.printMessage("Function does not exist yet. error checking needed")
        
        if len(str(val))>0:
            writebyte = 'text ' + str(val) +'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False) 
            self.printMessage("text() entered is " + str(val))
        else:
            self.printMessage("ERROR: text() needs non-empty values")
            msgbytes = self.errorByteReturn()
        return msgbytes 

    def threads(self):
        # lists information of the threads in the tinySA
        # usage: threads
        # example return:
        # bytearray(b'stklimit| ...\r')
        
        writebyte = 'threads\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("returning thread information for device")
        return msgbytes

    def touch(self, x=0, y=0):
        # sends the coordinates of a touch. 
        # The upper left corner of the screen is 0 0
        # usage: touch {X coordinate} {Y coordinate}
        # example return:

        # check if valid x
        if (x<0) or (self.screenWidth<x):
            self.printMessage("ERROR: touch() needs a valid x coordinate")
            msgbytes = self.errorByteReturn()
            return msgbytes 
        # check if valid y
        if (y<0) or (self.screenHeight<y):
            self.printMessage("ERROR: touch() needs a valid y coordinate")
            msgbytes = self.errorByteReturn()
            return msgbytes 
        writebyte = 'touch ' + str(x) + ' ' + str(y) + '\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("setting the touch() (" + str(x)+"," + str(y) + ")")
        return msgbytes 

    def touchcal(self):
        # starts the touch calibration
        # usage: touchcal
        # example return: bytearray(b'')
        writebyte = 'touchcal\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("starting touchcal")
        return msgbytes

    def touchtest(self):
        # starts the touch test
        # usage: touchtest
        # example return: bytearray(b'')
        
        writebyte = 'touchtest\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("starting the touchtest()")
        return msgbytes

    def trace(self):
        # TODO: get documentation for err checking
        # displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 
        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def trigger(self):
        # sets the trigger type or level
        # usage: trigger auto|normal|single| 
        # {level(dBm)}
        # the trigger level is always set in dBm
        # example return:  

        self.printMessage("Function does not exist yet. error checking needed")
        return None

    def ultra(self, val="off", freq=None):
        # turn on/config tiny SA ultra mode
        # usage: ultra off|on|auto|start|harm {freq}
        # example return: bytearray(b'')

        # #explicitly allowed vals
        # accepted_vals =  ["off", "on"]        


        writebyte = 'ultra\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        self.printMessage("configuring ultra()")
        return msgbytes

    def usart_cfg(self):
        # gets the current serial config
        # usage: usart_cfg
        # example return: bytearray(b'Serial: 115200 baud\r')
        self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'usart_cfg\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def vbat(self):
        # displays the battery voltage
        # usage: vbat
        # example return: bytearray(b'4132 mV\r')
        self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'vbat\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def vbat_offset(self, val=None):
        # displays or sets the battery offset value
        # usage: vbat_offset [{0..4095}]
        # example return: bytearray(b'300\r')

        if val == None:
            #get the offset       
            writebyte = 'vbat_offset\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
        elif (isinstance(val, int)) and (0<= val <=4095):
            writebyte = 'vbat_offset '+str(id)+'\r\n'
            msgbytes = self.tinySASerial(writebyte, printBool=False)   
            self.printMessage("vbat_offset set to " + str(id))
        else:
            self.printMessage("ERROR: vbat_offset() takes either None or [0 - 4095] integers")
            msgbytes = self.errorByteReturn()
        return msgbytes

    def version(self):
        # displays the version text
        # usage: version
        # example return: tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1
        self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'version\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes

    def wait(self):
        # displays the version text
        # usage: wait
        # example return: bytearray(b'')
        self.printMessage("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
        writebyte = 'wait\r\n'
        msgbytes = self.tinySASerial(writebyte, printBool=False) 
        return msgbytes #returns '', but does display screen

    def zero(self):
        # TODO: get info on exactly what this is, does, and the format
        # usage: zero {level}\r\n174dBm
        # example return:

        self.printMessage("Function does not exist yet. error checking needed")
        return None




######################################################################
# Unit testing
######################################################################

if __name__ == "__main__":
    # unit testing

    # create a new tinySA object    
    tsa = tinySA()
    # attempt to connect to previously discovered serial port
    success = tsa.connect(port='COM10')

    # if port open, then complete task(s) and disconnect
    if success == True:
        tsa.setVerbose(True) #detailed messages
        tsa.setErrorByteReturn(True) #get explicit b'ERROR'
        msg = tsa.ultra() 
        print(msg)
        

        tsa.disconnect()
    else:
        print("ERROR: could not connect to port")


    # print(msgbytes[0:10])
    # print(msgbytes[-25:])
    # hex_values = [f'{byte:02x}' for byte in msgbytes]
    # print("HEX")
    # print(len(hex_values))
    # print(hex_values[-25:])

