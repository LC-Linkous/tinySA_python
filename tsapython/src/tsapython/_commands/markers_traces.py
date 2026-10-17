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

from .._host import MixinHost

class MarkersTracesMixin(MixinHost):
    def line(self, val: int | float | str) -> bytearray | None:
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

    def line_off(self) -> bytearray | None:
        # alias for line
        return self.line("off")

    def set_line(self, val: int | float | str) -> bytearray | None:
        # alias for line
        return self.line(val)

    def marker(self, ID: int, val: int | float | str) -> bytearray | None:
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

        if isinstance(ID, int) and not (1 <= ID <= self.profile.markers):
            self.print_message("ERROR: the %s has markers 1..%d" % (self.profile.name, self.profile.markers))
            return self.error_byte_return()

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

    def marker_mode(self, ID: int, mode: str, val: int | str | None = None) -> bytearray | None:
        # marker options beyond on|off|peak:
        #   marker {id} delta {ref_id}|off   marker {id} noise on|off
        #   marker {id} tracking on|off      marker {id} trace {trace#}
        #   marker {id} trace_aver on|off
        accepted = {"delta": None, "noise": ("on", "off"), "tracking": ("on", "off"),
                    "trace": None, "trace_aver": ("on", "off")}
        if mode not in accepted or not isinstance(ID, int) or ID < 1:
            self.print_message("ERROR: marker_mode() takes ID >= 1 and mode delta|noise|tracking|trace|trace_aver")
            return self.error_byte_return()
        words = accepted[mode]
        if words is not None and str(val) not in words:
            self.print_message("ERROR: marker_mode(" + mode + ") takes 'on' or 'off'")
            return self.error_byte_return()
        if mode in ("delta", "trace") and not (isinstance(val, int) or str(val) == "off"):
            self.print_message("ERROR: marker_mode(" + mode + ") takes a number" + (" or 'off'" if mode == "delta" else ""))
            return self.error_byte_return()
        writebyte = 'marker ' + str(ID) + ' ' + mode + ' ' + str(val) + '\r\n'
        return self.tinySA_serial(writebyte, printBool=False)

    def marker_all_off(self) -> bytearray | None:
        # usage: marker off   (disables every marker)
        return self.tinySA_serial('marker off\r\n', printBool=False)

    def marker_read(self, ID: int | None = None) -> bytearray | None:
        # usage: marker [{id}]  -> '{id} {index} {frequency} {value}' per enabled marker
        if ID is None:
            return self.tinySA_serial('marker\r\n', printBool=False)
        if isinstance(ID, int) and ID >= 1:
            return self.tinySA_serial('marker ' + str(ID) + '\r\n', printBool=False)
        self.print_message("ERROR: marker_read() takes None or ID >= 1")
        return self.error_byte_return()

    def marker_on(self, ID: int) -> bytearray | None:
        # alias for marker()
        return self.marker(ID, "on")

    def marker_off(self, ID: int) -> bytearray | None:
        # alias for marker()
        return self.marker(ID, "off")

    def marker_peak(self, ID: int) -> bytearray | None:
        # alias for marker()
        return self.marker(ID, "peak")

    def marker_freq(self, ID: int, val: int | float | str) -> bytearray | None:
        # alias for marker()
        return self.marker(ID, val)

    def marker_index(self, ID: int, val: int | float | str) -> bytearray | None:
        # alias for marker()
        return self.marker(ID, val)

    def trace_select(self, ID: int) -> bytearray | None:
        # split call for TRACE. select an available trace.
        # NOTE: tinySA traces are 1-indexed (trace 0 does not exist).
        if (isinstance(ID, int)) and (ID >= 1):
            writebyte = 'trace '+ str(ID) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("selecting trace")
        else:
            self.print_message("ERROR: trace numbers must be integers >= 1. see device documentation for max")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_units(self, ID: int, val: int | float | str) -> bytearray | None:
        # split call for TRACE. set the units for a trace.
        # device form: trace {trace#} {dBm|dBmV|dBuV|RAW|V|Vpp|W|dBV}  (1-indexed)
        # dBV exists from tinySA firmware v1.4-235 (Aug 2026); older firmware
        # ignores it without an error.
        accepted_vals =  ["dBm", "dBmV", "dBuV", "V", "W", "Vpp", "RAW", "dBV"]

        if (isinstance(ID, int)) and (ID >= 1) and (str(val) in accepted_vals):
            if ID > self.profile.traces:
                self.print_message("ERROR: the %s has %d traces" % (self.profile.name, self.profile.traces))
                return self.error_byte_return()
            writebyte = 'trace '+ str(ID) + ' ' + str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("setting trace " + str(ID) + " units to " + str(val))
        else:
            self.print_message("ERROR: trace_units() takes ID >= 1 and units 'dBm'|'dBmV'|'dBuV'|'RAW'|'V'|'Vpp'|'W'|'dBV'")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_scale(self, val: int | float | str = "auto") -> bytearray | None:
        # split call for TRACE. scales a trace/traces.
        writebyte = 'trace scale ' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("scaling trace")
        return msgbytes

    def trace_reflevel(self, val: int | float | str = "auto") -> bytearray | None:
        # split call for TRACE. sets the reference level of a trace
        writebyte = 'trace reflevel ' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("setting reference level of trace")
        return msgbytes

    def trace_value(self, ID: int) -> bytearray | None:
        # split call for TRACE. gets values of a trace (1-indexed).
        # device form: trace {trace#} value
        if (isinstance(ID, int)) and (ID >= 1):
            writebyte = 'trace ' + str(ID) + ' value\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("getting raw trace values")
        else:
            self.print_message("ERROR: trace_value() takes ID >= 1")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_toggle(self, ID: int, val: int | float | str = "on") -> bytearray | None:
        # split call for TRACE. toggle trace ON or OFF
        # full description: displays all or one trace information
        # or sets trace related information
        # usage:
        # trace [ {0..2} |
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return:

        accepted_vals = ["on", "off"]

        if (isinstance(ID,int)) and (ID >= 1) and (str(val) in accepted_vals):
            # device form: trace {trace#} view on|off  (1-indexed)
            writebyte = 'trace ' + str(ID) + ' view ' +str(val)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("toggling trace " +str(val))
        else:
            self.print_message("ERROR: trace_toggle() takes ID >= 1 and val='on'|'off'")
            msgbytes = self.error_byte_return()

        return msgbytes

    def trace_subtract(self, ID1: int | float | str, ID2: int | float | str) -> bytearray | None:
        # split call for TRACE. subtracts a trace/traces.
        # subtract ID1 FROM ID2

        if (isinstance(ID1,int)) and (ID1 >= 1) and (isinstance(ID2,int)) and (ID2 >= 1):
            # device form: trace {trace#} subtract {trace#}  (1-indexed)
            writebyte = 'trace ' + str(ID1) + ' subtract ' +str(ID2)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("subtracting traces")
        else:
            self.print_message("ERROR: trace IDs must be ints >= 1")
            msgbytes = self.error_byte_return()

        return msgbytes

    def trace_copy(self, ID1: int | float | str, ID2: int | float | str) -> bytearray | None:
        # split call for TRACE. copies a trace/traces.

        if (isinstance(ID1,int)) and (ID1 >= 1) and (isinstance(ID2,int)) and (ID2 >= 1):
            # device form: trace {trace#} copy {trace#}  (1-indexed)
            writebyte = 'trace ' + str(ID1) + ' copy ' +str(ID2)+ '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("copying traces")
        else:
            self.print_message("ERROR: trace IDs must be ints >= 1")
            msgbytes = self.error_byte_return()

        return msgbytes

    def trace_freeze(self, ID: int, val: str = "on") -> bytearray | None:
        # split call for TRACE. freezes (val="on", the default) or releases
        # (val="off") a trace.
        # device form: trace {trace#} freeze on|off  (1-indexed)
        # The firmware needs the on|off word: 'trace 2 freeze' alone is parsed
        # and then ignored, which is what this function used to send.
        # example return:
        if (isinstance(ID,int)) and (ID >= 1) and (str(val) in ["on", "off"]):
            writebyte = 'trace ' + str(ID) + ' freeze ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("trace " + str(ID) + " freeze " + str(val))
        else:
            self.print_message("ERROR: trace_freeze() takes ID >= 1 and val='on'|'off'")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trace_unfreeze(self, ID: int) -> bytearray | None:
        # alias for trace_freeze()
        return self.trace_freeze(ID, "off")

    def trace_clear(self, val: int | float | str) -> bytearray | None:
        # DEPRECATED: the 'clear' keyword left the tinySA firmware in Jul 2021
        # ('store|clear|subtract' became 'copy|freeze|subtract|view|value').
        # Current firmware parses this command and ignores it. Still callable;
        # there is no replacement in current firmware.
        # split call for TRACE. clears a trace/traces. doesnt seem to take inputs
        # full description: displays all or one trace information
        # or sets trace related information
        # usage:
        # trace [ {0..2} |
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return:

        writebyte = 'trace ' + str(val) + ' clear\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("clearing trace(s)")
        return msgbytes

    def trace_action(self, ID: int, val: int | float | str, arg: int | float | str | None = None) -> bytearray | None:
        # split call for TRACE. toggle trace ON or OFF
        # full description: displays all or one trace information
        # or sets trace related information
        # usage:
        # trace [ {0..2} |
        # dBm|dBmV|dBuV|V|W |store|clear|subtract | (scale|
        # reflevel) auto|{level}
        # example return:

        accepted_vals = ["copy","freeze","subtract","view","value"]
        # arg: the word that follows the action on the device:
        #   copy {trace#} | subtract {trace#} | freeze on|off | view on|off
        # Only 'value' works without it; the firmware ignores the other four
        # when the word is missing. arg=None keeps the older two-word form.

        if (isinstance(ID,int)) and (ID >= 1) and (str(val) in accepted_vals):
            # device form: trace {trace#} {action} ...  (1-indexed)
            if arg is None:
                writebyte = 'trace ' + str(ID) + ' ' +str(val)+ '\r\n'
            else:
                writebyte = 'trace ' + str(ID) + ' ' +str(val)+ ' ' + str(arg) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("setting trace action")
        else:
            self.print_message("ERROR: trace_action() takes ID >= 1 and val 'copy'|'freeze'|'subtract'|'view'|'value'")
            msgbytes = self.error_byte_return()

        return msgbytes
