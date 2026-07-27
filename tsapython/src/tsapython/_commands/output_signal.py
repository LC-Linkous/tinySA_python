#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/output_signal.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

class OutputSignalMixin:
    def cal_output(self, val="off"):
        # disables or sets the caloutput to a specified frequency in MHz
        # usage: caloutput off|30|15|10|4|3|2|1
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  ["off", 'off', 1,2,3,4,10,15,30]
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
        return self.cal_output("off")

    def set_cal_output_30(self):
        # alias for cal_output()
        return self.cal_output(30)

    def set_cal_output_15(self):
        # alias for cal_output()
        return self.cal_output(15)

    def set_cal_output_10(self):
        # alias for cal_output()
        return self.cal_output(10)       

    def set_cal_output_4(self):
        # alias for cal_output()
        return self.cal_output(4)

    def set_cal_output_3(self):
        # alias for cal_output()
        return self.cal_output(3)

    def set_cal_output_2(self):
        # alias for cal_output()
        return self.cal_output(2)

    def set_cal_output_1(self):
        # alias for cal_output()
        return self.cal_output(1)

    def direct(self, val, freq=None):
        # Output mode for generating a square wave signal between 830MHz and 1130MHz
        # usage: direct {start|stop|on|off} {freq(Hz)}
        # example return: ''

        #check input
        if (str(val)=="on") or (str(val) =="off"):
            writebyte = 'direct '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)     
            self.print_message("direct() set with " + str(val))
        elif (str(val)=="start") or (str(val)=="stop"):
            # freq must be a positive number. No upper bound is enforced: the
            # valid range is model-dependent (varies across tinySA variants),
            # so the device itself rejects out-of-range values.
            if (isinstance(freq, (int, float))) and (freq > 0):
                writebyte = 'direct '+str(val)+' ' +str(freq)+ '\r\n'
                msgbytes = self.tinySA_serial(writebyte, printBool=False)     
                self.print_message("direct() set with " + str(val) + " frequency of " + str(freq))            
            else:
                self.print_message("ERROR: direct() start/stop requires freq as a positive number")
                msgbytes = self.error_byte_return()
        else:
            self.print_message("ERROR: direct() takes val={'on', 'off', 'start', 'stop'}, freq=INT")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_direct_on(self):
        # alias for direct()
        return self.direct("on")

    def set_direct_off(self):
        # alias for direct()
        return self.direct("off")

    def set_direct_start(self, freq):
        # alias for direct()
        return self.direct("start", freq)

    def set_direct_stop(self, freq):
        # alias for direct()
        return self.direct("stop", freq)

    def mode(self, val1="low", val2="input"):
        # sets the mode of the tinySA
        # usage: mode low|high input|output
        # example return: ''

        #explicitly allowed vals
        accepted_val1 =  ["low", "high"]
        accepted_val2= ["input", "output"]
        #check input
        if (val1 in accepted_val1) and (val2 in accepted_val2):
            writebyte = 'mode '+str(val1)+ ' ' +str(val2)+'\r\n'
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

    def set_high_output_mode(self):
        # alias for mode()
        # TODO: ERROR CHECKING
        return self.mode("high", "output")

    def modulation(self, val):
        # sets the modulation in output mode
        # usage: modulation off|AM_1kHz|AM_10Hz|NFM|WFM|extern
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["off", "AM_1kHz", "AM_10Hz",
                          "NFM", "WFM", "extern"]
        #check input
        if (str(val) in accepted_vals):
            writebyte = 'modulation '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)           
        else:
            self.print_message("ERROR: modulation() takes vals [off|AM_1kHz|AM_10Hz|NFM|WFM|extern]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_mod_off(self):
        # alias for modulation()
        return self.modulation("off")

    def set_mod_AM_1khz(self):
        # alias for modulation()
        return self.modulation("AM_1kHz")

    def set_mod_AM_10Hz(self):
        # alias for modulation()
        return self.modulation("AM_10Hz")

    def set_mod_NFM(self):
        # alias for modulation()
        return self.modulation("NFM")

    def set_mod_WFM(self):
        # alias for modulation()
        return self.modulation("WFM")

    def set_mod_extern(self):
        # alias for modulation()
        return self.modulation("extern")    

    def output(self, val):
        # sets the output on or off
        # usage: output on|off
        # example return: ''

        # explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (str(val) in accepted_vals):
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

    def ultra(self, val="off", freq=None):
        # turn on/config tiny SA ultra mode
        # usage: ultra off|on|auto|start|harm {freq}
        # example return: bytearray(b'')

        if str(val) in ["off", "on", "auto"]:
            writebyte = 'ultra ' + str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("configuring ultra() " + str(val))
        elif str(val) in ["start", "harm"]:
            writebyte = 'ultra ' + str(val) + ' ' + str(freq) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("configuring ultra() " + str(val) + " at " + str(freq))
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

    def set_ultra_start(self, val):
        return self.ultra("start", val)

    def set_ultra_harmonic(self, val):
        return self.ultra("harm", val)