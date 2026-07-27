#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/presets_config.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

from .._host import MixinHost

class PresetsConfigMixin(MixinHost):
######################################################################
# Serial command config, input error checking
######################################################################

    def abort(self, val: int | float | str | None = None) -> bytearray | None:
        # Sets the abort enabled status (on/off)
        # usage: abort [off|on]
        # example return: bytearray(b'')

        # #explicitly allowed vals
        accepted_vals =  ["off", "on"]        

        #check input
        if (str(val) in accepted_vals): #toggle state
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

    def enable_abort(self) -> bytearray | None:
        # alias for abort()
        return self.abort( "on")

    def disable_abort(self) -> bytearray | None:
        # alias for abort()
        return self.abort("off")

    def abort_action(self) -> bytearray | None:
        # alias for abort()
        return self.abort()

    def clear_config(self) -> bytearray | None:
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

    def clear_and_reset(self) -> bytearray | None:
        # alias function for full clear and reset process
        # NOTE: reset() disconnects the serial immediately, so it may raise a
        # SerialException or return nothing usable. We clear first, then reset,
        # and tolerate the disconnect rather than depending on a clean return.
        # Returns the reset response if one comes back before the port drops,
        # otherwise None. Callers should NOT block waiting on this return.
        self.clear_config()
        try:
            return self.reset()
        except Exception as err:  # serial drops on reset; expected
            self.print_message("reset() disconnected the serial (expected): " + str(err))
            return None

    def device_id(self, ID: int | None = None) -> bytearray | None:
        # sets or dumps a user settable number that can be used to identify a specific tinySA
        # usage: deviceid [{number}]
        # example return: bytearray(b'deviceid 12\r')

        if ID == None:
            #get the device ID        
            writebyte = 'deviceid\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        elif isinstance(ID, int):
            writebyte = 'deviceid '+str(ID)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)   
            self.print_message("device ID set to " + str(ID))
        else:
            self.print_message("ERROR: device_id() takes either None or integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def get_device_id(self) -> bytearray | None:
        # alias for device_id()
        return self.device_id()

    def set_device_id(self, ID: int) -> bytearray | None:
        # alias for device_id()
        return self.device_id(ID)

    def load(self, val: int = 0) -> bytearray | None:
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

    def recall(self, val: int = 0) -> bytearray | None:
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

    def remark(self, val: int | float | str) -> bytearray | None:
        # does nothing
        # usage: remark {any text}
        # example return: bytearray(b'')
        writebyte = 'remark ' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("remark " + str(val))
        
        return msgbytes 

    def repeat(self, val: int = 1) -> bytearray | None:
        # Sets the number of (re)measurements that 
        # should be taken at every frequency
        # usage: repeat
        # example return: bytearray(b'')

        val = int(val)
        if (1<=val<=1000):
            writebyte = 'repeat ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("setting the repeat() measurement to " + str(val))
        else:
            self.print_message("ERROR: repeat() takes integer vals [0 - 1000]")
            msgbytes = self.error_byte_return()
        return msgbytes 

    def reset(self) -> bytearray | None:
        # reset the tinySA Ultra. NOTE: will disconnect and fully reset
        # usage: reset
        # example return: throws error. raise SerialException

        writebyte = 'reset\r\n'
        self.print_message("sending reset signal. Serial will disconnect...")
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        return msgbytes 

    def reset_device(self) -> bytearray | None:
        # alias function for reset()
        return self.reset()

    def restart(self, val: int = 0) -> bytearray | None:
        # restarts the  tinySA after the specified number of seconds
        # usage: restart {seconds}
        # example return: ''
        val = int(val)
        if val == 0:
            writebyte = 'restart ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("restarting cancelled.")       
        elif (0<val):
            writebyte = 'restart ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("restarting the device in " + str(val) + " seconds.")
        else:
            self.print_message("ERROR: restart() takes vals 0 or greater")
            msgbytes = self.error_byte_return()

        return msgbytes

    def restart_device(self, val: int) -> bytearray | None:
        # alias function for restart
        return self.restart(val)

    def cancel_restart(self) -> bytearray | None:
        # alias function for restart
        return self.restart(val=0)

    def save(self, val: int = 1) -> bytearray | None:
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

    def save_config(self) -> bytearray | None:
        # saves the device configuration data
        # usage: saveconfig
        # example return: bytearray(b'Config saved.\r')

        writebyte = 'saveconfig\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("save_config() called")
        return msgbytes

    def sd_delete(self, val: int | float | str) -> bytearray | None:
        # delete a specific file on the sd card
        # usage: sd_delete {filename}
        # example return:

        writebyte = 'sd_delete ' + str(val)+ '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("deleting file from sd card")
        return msgbytes

    def sd_list(self) -> bytearray | None:
        # displays list of filenames with extension and sizes
        # usage: sd_list
        # example return: bytearray(b'-0.bmp 307322\r')

        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("listing files from sd card")
        return msgbytes 

    def sd_read(self, val: int | float | str) -> bytearray | None:
        # read a specific file on the sd_card
        # usage: sd_read {filename}
        # example return: 

        writebyte = 'sd_read ' + str(val)+ '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("reading file from sd card")
        return msgbytes

    def wait(self, val: int = 0) -> bytearray | None:
        # wait for a single sweep to finish and pauses
        #  sweep or waits for specified number of seconds
        # usage: wait [{seconds}]
        # example return:

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
        return msgbytes