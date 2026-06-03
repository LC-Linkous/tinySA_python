#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/markers_traces.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

class MarkersTracesMixin:
    def line(self, val):
        # Disables the horizontal line or sets it to a specific level.
        # usage: line off|{level}
        # example return: ''
        if (val=="off"):
            writebyte = 'line '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)    
            self.print_message("horizontal line turned off")
        elif (isinstance(val, (int, float))): # or (isinstance(val, float)):    
            writebyte = 'line '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)    
            self.print_message("horizontal line turned off")  
        else:
            self.print_message("ERROR: line takes arguments 'off' or level")
            msgbytes = self.error_byte_return()
        return msgbytes

    def line_off(self):
        # alias for line
        return self.line("off")

    def set_line(self, val):
        # alias for line
        return self.line(val)

    def marker(self, ID, val):
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
        #check input
        if ID == None: 
            self.print_message("ERROR: marker() takes ID=Int|0..4")
            msgbytes = self.error_byte_return()
            return msgbytes

        if (str(val) in accepted_vals):
            writebyte = 'marker ' + str(ID) + ' ' +str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)     
            self.print_message("marker set to " + str(val))      
        elif (isinstance(val, (int, float))): # or (isinstance(val, float)):  
            writebyte = 'marker ' + str(ID) + ' ' +str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)     
            self.print_message("marker set to " + str(val)) 
        else:
            self.print_message("ERROR: marker() takes ID=Int|0..4, and frequency or index in Int or Float")
            msgbytes = self.error_byte_return()
        return msgbytes

    def marker_on(self, ID):
        # alias for marker()
        self.marker(ID, "on")

    def marker_off(self, ID):
        # alias for marker()
        self.marker(ID, "off")

    def marker_peak(self, ID):
        # alias for marker()
        self.marker(ID, "peak")

    def marker_freq(self, ID, val):
        # alias for marker()
        self.marker(ID, val)

    def marker_index(self, ID, val):
        # alias for marker()
        self.marker(ID, val)    

    def trace_select(self, ID):
        # split call for TRACE. select an available trace
        if (isinstance(ID, int)) and ID >=0:
            writebyte = 'trace '+ str(ID) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("selecting trace")
        else:
            self.print_message("ERROR: trace numbers must be integers greater than 0. see device documentation for max")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_units(self, val):
        # split call for TRACE. set the units for the traces
        # explicitly allowed vals
        accepted_vals =  ["dBm", "dBmV", "dBuV", "V", "W", "Vpp", "RAW"]

        if (str(val) in accepted_vals):
            writebyte = 'trace '+ str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("setting trace units to " + str(val))
        else:
            self.print_message("ERROR: trace vals can be 'dBm'|'dBmV'|'dBuV'|'RAW'|'V'|'Vpp'|'W'")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_scale(self, val="auto"):
        # split call for TRACE. scales a trace/traces.
        writebyte = 'trace scale' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("scaling trace")
        return msgbytes

    def trace_reflevel(self, val="auto"):
        # split call for TRACE. sets the reference level of a trace
        writebyte = 'trace reflevel' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("setting reference level of trace")
        return msgbytes

    def trace_value(self, ID):
        # split call for TRACE. gets values of trace

        writebyte = 'trace' + str(ID) + 'value \r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("getting raw trace values")
        return msgbytes

    def trace_toggle(self, ID, val="on"):
        # split call for TRACE. toggle trace ON or OFF
        # full description: displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 

        accepted_vals = ["on", "off"]

        if (isinstance(ID,int)) and (str(val) in accepted_vals):
            writebyte = 'trace' + str(ID) + ' ' +str(val)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("toggling trace " +str(val))
        else:
            self.print_message("ERROR: trace ID is an Int, val='on'|'off'")
            msgbytes = self.error_byte_return()

        return msgbytes

    def trace_subtract(self, ID1, ID2):
        # split call for TRACE. subtracts a trace/traces. 
        # subtract ID1 FROM ID2

        if (isinstance(ID1,int)) and (isinstance(ID2,int)):
            writebyte = 'trace' + str(ID1) + ' subtract ' +str(ID2)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("subtracting traces")
        else:
            self.print_message("ERROR: trace IDs must be Ints")
            msgbytes = self.error_byte_return()

        return msgbytes

    def trace_copy(self, ID1, ID2):
        # split call for TRACE. copies a trace/traces. 

        if (isinstance(ID1,int)) and (isinstance(ID2,int)):
            writebyte = 'trace' + str(ID1) + ' subtract ' +str(ID2)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("copying traces")
        else:
            self.print_message("ERROR: trace IDs must be Ints")
            msgbytes = self.error_byte_return()

        return msgbytes

    def trace_freeze(self, ID):
        # split call for TRACE. sets the reference level of a trace
        # full description: displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 
        if (isinstance(ID,int)):
            writebyte = 'trace' + str(ID) + ' freeze\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("freezing trace")
        else:
            self.print_message("ERROR: trace ID must be Ints")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_clear(self, val):
        # split call for TRACE. clears a trace/traces. doesnt seem to take inputs
        # full description: displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 

        writebyte = 'trace ' + str(val) + 'clear \r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("clearing trace(s)")
        return msgbytes

    def trace_action(self, ID, val):
        # split call for TRACE. toggle trace ON or OFF
        # full description: displays all or one trace information
        # or sets trace related information
        # usage: 
        # trace [ {0..2} | 
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return: 

        accepted_vals = ["copy","freeze","subtract","view","value"]

        if (isinstance(ID,int)) and (str(val) in accepted_vals):
            writebyte = 'trace' + str(ID) + ' ' +str(val)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("setting trace action")
        else:
            self.print_message("ERROR: trace vals can be 'copy'|'freeze'|'subtract'|'view'|'value' and ID is an Int")
            msgbytes = self.error_byte_return()

        return msgbytes