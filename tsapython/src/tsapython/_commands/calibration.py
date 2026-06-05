#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/calibration.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

import numpy as np

class CalibrationMixin:
    def actual_freq(self, val=None):
        # Sets or gets the frequency correction set by CORRECT FREQUENCY menu in the expert menu settings
        # related to freq_corr
        # usage: actual_freq [{frequency}]
        # example return: bytearray(b'3000000000\r')

        if val == None:
            #get the dac       
            writebyte = 'actual_freq\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif (isinstance(val, (int, float))) and (self.minSADeviceFreq <= val <=self.maxSADeviceFreq ):
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
            if (freq is None) or not(self.minSADeviceFreq <= freq <= self.maxSADeviceFreq):
                self.print_message("ERROR: correction() frequency outside of device specs. see documentation")
                msgbytes = self.error_byte_return()
                return msgbytes
            if (val is None) or not(-10 <= val <= 35):
                self.print_message("ERROR: correction() val dB outside of  specs. see documentation")
                msgbytes = self.error_byte_return()
                return msgbytes
            writebyte = 'correction ' + str(argName) + ' ' + str(slot) +\
                    ' ' + str(freq) + ' ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("correction() set with " + str(argName) + " " + str(slot) +\
                    " " + str(freq) + " " + str(val))
        return msgbytes

    def freq(self, val):
        # pauses the sweep and sets the measurement frequency.
        # usage: freq {frequency}
        # example return: bytearray(b'')

        #check input
        if (isinstance(val, (int, float))) and (self.minSADeviceFreq<= val <=self.maxSADeviceFreq):
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
        elif ((433e6) <=val <=(435e6)):
            writebyte = 'if '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)                 
            self.print_message("setIF() set to "  + str(val))       
        else:
            self.print_message("ERROR: if() takes vals ['auto'|0|433M...435M] in Hz as integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_IF1(self, val):
        # usage: if1 {975M..979M}\r\n977.555902MHz
        # example return: ''

        #check input
        if (val == 0) or (val=='auto'):
            writebyte = 'if1 '+str(0)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)      
            self.print_message("setIF1() set to auto")         
        elif ((975e6) <=val <=(979e6)):
            writebyte = 'if1 '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("setIF() set to "  + str(val))          
        else:
            self.print_message("ERROR: if1() takes vals ['auto'|0|975M...979M] in Hz as integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def level_offset(self, val, offset, isOutput=False):
        # sets or dumps the level calibration data.
        # For the output corrections first ensure correct output 
        # levels at maximum output level. 
        # For the low output set the output to -50dBm and
        # measure and correct the level with 
        # "leveloffset switch error" where for all output 
        # leveloffset commands measure the level with the
        # leveloffset to zero and calculate
        # error = measured level - specified level


        # usage: leveloffset [low|switch|receive_switch|out_switch|lna|
        #   harmonic|shift|shift1|shift2|shift3|drive1|drive2|drive3|
        #   direct|direct_lna|ultra|ultra_lna|harmonic_lna|adf]
        #    {output} [-20..+20]


        #NOTE: there's probably some limitations on which of these take the 'output' command,
        # but that error checking isn't done here YET

        #explicitly allowed vals
        accepted_vals =  ["low","switch","receive_switch","out_switch","lna",
                          "harmonic","shift","shift1","shift2","shift3",
                          "drive1","drive2","drive3","direct","direct_lna",
                          "ultra","ultra_lna","harmonic_lna","adf"]
        #check input
        if (val in accepted_vals):
            if (-20.0<=offset<=20.0):
                if isOutput == True:
                    # success message
                    writebyte = 'leveloffset '+str(val)+ ' output ' + str(float(offset)) +'\r\n'
                    msgbytes = self.tinySA_serial(writebyte, printBool=False)
                    self.print_message("leveloffset() set to " + str(val) + " output " + str(offset))    


                elif isOutput == False:
                    # success message
                    writebyte = 'leveloffset '+str(val)+ ' ' + str(float(offset)) +'\r\n'
                    msgbytes = self.tinySA_serial(writebyte, printBool=False)
                    self.print_message("leveloffset() set to " + str(val) +  " "  + str(offset))    

                else:
                    # just for the error check when bulking this function out
                    self.print_message("ERROR: leveloffset() value isOutput is a Boolean")
                    self.print_message("ERROR: value set to" + str(isOutput))
                    msgbytes =  self.error_byte_return()
                    return msgbytes
                        

            else:
                self.print_message("ERROR: leveloffset() takes offset vals as floats [-20.0 - 20.0]")
                self.print_message("ERROR: value set to" + str(offset))
                msgbytes =  self.error_byte_return()
               
       
        else:
            self.print_message("ERROR: leveloffset() takes value arguments low|switch|receive_switch|out_switch|lna|" \
            "harmonic|shift|shift1|shift2|shift3|drive1|drive2|drive3|direct|" \
            "direct_lna|ultra|ultra_lna|harmonic_lna|adf, ans specificed output and level")
            self.print_message("ERROR: value set to" + str(val))
            msgbytes =  self.error_byte_return()
        return msgbytes


    def spur(self, val=None):
        # enables or disables spur reduction
        # usage: spur on|off
        # example return:

        # explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (str(val) in accepted_vals):
            writebyte = 'spur '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("spur() set to " + str(val))           
        else:
            self.print_message("ERROR: spur() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def spur_on(self):
        # alias for spur()
        return self.spur("on")

    def spur_off(self):
        # alias for spur()
        return self.spur("off")

    def vbat_offset(self, val=None):
        # displays or sets the battery offset value
        # usage: vbat_offset [{0..4095}]
        # example return: bytearray(b'300\r')

        if val == None:
            #get the offset       
            writebyte = 'vbat_offset\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif (isinstance(val, (int, float))) and (0<= val <=4095):
            writebyte = 'vbat_offset '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("vbat_offset set to " + str(val))
        else:
            self.print_message("ERROR: vbat_offset() takes either None or [0 - 4095] integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def get_vbat_offset(self, val=None):
        # alias for vbat_offset()
        return self.vbat_offset(val)

    def set_vbat_offset(self, val=None):
        # alias for vbat_offset()
        return self.vbat_offset(val)

    def zero(self, val=None):
        #get or set the zero offset in dBm
        # DO NOT CHANGE if unfamiliar with device and offset
        # usage: zero {level}\r\n174dBm
        # example return:

        if val == None:
            writebyte = 'zero\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("returning zero offset")
        else:
            writebyte = 'zero ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("device zero offset is " + str(val) + " dBm.")

        return msgbytes

    def get_zero_offset(self, val=None):
        # alias function for zero
        return self.zero(val)