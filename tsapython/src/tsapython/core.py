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
    def __init__(self, parent: object | None = None) -> None:
        # serial port
        self.ser: serial.Serial | None = None

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

    def set_verbose(self, verbose: bool = False) -> None:
        self.verboseEnabled = verbose

    def get_verbose(self) -> bool:
        return self.verboseEnabled

    def print_message(self, msg: object) -> None:
        if self.verboseEnabled == True:
            print(msg)

######################################################################
# Explicit error return
# set_error_byte_return()  - set if explicit b'ERROR' is returned
# get_error_byte_return()  - get the return mode True/False
# error_byte_return()  - return 'ERROR' message or empty. 
######################################################################

    def set_error_byte_return(self, errByte: bool = False) -> None:
        self.returnErrorByte = errByte

    def get_error_byte_return(self) -> bool:
        return self.returnErrorByte

    def error_byte_return(self) -> bytearray:
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

    def select_existing_device(self, tinySAModel: str) -> None:
        # uses pre-set config files. 
        # tinySAModel var must be one of the following:
        # "BASIC", "ZS405", "ZS406", "ZS407"
        try:
            # self.dev is the planned device-config module; not implemented yet.
            # The bare except below is what makes this a safe no-op today.
            noErrors = self.dev.select_preset_model(tinySAModel)  # type: ignore[attr-defined]
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

    def load_custom_config(self, configFile: str) -> None:
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

    def set_ultra_mode(self, ultraMode: bool = False) -> None:
        self.ultraEnabled = ultraMode

    def set_abort_mode(self, abortMode: bool = False) -> None:
        self.abortEnabled = abortMode

    def set_harmonic_mode(self, harmonicMode: bool = False) -> None:
        self.harmonicEnabled = harmonicMode

    
    # error check boundaries
    ## signal analyzer specific

    def set_min_SA_freq(self, f: int | float | str) -> None:
        self.minSADeviceFreq = float(f)

    def get_min_SA_freq(self) -> float:
        return self.minSADeviceFreq 

    def set_max_SA_freq(self, f: int | float | str) -> None:
        self.maxSADeviceFreq = float(f)

    def get_max_SA_freq(self) -> float:
        return self.maxSADeviceFreq

    ## signal generator specific 

    def set_min_SG_freq(self, f: int | float | str) -> None:
        self.minSGDeviceFreq = float(f)

    def get_min_SG_freq(self) -> float:
        return self.minSGDeviceFreq 

    def set_max_SG_freq(self, f: int | float | str) -> None:
        self.maxSGDeviceFreq = float(f)

    def get_max_SG_freq(self) -> float:
        return self.maxSGDeviceFreq

######################################################################
# Serial management and message processing
######################################################################

    def autoconnect(self, timeout: float = 1) -> tuple[bool, bool]:
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

    def connect(self, port: str, timeout: float = 1) -> bool:
        # attempt connection to provided port. 
        # returns: True if successful, False otherwise

        try:
            self.ser = serial.Serial(port=port, timeout=timeout)
            return True
        except Exception as err:
            self.print_message("ERROR: cannot open port at " + str(port))
            self.print_message(err)
            return False

    def _require_serial(self) -> "serial.Serial":
        # The serial-touching methods assume connect()/autoconnect() succeeded.
        # Raising here (instead of the former AttributeError on NoneType) gives
        # a clear message and lets the type-checker narrow self.ser.
        if self.ser is None:
            raise RuntimeError(
                "not connected: call connect() or autoconnect() before sending commands")
        return self.ser

    def disconnect(self) -> None:
        # closes the serial port
        self._require_serial().close()

    def tinySA_serial(self, writebyte: str, printBool: bool = False, pts: int | None = None) -> bytearray | None:
        # write out to serial, get message back, clean up, return
        
        ser = self._require_serial()
        # clear INPUT buffer
        ser.reset_input_buffer()
        # clear OUTPUT buffer
        ser.reset_output_buffer()


        ser.write(bytes(writebyte, 'utf-8'))
        msgbytes: bytearray | None
        if pts is None:
            # text commands: read to the 'ch>' prompt, then clean
            raw = self.get_serial_return()
            # a None here means the serial read itself failed; pass that through
            # rather than crashing in clean_return
            msgbytes = self.clean_return(raw) if raw is not None else None
        else:
            # binary commands (scanraw): read by EXPECTED LENGTH, not by a
            # terminator byte. Any byte value (incl. '}' 0x7d and '>' 0x3e) can
            # occur inside the 16-bit sample data, so terminator scanning
            # truncates the frame. See get_binary_return().
            msgbytes = self.get_binary_return(pts)

        if printBool == True:
            print(msgbytes) #overrides verbose for debug

        return msgbytes

    def get_serial_return(self) -> bytearray | None:
        # while there's a buffer, read in the returned message
        # original buffer reading from: https://groups.io/g/tinysa/topic/tinysa_screen_capture_using/82218670

        ser = self._require_serial()
        buffer = bytes()
        while True:
            if ser.in_waiting > 0:
                buffer += ser.read(ser.in_waiting)
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

    def get_binary_return(self, pts: int | None = None, timeout: float = 10.0, idle_timeout: float = 1.0) -> bytearray:
        # Reads a binary scanraw-style frame from the serial port.
        #
        # WHY THIS EXISTS (separate from get_serial_return):
        # get_serial_return terminates the read at the first '>' (0x3e) byte,
        # which is correct for text responses ending in the 'ch>' prompt. Binary
        # scanraw data, however, contains arbitrary byte values -- including
        # 0x3e ('>') AND 0x7d ('}') -- inside the 16-bit samples. So a binary
        # frame CANNOT be terminated by scanning for any marker byte; doing so
        # truncates the frame at the first colliding data byte. (Confirmed on
        # hardware: 450-pt frames intermittently contain early 0x3e/0x7d bytes.)
        #
        # The frame format is:
        #     'scanraw ...\r\n' (echoed command) + '{' + N*( 'x' + 2 bytes ) + '}'
        # i.e. N points, each 3 bytes (an 'x' separator + a little-endian uint16).
        #
        # TWO MODES:
        #   * Known count (pts is given): read until we have the full frame by
        #     LENGTH (1 + 3*pts + 1 bytes from the opening '{'). This is the
        #     reliable path for scan_raw(), which always knows pts.
        #   * Unknown count (pts is None): read structurally for streaming/
        #     continuous callers -- accumulate until a '}' appears at a 3-byte
        #     group boundary (a real terminator), or the stream goes idle.
        #     Intended for future continuous-scanraw functions.
        #
        # Returns: '{' + the 3*N data bytes, WITHOUT the trailing '}', matching
        # the historical clean_return() contract that existing examples rely on
        # (callers do data[1:] then struct.unpack exactly 3*N bytes).

        ser = self._require_serial()
        buffer = bytes()
        start_time = time.time()
        last_data_time = None

        # ---- accumulate raw bytes from the port ----
        def overall_timed_out() -> bool:
            return (time.time() - start_time) > timeout

        if pts is not None:
            # KNOWN-LENGTH MODE
            # full frame from '{' is: '{' + 3*pts data bytes + '}'
            frame_len = 1 + (3 * pts) + 1
            # We must first see the opening '{', then collect frame_len bytes
            # starting at it. Read until we have '{' plus frame_len bytes after
            # the brace position, or time out.
            while True:
                if ser.in_waiting > 0:
                    buffer += ser.read(ser.in_waiting)
                    last_data_time = time.time()
                    start = buffer.find(b'{')
                    if start != -1 and (len(buffer) - start) >= frame_len:
                        # we have the complete frame
                        frame = buffer[start:start + frame_len]
                        # return '{' + data, dropping the trailing '}'
                        return bytearray(frame[:-1])
                elif overall_timed_out():
                    self.print_message(
                        "WARNING: scanraw binary read timed out "
                        "(have %d bytes, wanted frame of %d from '{')"
                        % (len(buffer), frame_len))
                    break
                else:
                    time.sleep(0.01)
            # timed out: return what we have from '{' (caller will detect short)
            start = buffer.find(b'{')
            if start == -1:
                self.print_message("ERROR: scanraw frame start '{' not found")
                return self.error_byte_return()
            return bytearray(buffer[start:])

        else:
            # UNKNOWN-COUNT / STREAMING MODE (for future continuous callers)
            # Read until a '}' lands on a 3-byte group boundary measured from the
            # byte after '{'. A '}' at a boundary is the true frame end; a 0x7d
            # inside a sample is never at a boundary (it's byte 2 or 3 of an
            # 'x__' group). Also stop if the stream goes idle.
            while True:
                if ser.in_waiting > 0:
                    buffer += ser.read(ser.in_waiting)
                    last_data_time = time.time()
                    start = buffer.find(b'{')
                    if start != -1:
                        body = buffer[start + 1:]   # bytes after '{'
                        # scan group boundaries (every 3 bytes) for a '}'
                        # a complete group is 3 bytes; check position % 3 == 0
                        for i in range(0, len(body)):
                            if body[i] == 0x7d and (i % 3) == 0:
                                # '}' at a group boundary -> true end
                                frame = buffer[start:start + 1 + i + 1]
                                return bytearray(frame[:-1])  # drop trailing '}'
                elif last_data_time and (time.time() - last_data_time) > idle_timeout:
                    # stream went idle without a clean terminator
                    self.print_message(
                        "WARNING: streaming binary read went idle "
                        "(%d bytes, no boundary '}')" % len(buffer))
                    break
                elif overall_timed_out():
                    self.print_message(
                        "WARNING: streaming binary read timed out (%d bytes)"
                        % len(buffer))
                    break
                else:
                    time.sleep(0.01)
            start = buffer.find(b'{')
            if start == -1:
                self.print_message("ERROR: streaming frame start '{' not found")
                return self.error_byte_return()
            return bytearray(buffer[start:])
    def clean_return(self, data: bytearray) -> bytearray:
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

    def convert_frequency(self, txtstr: str) -> None:
        # this takes the user input (as text) and converts it. 
        #  From documentation:
        #       Frequencies can be specified using an integer optionally postfixed with a the letter 
        #       'k' for kilo 'M' for Mega or 'G' for Giga. E.g. 0.1M (100kHz), 500k (0.5MHz) or 12000000 (12MHz)
        # However the abbreviation makes error checking with numerics more difficult. so convert everything to Hz.
        #  e notation is fine
        pass

    def convert_time(self, txtstr: str) -> None:
        # this takes the user input (as text) and converts it. 
        #  From documentation:        
        #        Time is specified in seconds optionally postfixed with the letters 'm' for mili 
        #        or 'u' for micro. E.g. 1 (1 second), 2.5 (2.5 seconds), 120m (120 milliseconds)



        pass

    def is_rgb24(self, hexStr: str) -> bool:
        # check if the string matches the pattern 0xRRGGBB
        pattern = r"^0x[0-9A-Fa-f]{6}$"
        return bool(re.match(pattern, hexStr))