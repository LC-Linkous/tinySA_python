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

class PresetsConfigMixin:
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

    def enable_abort(self):
        # alias for abort()
        return self.abort( "on")

    def disable_abort(self):
        # alias for abort()
        return self.abort("off")

    def abort_action(self):
        # alias for abort()
        return self.abort()

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

    def device_id(self, ID=None):
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

    def get_device_id(self):
        # alias for device_id()
        return self.device_id()

    def set_device_id(self, ID):
        # alias for device_id()
        return self.device_id(ID)

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

    def remark(self, val):
        # does nothing
        # usage: remark {any text}
        # example return: bytearray(b'')
        writebyte = 'remark ' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("remark " + str(val))
        
        return msgbytes 

    def repeat(self, val=1):
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

    def reset(self):
        # reset the tinySA Ultra. NOTE: will disconnect and fully reset
        # usage: reset
        # example return: throws error. raise SerialException

        writebyte = 'reset\r\n'
        self.print_message("sending reset signal. Serial will disconnect...")
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        return msgbytes 

    def reset_device(self):
        # alias function for reset()
        return self.reset()

    def restart(self, val=0):
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

    def restart_device(self, val):
        # alias function for restart
        return self.restart(val)

    def cancel_restart(self):
        # alias function for restart
        return self.restart(val=0)

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

    def sd_delete(self, val):
        # delete a specific file on the sd card
        # usage: sd_delete {filename}
        # example return:

        writebyte = 'sd_delete ' + str(val)+ '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("deleting file from sd card")
        return msgbytes

    def sd_list(self):
        # displays list of filenames with extension and sizes
        # usage: sd_list
        # example return: bytearray(b'-0.bmp 307322\r')

        writebyte = 'sd_list\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("listing files from sd card")
        return msgbytes 

    def sd_read(self, val):
        # read a specific file on the sd_card
        # usage: sd_read {filename}
        # example return: 

        writebyte = 'sd_read ' + str(val)+ '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("reading file from sd card")
        return msgbytes

    def wait(self, val=0):
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