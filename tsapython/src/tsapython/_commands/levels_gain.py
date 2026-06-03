#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/levels_gain.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

import numpy as np

class LevelsGainMixin:
    def agc(self, val='auto'):
        # Enables/disables the build in Automatic Gain Control
        # usage: agc 0..7|auto
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  np.arange(0, 8, 1) # max exclusive
        #check input
        if (str(val) == "auto") or (val in accepted_vals):
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
        if (str(val) == "auto") or (val in accepted_vals):
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
        if (str(val) in accepted_vals):
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

    def ext_gain(self, val):
        # sets the external attenuation/amplification.
        # Works in both input and output mode
        # usage: ext_gain -100..100
        # example return: ''        
        
        #check input
        if (isinstance(val, (int, float))) and (-100<= val <=100):
            writebyte = 'ext_gain '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("ext_gain() set to " + str(val))       
        else:
            self.print_message("ERROR: ext_gain() takes vals [-100 - 100]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_ext_gain(self, val):
        # alias for ext_gain()
        return self.ext_gain(val)

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

    def set_level(self, val):
        # alias for level()
        return self.level(val)

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

    def set_level_change(self, val):
        # alias for level_change()
        return self.level_change(val)

    def lna(self, val):
        # toggle lna usage off/on
        # usage: lna off|on
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (str(val) in accepted_vals):
            writebyte = 'lna '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("lna() set to " + str(val))        
        else:
            self.print_message("ERROR: lna() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_lna_on(self):
        #alias for lna1()
        return self.lna("on")

    def set_lna_off(self):
        #alias for lna1()
        return self.lna("off")   

    def lna2(self, val="auto"):
        # Set the second LNA usage off/on. 
        # The Ultra Plus devices have a 2nd LNA at a higher frequency range.
        # usage: lna2 0..7|auto
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  [0,1,2,3,4,5,6,7]
        #check input
        if (val == "auto") or (val in accepted_vals):
            writebyte = 'lna2 '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)     
            self.print_message("lna2() set to " + str(val))      
        else:
            self.print_message("ERROR: lna2() takes vals [0 - 7]|auto")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_lna2(self, val):
        #alias for lna2()
        return self.lna2(val)