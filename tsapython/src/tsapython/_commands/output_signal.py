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

import typing
import warnings

from .._host import MixinHost
from .._identify import STATUS_OK

class OutputSignalMixin(MixinHost):
    def cal_output(self, val: int | float | str = "off") -> bytearray | None:
        # disables or sets the caloutput to a specified frequency in MHz
        # usage: caloutput off|30|15|10|4|3|2|1
        # example return: bytearray(b'')

        #explicitly allowed vals
        accepted_vals =  ["off", 'off', 1,2,3,4,10,15,30]
        #check input
        if (val in accepted_vals):
            if str(val) != "off" and not self._check_output_allowed("caloutput " + str(val)):
                return self.error_byte_return()
            writebyte = 'caloutput '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("caloutput() set with " + str(val))
        else:
            self.print_message("ERROR: caloutput() takes vals 1|2|3|4|10|15|30|\"off\"")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_cal_output_off(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output("off")

    def set_cal_output_30(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(30)

    def set_cal_output_15(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(15)

    def set_cal_output_10(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(10)

    def set_cal_output_4(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(4)

    def set_cal_output_3(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(3)

    def set_cal_output_2(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(2)

    def set_cal_output_1(self) -> bytearray | None:
        # alias for cal_output()
        return self.cal_output(1)

    def direct(self, val: int | float | str, freq: int | None = None) -> bytearray | None:
        # Output mode for generating a square wave signal between 830MHz and 1130MHz
        # usage: direct {start|stop|on|off} {freq(Hz)}
        # example return: ''

        if not self._check_command("direct"):
            return self.error_byte_return()

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

    def set_direct_on(self) -> bytearray | None:
        # alias for direct()
        return self.direct("on")

    def set_direct_off(self) -> bytearray | None:
        # alias for direct()
        return self.direct("off")

    def set_direct_start(self, freq: int) -> bytearray | None:
        # alias for direct()
        return self.direct("start", freq)

    def set_direct_stop(self, freq: int) -> bytearray | None:
        # alias for direct()
        return self.direct("stop", freq)

    def mode(self, val1: str = "low", val2: str = "input") -> bytearray | None:
        # sets the mode of the tinySA
        # usage: mode low|high input|output     Basic (ZS304)
        #        mode [low] input|output        Ultra family: there is no 'high'
        # On the Ultra family 'mode high ...' is answered with a usage line and
        # the mode does not change.
        # example return: ''

        #explicitly allowed vals
        accepted_val1 =  ["low", "high"]
        accepted_val2= ["input", "output"]
        #check input
        if (val1 in accepted_val1) and (val2 in accepted_val2):
            if not self._check_word("mode", val1, self.profile.mode_words):
                return self.error_byte_return()
            writebyte = 'mode '+str(val1)+ ' ' +str(val2)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: mode() takes vals [low|high] [input|output]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_low_input_mode(self) -> bytearray | None:
        # alias for mode()
        return self.mode("low", "input")

    def set_low_output_mode(self) -> bytearray | None:
        # alias for mode()
        return self.mode("low", "output")

    def set_high_input_mode(self) -> bytearray | None:
        # alias for mode(). Basic only
        return self.mode("high", "input")

    def set_high_output_mode(self) -> bytearray | None:
        # alias for mode(). Basic only
        return self.mode("high", "output")

    def modulation(self, val: int | float | str) -> bytearray | None:
        # sets the modulation in output mode
        # usage: modulation off|am|fm                 Ultra family (ZS405, ZS406, ZS407)
        #        modulation off|am|nfm|wfm|extern     Basic (ZS304)
        # The rate, AM depth and FM deviation are separate calls:
        #   modulation_freq(), modulation_depth(), modulation_deviation()
        #
        # FIRMWARE NOTE: 'AM_1kHz', 'AM_10Hz', 'NFM' and 'WFM' were the keywords
        # of tinySA firmware up to Nov 2020. Current firmware matches keywords
        # case-sensitively and rejects all four. They are still accepted HERE and
        # are translated to what current firmware takes:
        #   AM_1kHz -> 'modulation am' then 'modulation freq 1000'
        #   AM_10Hz -> 'modulation am' then 'modulation freq 10'
        #   NFM     -> 'modulation nfm'   (Basic only)
        #   WFM     -> 'modulation wfm'   (Basic only)
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["off", "am", "fm", "nfm", "wfm", "extern"]
        # older keywords: (keyword to send, modulation rate in Hz or None)
        legacy_vals: dict[str, tuple[str, int | None]] = {
            "AM_1kHz": ("am", 1000), "AM_10Hz": ("am", 10),
            "NFM": ("nfm", None), "WFM": ("wfm", None)}
        #check input
        if (str(val) in accepted_vals):
            if not self._check_word("modulation", val, self.profile.modulation_words):
                return self.error_byte_return()
            writebyte = 'modulation '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        elif (str(val) in legacy_vals):
            keyword, rate = legacy_vals[str(val)]
            if not self._check_word("modulation", keyword, self.profile.modulation_words):
                return self.error_byte_return()
            writebyte = 'modulation '+keyword+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            if rate is not None:
                writebyte = 'modulation freq '+str(rate)+'\r\n'
                msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: modulation() takes vals [off|am|fm|nfm|wfm|extern]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def modulation_freq(self, val: int | float) -> bytearray | None:
        # sets the modulation rate in Hz (the frequency of the modulating tone)
        # usage: modulation freq {Hz}
        # The device limits the value to 1..10000 Hz (3500 Hz for FM on the Ultra family).
        # example return: ''

        if isinstance(val, (int, float)) and (not isinstance(val, bool)) and (1 <= val <= 10000):
            writebyte = 'modulation freq '+str(int(val))+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: modulation_freq() takes a rate in Hz [1 - 10000]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def modulation_depth(self, val: int | float) -> bytearray | None:
        # sets the AM depth in percent. Ultra family only
        # usage: modulation depth {percent}
        # example return: ''

        if "fm" not in self.profile.modulation_words:     # depth exists only where fm does (Ultra family)
            self.print_message("ERROR: 'modulation depth' is not available on the %s" % self.profile.name)
            return self.error_byte_return()
        if isinstance(val, (int, float)) and (not isinstance(val, bool)) and (0 <= val <= 100):
            writebyte = 'modulation depth '+str(int(val))+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: modulation_depth() takes a depth in percent [0 - 100]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def modulation_deviation(self, val: int | float) -> bytearray | None:
        # sets the FM deviation in Hz. Ultra family only
        # usage: modulation deviation {Hz}
        # The device stores the deviation in steps of 100 Hz.
        # example return: ''

        if "fm" not in self.profile.modulation_words:     # deviation exists only where fm does (Ultra family)
            self.print_message("ERROR: 'modulation deviation' is not available on the %s" % self.profile.name)
            return self.error_byte_return()
        if isinstance(val, (int, float)) and (not isinstance(val, bool)) and (100 <= val <= 300000):
            writebyte = 'modulation deviation '+str(int(val))+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: modulation_deviation() takes a deviation in Hz [100 - 300000]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_mod_off(self) -> bytearray | None:
        # alias for modulation()
        return self.modulation("off")

    def set_mod_AM(self) -> bytearray | None:
        # alias for modulation(). Set the rate with modulation_freq()
        return self.modulation("am")

    def set_mod_FM(self) -> bytearray | None:
        # alias for modulation(). Ultra family only
        return self.modulation("fm")

    def set_mod_AM_1khz(self) -> bytearray | None:
        # DEPRECATED: the 'AM_1kHz' keyword left the tinySA firmware in Nov 2020.
        # Still callable: sends 'modulation am' then 'modulation freq 1000'.
        # Use modulation("am") and modulation_freq(1000) instead.
        warnings.warn("set_mod_AM_1khz() is deprecated; use modulation('am') and modulation_freq(1000)",
                      DeprecationWarning, stacklevel=2)
        return self.modulation("AM_1kHz")

    def set_mod_AM_10Hz(self) -> bytearray | None:
        # DEPRECATED: the 'AM_10Hz' keyword left the tinySA firmware in Nov 2020.
        # Still callable: sends 'modulation am' then 'modulation freq 10'.
        # Use modulation("am") and modulation_freq(10) instead.
        warnings.warn("set_mod_AM_10Hz() is deprecated; use modulation('am') and modulation_freq(10)",
                      DeprecationWarning, stacklevel=2)
        return self.modulation("AM_10Hz")

    def set_mod_NFM(self) -> bytearray | None:
        # alias for modulation(). Basic only; sends 'modulation nfm'
        return self.modulation("NFM")

    def set_mod_WFM(self) -> bytearray | None:
        # alias for modulation(). Basic only; sends 'modulation wfm'
        return self.modulation("WFM")

    def set_mod_extern(self) -> bytearray | None:
        # alias for modulation(). Basic only
        return self.modulation("extern")

    def output(self, val: int | float | str) -> bytearray | None:
        # sets the output on or off
        # usage: output on|off
        #        output normal|mixer   Ultra family only: selects the output path.
        #                              These two do not switch the output on or off.
        # example return: ''

        # explicitly allowed vals
        accepted_vals =  ["on", "off", "normal", "mixer"]
        #check input
        if (str(val) in accepted_vals):
            if not self._check_word("output", val, self.profile.output_words):
                return self.error_byte_return()
            if str(val) == "on" and not self._check_output_allowed("output on"):
                return self.error_byte_return()
            writebyte = 'output '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: output() takes vals [on|off|normal|mixer]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_output_on(self) -> bytearray | None:
        #alias for output()
        return self.output("on")

    def set_output_off(self) -> bytearray | None:
        #alias for output()
        return self.output("off")

    def set_output_path_normal(self) -> bytearray | None:
        #alias for output(). Ultra family only
        return self.output("normal")

    def set_output_path_mixer(self) -> bytearray | None:
        #alias for output(). Ultra family only
        return self.output("mixer")

    def setup_generator(self, freq_hz: int | float, level_dbm: int | float,
                        modulation_type: str = "off", modulation_rate_hz: int | float | None = None,
                        high: bool = False) -> bool:
        # Puts the device into signal generator mode in the order the firmware
        # needs, and leaves the output OFF:
        #   output off -> mode low|high output -> pause -> level -> sweep cw
        #   -> modulation -> resume
        # The level is set after the mode because the firmware resets the level
        # to maximum whenever the mode changes. Switching the output on is a
        # separate, explicit call: set_output_allowed(True) then output("on").
        # high=True selects the Basic's high output mode (refused on the Ultra family).
        # Returns True if every step was accepted.
        #
        # WHY THE PAUSE (seen on hardware, ZS405 v1.4-252): in output mode,
        # 'level', 'sweep', 'rbw', 'attenuate', 'mode' and other settings run in
        # the firmware's sweep thread BETWEEN sweeps, and a generator sweep is
        # seconds long, so each of them waited about 20 s for its prompt. While
        # the sweep is paused the firmware runs them immediately. 'output' and
        # 'modulation' do not go through the sweep thread and return at once.
        # Use the same pattern in your own scripts: pause(), settings, resume().
        steps: list[typing.Callable[[], object]] = [
            lambda: self.output("off"),
            lambda: self.mode("high" if high else "low", "output"),
            lambda: self.output("off"),           # the mode change already muted; be explicit
            lambda: self.pause(),
            lambda: self.level(level_dbm),
            lambda: self.set_sweep_cw(int(freq_hz)),
            lambda: self.modulation(modulation_type)]
        if modulation_rate_hz is not None and str(modulation_type) != "off":
            steps.append(lambda: self.modulation_freq(modulation_rate_hz))
        steps.append(lambda: self.resume())
        return self._run_steps(steps, "setup_generator()")

    def _run_steps(self, steps: "list[typing.Callable[[], object]]", name: str) -> bool:
        # Runs each step and checks HOW it ended (get_last_status), not what it
        # returned: in the default error mode an accepted setter and a rejected
        # one both return b''. Stops at the first step that was not accepted
        # and resumes the sweep so the device is not left paused.
        for step in steps:
            step()
            status = self.get_last_status()
            if status != STATUS_OK:
                self.print_message("ERROR: %s stopped at a refused step (%s); output is off" % (name, status))
                self.resume()
                self._last_status = status      # report the failure, not the resume
                return False
        return True

    def set_generator(self, level_dbm: int | float | None = None, freq_hz: int | float | None = None,
                      modulation_type: str | None = None, modulation_rate_hz: int | float | None = None,
                      depth_percent: int | float | None = None, deviation_hz: int | float | None = None) -> bool:
        # Changes generator settings while already in output mode (output on or
        # off): pause -> the given settings -> resume. The pause is what makes
        # 'level' and 'sweep cw' return at once in output mode (see
        # setup_generator); the resume lets the next generator sweep apply them.
        # Only the arguments given are sent. Returns True if every step was accepted.
        steps: list[typing.Callable[[], object]] = [lambda: self.pause()]
        if level_dbm is not None:
            steps.append(lambda: self.level(level_dbm))
        if freq_hz is not None:
            steps.append(lambda: self.set_sweep_cw(int(freq_hz)))
        if modulation_type is not None:
            steps.append(lambda: self.modulation(modulation_type))
        if modulation_rate_hz is not None:
            steps.append(lambda: self.modulation_freq(modulation_rate_hz))
        if depth_percent is not None:
            steps.append(lambda: self.modulation_depth(depth_percent))
        if deviation_hz is not None:
            steps.append(lambda: self.modulation_deviation(deviation_hz))
        steps.append(lambda: self.resume())
        return self._run_steps(steps, "set_generator()")

    def ultra(self, val: int | float | str = "off", freq: int | float | str | None = None) -> bytearray | None:
        # turn on/config tiny SA ultra mode
        # usage: ultra off|on|auto|start|harm {freq}
        # example return: bytearray(b'')

        if not self._check_command("ultra"):
            return self.error_byte_return()

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

    def set_ultra_on(self) -> bytearray | None:
        return self.ultra("on")

    def set_ultra_off(self) -> bytearray | None:
        return self.ultra("off")

    def set_ultra_auto(self) -> bytearray | None:
        return self.ultra("auto")

    def set_ultra_start(self, val: int | float | str) -> bytearray | None:
        return self.ultra("start", val)

    def set_ultra_harmonic(self, val: int | float | str) -> bytearray | None:
        return self.ultra("harm", val)
