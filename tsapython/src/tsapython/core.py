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

import platform
import serial
import serial.tools.list_ports # COM search method wants full path
import re
import sys
import time

from ._identify import (
    classify_reply, identify_device, STATUS_BLOCKED, STATUS_REFUSED, STATUS_TIMEOUT,
    STATUS_UNKNOWN, STATUS_USAGE)
from ._log import JsonlLog, LOG_FORMAT, LOG_LEVELS
from ._profiles import (
    DeviceProfile, DEFAULT, FIRMWARE_FLOOR, PROFILES, profile_for)


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
    # Default wait for the device prompt, in seconds. The firmware's own limits
    # bound a single reply: the longest sweep time is 60 s ('sweeptime 0.003..60'),
    # so a scan on any setting completes well inside this. Change it for every
    # instance here, for one instance with tinySA(serial_timeout=...), or at any
    # time with set_serial_timeout(). None waits indefinitely, as 3.x did.
    DEFAULT_SERIAL_TIMEOUT: float | None = 120.0

    def __init__(self, parent: object | None = None,
                 serial_timeout: float | None = DEFAULT_SERIAL_TIMEOUT) -> None:
        # serial port
        self.ser: serial.Serial | None = None

        # message feedback
        self.verboseEnabled = False
        self.returnErrorByte = False

        # serial read timeout in seconds; see DEFAULT_SERIAL_TIMEOUT above.
        # On timeout a call returns None, the same value a failed read returns.
        self.serialTimeout: float | None = None if serial_timeout is None else float(serial_timeout)

        # optional log file (see set_log_file). None = logging off.
        self._log: JsonlLog | None = None
        # Used ONLY while a log file is open: the text of the ERROR message(s) a
        # function printed just before returning its error value, so the log
        # record can say why. Cleared as soon as that record is written.
        self._log_reason = ""
        self._serial_busy = False      # True while tinySA_serial() is running
        self._serial_timed_out = False # set by the read helpers, read by tinySA_serial()
        self._timed_out_partial = bytes() # what HAD arrived when a text read timed out (for the log)


        # VARS BELOW HERE will be largely replaced with device class config calls
        # # this will allow for user settings and device presets

        # other overrides
        self.ultraEnabled = False
        self.abortEnabled = False
        self.harmonicEnabled = False

        # 4.0.0: device profile. DEFAULT until connect() identifies the device or
        # select_existing_device() is called. See _profiles.py.
        self.profile: DeviceProfile = DEFAULT
        self.profileDetected = False
        self.deviceCommands: frozenset[str] | None = None   # from the device's own 'help' reply
        self.firmwareBuild: tuple[int, int, int] | None = None
        self.identifyOnConnect = True
        # RF output gate: output("on") and cal_output() send nothing until this is True
        self.outputAllowed = False

        #select device vars - the DEFAULT profile; replaced by _apply_profile()
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
        if (self._log is not None) and str(msg).startswith("ERROR"):
            # keep the reason for the log record that follows (logging only)
            self._log_reason = (self._log_reason + " | " + str(msg)) if self._log_reason else str(msg)
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
        if (self._log is not None) and (not self._serial_busy):
            # a library-side check refused the call before anything was sent
            reason, self._log_reason = self._log_reason, ""
            self._log.write_command(sys._getframe(1).f_code.co_name, "", STATUS_BLOCKED,
                                    0, b"", False, reason)
        if self.returnErrorByte == True:
            return bytearray(b'ERROR')
        else:
            return bytearray(b'') # the default

######################################################################
# Serial read timeout
# set_serial_timeout()  - seconds to wait for the device prompt, or None
# get_serial_timeout()  - the current setting
#
# 4.0.0: the default is DEFAULT_SERIAL_TIMEOUT (120 s). Earlier versions
# waited indefinitely; pass None to get that back. On timeout the call
# returns None (the same value a failed serial read already returned) and,
# if a log file is open, a record with status 'timeout' is written.
######################################################################

    def set_serial_timeout(self, seconds: float | None = None) -> None:
        if (seconds is not None) and (float(seconds) <= 0):
            self.print_message("ERROR: set_serial_timeout() takes a positive number of seconds, or None")
            return
        self.serialTimeout = None if seconds is None else float(seconds)

    def get_serial_timeout(self) -> float | None:
        return self.serialTimeout

######################################################################
# Log file (optional, off by default)
# set_log_file()    - start appending records to a JSON Lines file
# close_log_file()  - stop logging and close the file
# get_log_file()    - path of the open log file, or None
#
# The library keeps nothing in memory: each record is written and flushed
# as it happens. See the README section "Logging" for the record format.
#   level="commands" : every call, reply text limited to 256 characters,
#                      binary replies recorded by length only
#   level="data"     : complete replies; binary replies as base64
######################################################################

    def set_log_file(self, path: str, level: str = "commands") -> bool:
        # returns True if the log file was opened
        if level not in LOG_LEVELS:
            self.print_message("ERROR: set_log_file() level must be one of " + str(LOG_LEVELS))
            return False
        self.close_log_file()
        try:
            self._log = JsonlLog(path, level)
        except OSError as err:
            self.print_message("ERROR: cannot open log file at " + str(path))
            self.print_message(err)
            self._log = None
            return False
        self._log_reason = ""
        self._log_session()
        return True

    def close_log_file(self) -> None:
        if self._log is not None:
            self._log.write("event", {"event": "log-closed", "detail": ""})
            self._log.close()
            self._log = None
        self._log_reason = ""

    def get_log_file(self) -> str | None:
        return self._log.path if self._log is not None else None

    def _log_session(self) -> None:
        # Writes the 'session' record: what library, what port, what device.
        # If a port is open, the device is asked for 'version' and 'info' so
        # the record can name the board and firmware. Those two reads are not
        # logged as commands, and use a short timeout so a silent or foreign
        # device cannot hang the call.
        log = self._log
        if log is None:
            return
        version_reply = ""
        info_reply = ""
        port = ""
        if self.ser is not None:
            port = str(getattr(self.ser, "port", ""))
            saved_timeout = self.serialTimeout
            self._log = None            # do not log the identification reads
            self.serialTimeout = 3.0 if saved_timeout is None else saved_timeout
            try:
                reply = self.tinySA_serial('version\r\n', printBool=False, _raw=True)
                version_reply = bytes(reply).decode("utf-8", errors="replace").strip() if reply else ""
                reply = self.tinySA_serial('info\r\n', printBool=False, _raw=True)
                info_reply = bytes(reply).decode("utf-8", errors="replace").strip() if reply else ""
            except Exception as err:    # logging must never break the caller
                self.print_message("WARNING: could not identify the device for the log: " + str(err))
            finally:
                self._log = log
                self.serialTimeout = saved_timeout
        device = identify_device(version_reply, info_reply)
        try:
            from . import __version__ as library_version
        except Exception:
            library_version = "unknown"
        log.write("session", {
            "log_format": LOG_FORMAT,
            "library": library_version,
            "python": platform.python_version(),
            "platform": platform.platform(),
            "port": port,
            "version_reply": version_reply,
            "info_first_line": info_reply.split("\r\n")[0] if info_reply else "",
            "family": device["family"],
            "board": device["board"],
            "build": device["build"],
        })

######################################################################
# Set Device Params
#   Library specific functions. These set the boundaries & features for
#   error checking in the library
#
# WARNING: these DO NOT change the settings on the DEVICE. just the library.
######################################################################

    def select_existing_device(self, tinySAModel: str) -> bool:
        # Choose the device profile by name instead of asking the device.
        # tinySAModel: "BASIC" | "ZS304" | "ULTRA" | "ZS405" | "ULTRA+" | "ZS406" | "ZS407"
        # Returns True if the name was known. connect() normally does this for
        # you (see identify()); call this for scripts that must not query the
        # device, or to override what was detected.
        key = str(tinySAModel).strip().upper()
        if key not in PROFILES:
            self.print_message("ERROR: select_existing_device() takes one of " + ", ".join(sorted(PROFILES)))
            return False
        self._apply_profile(PROFILES[key], detected=False)
        return True

    def load_custom_config(self, configFile: str) -> None:
        # TODO: for loading modified or other devices working on the same firmware
        pass

    def _apply_profile(self, profile: DeviceProfile, detected: bool) -> None:
        self.profile = profile
        self.profileDetected = detected
        self.maxPoints = profile.max_points
        self.minSADeviceFreq = profile.min_freq
        self.maxSADeviceFreq = profile.max_freq_ultra
        self.minSGDeviceFreq = profile.min_sg_freq
        self.maxSGDeviceFreq = profile.max_sg_freq
        self.screenWidth = profile.screen_width
        self.screenHeight = profile.screen_height
        if self._log is not None:
            self._log.write("event", {"event": "profile", "detail": profile.name
                                      + (" (detected)" if detected else " (selected)")})

    def get_profile(self) -> DeviceProfile:
        return self.profile

    def identify(self) -> dict[str, object]:
        # Ask the connected device what it is, choose its profile, and read its
        # command list. Called by connect() unless identifyOnConnect is False.
        # Returns the identify_device() dict plus 'commands' and 'profile'.
        # Uses a 3 s read timeout for these three commands only, so a silent or
        # foreign device cannot hang the connect.
        saved = self.serialTimeout
        self.serialTimeout = 3.0 if saved is None else min(saved, 3.0)
        try:
            version_reply = self._reply_text('version\r\n')
            info_reply = self._reply_text('info\r\n')
            help_reply = self._reply_text('help\r\n')
        finally:
            self.serialTimeout = saved
        found = identify_device(version_reply, info_reply)
        family = str(found["family"])
        board = str(found["board"])
        build = found["build"]
        self.firmwareBuild = (int(build[0]), int(build[1]), int(build[2])) if isinstance(build, list) else None
        if help_reply:
            words = re.sub(r"(Other )?commands:", " ", help_reply).split()
            self.deviceCommands = frozenset(words) if words else None
        else:
            self.deviceCommands = None
        if family == "unknown":
            self.print_message("WARNING: device did not answer 'version' as a tinySA; keeping the default profile")
            self._apply_profile(DEFAULT, detected=False)
        else:
            self._apply_profile(profile_for(family, board), detected=True)
        if self.firmwareBuild is not None and self.firmwareBuild < FIRMWARE_FLOOR:
            self.print_message("WARNING: firmware build %s is older than the oldest build this library is "
                               "written for (v%d.%d-%d); commands added since then will be refused by the device"
                               % (version_reply.split("\r\n")[0], *FIRMWARE_FLOOR))
            if self._log is not None:
                self._log.write("event", {"event": "firmware-below-floor",
                                          "detail": version_reply.split("\r\n")[0]})
        found["commands"] = sorted(self.deviceCommands) if self.deviceCommands else []
        found["profile"] = self.profile.name
        return found

    def _reply_text(self, writebyte: str) -> str:
        reply = self.tinySA_serial(writebyte, printBool=False, _raw=True)
        return bytes(reply).decode("utf-8", errors="replace").strip() if reply else ""

######################################################################
# 4.0.0 gates
#   _check_command : is this command in the connected device's firmware?
#   _check_word    : is this argument word accepted by this device family?
#   _check_output_allowed : has the caller enabled the RF output?
# Each prints an ERROR message (so the log carries the reason) and returns
# False when the call must not be sent.
######################################################################

    def _check_command(self, name: str) -> bool:
        known = self.deviceCommands if self.deviceCommands is not None else self.profile.commands
        if name in known:
            return True
        where = "this device's firmware" if self.deviceCommands is not None else self.profile.name
        self.print_message("ERROR: '%s' is not a command in %s" % (name, where))
        return False

    def _check_word(self, command: str, word: object, words: tuple[str, ...]) -> bool:
        if str(word) in words:
            return True
        self.print_message("ERROR: %s does not accept '%s' on the %s; it takes %s"
                           % (command, word, self.profile.name, "|".join(words)))
        return False

    def set_output_allowed(self, allowed: bool = False) -> None:
        # The RF output gate. Off by default: output("on"), set_output_on() and
        # cal_output() with any value but "off" return the error value and send
        # nothing until set_output_allowed(True) has been called. Turning it on
        # sends nothing to the device. output("off") always works.
        self.outputAllowed = bool(allowed)
        if self._log is not None:
            self._log.write("event", {"event": "output-allowed", "detail": str(self.outputAllowed)})

    def get_output_allowed(self) -> bool:
        return self.outputAllowed

    def _check_output_allowed(self, what: str) -> bool:
        if self.outputAllowed:
            return True
        self.print_message("ERROR: %s refused: call set_output_allowed(True) first to enable the RF output" % what)
        return False

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
            if self._log is not None:
                self._log.write("event", {"event": "connect", "detail": str(port)})
                self._log_session()
            if self.identifyOnConnect:
                self.identify()
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
        if self._log is not None:
            self._log.write("event", {"event": "disconnect", "detail": ""})

    def tinySA_serial(self, writebyte: str, printBool: bool = False, pts: int | None = None,
                      _raw: bool = False) -> bytearray | None:
        # write out to serial, get message back, clean up, return
        #
        # 4.0.0: if the DEVICE rejects the command (a 'usage:' line for a setter,
        # 'name?' for a command this firmware lacks, or a refusal such as
        # 'usb disk mode active'), the error value is returned instead of the
        # device's text. _raw=True (used by command() and the readback helpers)
        # returns the device's text unchanged, as 3.x did for everything.

        ser = self._require_serial()
        # clear INPUT buffer
        ser.reset_input_buffer()
        # clear OUTPUT buffer
        ser.reset_output_buffer()

        started = time.monotonic()
        self._serial_busy = True
        self._serial_timed_out = False
        self._timed_out_partial = bytes()
        binary = False
        msgbytes: bytearray | None
        try:
            ser.write(bytes(writebyte, 'utf-8'))
            if pts is not None:
                # binary commands (scanraw): read by EXPECTED LENGTH, not by a
                # terminator byte. Any byte value (incl. '}' 0x7d and '>' 0x3e) can
                # occur inside the 16-bit sample data, so terminator scanning
                # truncates the frame. See get_binary_return().
                binary = True
                msgbytes = self.get_binary_return(pts)
            elif writebyte.strip().startswith('sd_read '):
                # SD card file: 4-byte little-endian length, then the bytes. Binary.
                binary = True
                msgbytes = self.get_sd_read_return()
            elif writebyte.strip() == 'capture':
                # the screen dump is binary too: pixel bytes can be 0x3e ('>'),
                # so it is read by length. See get_capture_return().
                binary = True
                msgbytes = self.get_capture_return()
            else:
                # text commands: read to the 'ch>' prompt, then clean
                raw = self.get_serial_return(echo=writebyte.strip())
                # a None here means the serial read itself failed; pass that through
                # rather than crashing in clean_return
                msgbytes = self.clean_return(raw) if raw is not None else None
        finally:
            self._serial_busy = False

        if self._serial_timed_out:
            status, reason = STATUS_TIMEOUT, "no prompt from the device within the timeout"
            if self._timed_out_partial:
                # keep what did arrive: it says whether the device echoed the
                # command, printed 'usage:', or said nothing at all
                reason += "; received: " + repr(self._timed_out_partial[-120:])
        elif binary:
            status, reason = classify_reply("", msgbytes)   # binary data is never 'usage'
        else:
            status, reason = classify_reply(writebyte, msgbytes)

        if self._log is not None:
            self._log_reason = ""
            self._log.write_command(sys._getframe(1).f_code.co_name, writebyte, status,
                                    int((time.monotonic() - started) * 1000),
                                    msgbytes, binary, reason)

        if printBool == True:
            print(msgbytes) #overrides verbose for debug

        if (not _raw) and status in (STATUS_USAGE, STATUS_UNKNOWN, STATUS_REFUSED):
            self.print_message("ERROR: device rejected '%s': %s" % (writebyte.strip(), reason))
            if msgbytes:
                self.print_message("device said: " + bytes(msgbytes).decode("utf-8", errors="replace").strip())
            self._log_reason = ""
            return bytearray(b'ERROR') if self.returnErrorByte else bytearray(b'')

        return msgbytes

    def get_serial_return(self, echo: str | None = None) -> bytearray | None:
        # while there's a buffer, read in the returned message
        # original buffer reading from: https://groups.io/g/tinysa/topic/tinysa_screen_capture_using/82218670
        #
        # echo: the command that was just written. The device echoes it as the
        # first line of its reply. When given, a prompt is only accepted AFTER
        # that echo has been seen; anything before it is a late reply to an
        # EARLIER command (one that timed out) and is discarded. Without this a
        # stale 'sweep cw ...\r\nch> ' left over from a timeout was returned as
        # the answer to the next command.

        ser = self._require_serial()
        buffer = bytes()
        start_time = time.monotonic()
        echo_bytes = bytes(echo, 'utf-8') if echo else None
        while True:
            if ser.in_waiting > 0:
                buffer += ser.read(ser.in_waiting)
                if echo_bytes is not None:
                    at = buffer.find(echo_bytes)
                    if at == -1:
                        # no echo yet: everything so far is stale output
                        if buffer.endswith((b'ch> ', b'ch>')):
                            self.print_message("discarding %d stale bytes from an earlier command" % len(buffer))
                            buffer = bytes()
                        continue
                    if at > 0:
                        buffer = buffer[at:]
                    echo_bytes = None              # found; stop checking
                # Firmware >= v1.4-222: when the sweep thread does not pick up a
                # command within 20 s the shell prints 'Command timeout' and
                # NO prompt. Treat that line as the end of the reply, so the
                # caller gets an error after ~20 s instead of waiting out the
                # library timeout (120 s by default) for a prompt that never comes.
                if buffer.rstrip().endswith(b'Command timeout'):
                    complete = buffer.rstrip()
                    break
                try:
                    # The reply ends with the prompt 'ch> '. Earlier versions
                    # stopped at the FIRST '>' byte, which cut short any reply
                    # whose text contained one (e.g. 'usage: deviceid [<number>]').
                    # The trailing space may arrive in a later USB packet, so
                    # either ending counts as complete; a stray space is
                    # discarded by reset_input_buffer() before the next command.
                    if buffer.endswith(b'ch> '):
                        complete = buffer[:-1]       # keep 'ch>' for clean_return
                    elif buffer.endswith(b'ch>'):
                        complete = buffer
                    else:
                        raise ValueError
                except ValueError:
                    # this is an acceptable err, so can skip it and keep looping
                    continue
                except Exception as err:
                    # otherwise, something else is wrong
                    self.print_message("ERROR: exception thrown while reading serial")
                    self.print_message(err)
                    return None
                break
            elif (self.serialTimeout is not None) and ((time.monotonic() - start_time) > self.serialTimeout):
                # only reachable when the user has set a timeout; the default waits forever
                self._serial_timed_out = True
                self._timed_out_partial = buffer
                self.print_message("WARNING: no prompt from the device after %.1f s (have %d bytes: %r)"
                                   % (self.serialTimeout, len(buffer), buffer[-80:]))
                return None
            else:
                # nothing waiting: yield instead of spinning a CPU core
                time.sleep(0.001)

        return bytearray(complete)

    def get_capture_return(self, idle_timeout: float = 0.5, timeout: float = 30.0) -> bytearray | None:
        # Reads the reply to 'capture': the echoed command line, then
        # screenWidth * screenHeight * 2 bytes of RGB565 pixel data, then the
        # 'ch> ' prompt with no line break in between.
        #
        # WHY THIS EXISTS (separate from get_serial_return):
        # get_serial_return stops at the first '>' (0x3e). Pixel data can
        # contain that byte, which cut the image short, and clean_return()
        # then removed 4 bytes for a 3-byte 'ch>', losing one more pixel byte
        # (the README example used to pad it back).
        #
        # TWO WAYS A FRAME ENDS:
        #   * Expected size: the pixel data is exactly screenWidth*screenHeight*2
        #     bytes and is followed by the prompt. Returned immediately.
        #   * Other size (screenWidth/screenHeight not set for this model, e.g.
        #     a Basic with the Ultra defaults): the stream ends with the prompt
        #     and then stays idle. Returned after idle_timeout.
        #
        # Returns ONLY the pixel bytes. None if nothing usable arrived.

        ser = self._require_serial()
        prompt = b'ch> '
        expected = self.screenWidth * self.screenHeight * 2
        limit = self.serialTimeout if self.serialTimeout is not None else timeout
        buffer = bytes()
        start_time = time.monotonic()
        last_data_time = start_time

        while True:
            if ser.in_waiting > 0:
                buffer += ser.read(ser.in_waiting)
                last_data_time = time.monotonic()
                echo_end = buffer.find(b'\r\n')
                if echo_end != -1:
                    payload = buffer[echo_end + 2:]
                    if payload[expected:expected + len(prompt)] == prompt:
                        return bytearray(payload[:expected])
            else:
                now = time.monotonic()
                echo_end = buffer.find(b'\r\n')
                if (echo_end != -1) and buffer.endswith(prompt) and ((now - last_data_time) > idle_timeout):
                    payload = buffer[echo_end + 2:-len(prompt)]
                    self.print_message(
                        "WARNING: capture returned %d bytes, expected %d for a %dx%d screen. "
                        "Check the screen size set for this device."
                        % (len(payload), expected, self.screenWidth, self.screenHeight))
                    return bytearray(payload)
                if (now - start_time) > limit:
                    self._serial_timed_out = True
                    self.print_message("WARNING: capture read timed out (have %d bytes, expected %d)"
                                       % (len(buffer), expected))
                    return None
                time.sleep(0.001)

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
    def get_sd_read_return(self, timeout: float = 60.0) -> bytearray | None:
        # Reads the reply to 'sd_read {filename}'. The firmware sends the echoed
        # command line, then a 4-byte little-endian file size, then exactly that
        # many bytes, then the 'ch> ' prompt. A missing file or missing card is
        # reported as text instead ('err: (4) no file') and has no length prefix.
        #
        # Returns ONLY the file bytes, or the error text as bytes, or None on timeout.
        ser = self._require_serial()
        limit = self.serialTimeout if self.serialTimeout is not None else timeout
        buffer = bytes()
        start_time = time.monotonic()
        while True:
            if ser.in_waiting > 0:
                buffer += ser.read(ser.in_waiting)
                echo_end = buffer.find(b'\r\n')
                if echo_end == -1:
                    continue
                payload = buffer[echo_end + 2:]
                if payload.startswith(b'err:'):
                    if payload.endswith(b'ch> '):
                        return bytearray(payload[:-4].rstrip(b'\r\n'))
                    continue
                if len(payload) >= 4:
                    size = int.from_bytes(payload[:4], 'little')
                    if len(payload) >= 4 + size:
                        return bytearray(payload[4:4 + size])
            elif (time.monotonic() - start_time) > limit:
                self._serial_timed_out = True
                self.print_message("WARNING: sd_read timed out (have %d bytes)" % len(buffer))
                return None
            else:
                time.sleep(0.001)

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

######################################################################
# Readback (getters)
#   The firmware has no dedicated "get" commands, but most setters print
#   their current value when sent with no argument or with '?', e.g.
#       rbw ?        ->  usage: rbw 0.2..850|auto\r\n10kHz
#       attenuate ?  ->  usage: attenuate 0..31|auto\r\n   0
#   These helpers send that query form and parse the value line. They
#   return None when the device gave no value (unknown command, no reply).
######################################################################

    def _query_value(self, command: str) -> str | None:
        # send a query and return the LAST non-usage line of the reply as text
        reply = self.tinySA_serial(command + '\r\n', printBool=False, _raw=True)
        if not reply:
            return None
        lines = [ln.strip() for ln in bytes(reply).decode("utf-8", errors="replace").splitlines()]
        lines = [ln for ln in lines if ln and not ln.startswith("usage:") and not ln.endswith("?")]
        return lines[-1] if lines else None

    def get_rbw(self) -> float | None:
        # current resolution bandwidth in kHz, e.g. 10.0 for '10kHz', 0.3 for '300Hz'
        text = self._query_value('rbw ?')
        if text is None:
            return None
        value = text.replace('Hz', '').strip()
        if value.endswith('k'):
            return float(value[:-1])
        if value.endswith('M'):
            return float(value[:-1]) * 1000.0
        return float(value) / 1000.0

    def get_attenuation(self) -> float | None:
        # current internal attenuation in dB
        text = self._query_value('attenuate ?')
        return None if text is None else float(text)

    def get_sweep_time(self) -> float | None:
        # current sweep time in seconds, e.g. 0.462 for '462ms'
        text = self._query_value('sweeptime ?')
        if text is None:
            return None
        value = text.strip()
        if value.endswith('ms'):
            return float(value[:-2]) / 1000.0
        if value.endswith('us'):
            return float(value[:-2]) / 1e6
        return float(value.rstrip('s'))

    def get_IF(self) -> float | None:
        # current intermediate frequency in Hz, e.g. 977400000.0 for '977.400000MHz'
        text = self._query_value('if ?')
        if text is None:
            return None
        value = text.strip()
        if value.endswith('MHz'):
            return float(value[:-3]) * 1e6
        if value.endswith('kHz'):
            return float(value[:-3]) * 1e3
        return float(value.replace('Hz', ''))

    def get_scanraw_offset(self) -> int | None:
        # the scanraw level offset as a number: 174 on the Ultra family, 128 on the Basic
        # (get_zero_offset() is the older alias that returns the raw reply)
        text = self._query_value('zero ?')
        return None if text is None else int(text.replace('dBm', '').strip())

    def get_noise_figure(self) -> float | None:
        # configured noise figure in dB (Ultra family)
        text = self._query_value('nf ?')
        return None if text is None else float(text)

    def get_dac_value(self) -> int | None:
        # current DAC value, 0..4095
        text = self._query_value('dac ?')
        if text is None:
            return None
        return int(text.split(':')[-1].strip())

    def get_calc(self) -> str | None:
        # current calc mode as the device prints it: OFF, MINH, MAXH, MAXD, AVER4, A16, AVER, QUASI...
        return self._query_value('calc ?')

    def get_sweep_range(self) -> tuple[int, int, int] | None:
        # (start_hz, stop_hz, points) from the bare 'sweep' command
        reply = self.tinySA_serial('sweep\r\n', printBool=False, _raw=True)
        if not reply:
            return None
        parts = bytes(reply).decode("utf-8", errors="replace").split()
        if len(parts) < 3:
            return None
        return int(parts[0]), int(parts[1]), int(parts[2])

    @staticmethod
    def decode_number(text: str | bytes) -> float:
        # Parse one number from a device reply, including the ':' artifact.
        #
        # tinySA firmware before v1.4-230 (July 2026) printed an exact power of
        # ten in scientific notation with ':' as the leading digit, because ':'
        # is the character after '9' and the mantissa was not normalised below
        # 10. So '-:.000000e+01' means -10.000000e+01, which is exactly -100.0.
        # The value is recoverable, and this does that; the examples in the
        # README used to replace it with a noise-floor number instead.
        if isinstance(text, (bytes, bytearray)):
            text = bytes(text).decode("utf-8", errors="replace")
        text = text.strip()
        if ':' in text:
            mantissa, _, exponent = text.partition('e')
            sign = -1.0 if mantissa.startswith('-') else 1.0
            digits = mantissa.lstrip('+-')
            if digits.startswith(':'):
                digits = '10' + digits[1:]
            else:
                digits = digits.replace(':', '')
            return sign * float(digits) * (10.0 ** int(exponent)) if exponent else sign * float(digits)
        return float(text)

    def is_rgb24(self, hexStr: str) -> bool:
        # check if the string matches the pattern 0xRRGGBB
        pattern = r"^0x[0-9A-Fa-f]{6}$"
        return bool(re.match(pattern, hexStr))
