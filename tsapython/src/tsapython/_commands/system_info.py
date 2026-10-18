#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/system_info.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

from .._host import MixinHost

class SystemInfoMixin(MixinHost):
    def command(self, val: int | float | str) -> bytearray | None:
        # if the command isn't already a function,
        #  use existing func setup to send command
        # 4.0.0: command() returns whatever the device printed, including usage
        # lines and 'name?'. It is the raw escape hatch and is not gated.
        writebyte = str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False, _raw=True)
        self.print_message("command() called with ::" + str(val))
        return msgbytes


    def dac(self, val: int | float | str | None = None) -> bytearray | None:
        # sets or dumps the dac value
        # usage: dac [0..4095]
        # example return: bytearray(b'usage: dac {value(0-4095)}\r\ncurrent value: 1922\r')

        if val is None:
            #get the dac
            writebyte = 'dac\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        elif (isinstance(val, (int, float))) and (0<= val <=4095):
            writebyte = 'dac '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("dac set to " + str(val))
        else:
            self.print_message("ERROR: dac() takes either None or integers")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_dac(self, val: int | float | str) -> bytearray | None:
        # alias for dac()
        return self.dac(val)

    def get_dac(self) -> bytearray | None:
        # alias for dac()
        return self.dac()

    def info(self) -> bytearray | None:
        # displays various SW and HW information
        # usage: info
        # example return: bytearray(b'tinySA ...\r')

        writebyte = 'info\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("returning device info()")
        return msgbytes

    def get_info(self) -> bytearray | None:
        # alias for info()
        return self.info()

    def channel(self, val: int | None = None) -> bytearray | None:
        # prints the channel power value(s) from the channel power measurement
        # usage: channel [1-3]
        # Needs tinySA firmware v1.4-223 (Mar 2026) or later; older firmware answers 'channel?'
        # example return: bytearray(b'channel[1] : -90.0\r\nchannel[2] : ...')
        if not self._check_command("channel"):
            return self.error_byte_return()
        if val is None:
            writebyte = 'channel\r\n'
        elif val in (1, 2, 3):
            writebyte = 'channel ' + str(val) + '\r\n'
        else:
            self.print_message("ERROR: channel() takes None or 1..3")
            return self.error_byte_return()
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("reading channel power")
        return msgbytes

    def time(self, field: str | None = None, val: int | None = None) -> bytearray | None:
        # reads or sets the real-time clock. Ultra family only
        # usage: time                 -> prints the usage line and the current date/time
        #        time y|m|d|h|min|sec {0-99}
        # example return: bytearray(b'usage: time ...\r\n2026/10/17 13:40:29\r')
        accepted = ["y", "m", "d", "h", "min", "sec"]
        if not self._check_command("time"):
            return self.error_byte_return()
        if field is None:
            writebyte = 'time\r\n'
        elif (field in accepted) and isinstance(val, int) and (0 <= val <= 99):
            writebyte = 'time ' + field + ' ' + str(val) + '\r\n'
        else:
            self.print_message("ERROR: time() takes (None) or (field in y|m|d|h|min|sec, 0..99)")
            return self.error_byte_return()
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        return msgbytes

    def usbdisk(self, val: str | None = None) -> bytearray | None:
        # reads or sets USB DISK mode, which presents the SD card as a USB drive.
        # WHILE IT IS ON, most other serial commands answer 'usb disk mode active'.
        # usage: usbdisk [off|on]
        # Needs tinySA firmware v1.4-244 (Sep 2026) or later, Ultra family.
        if not self._check_command("usbdisk"):
            return self.error_byte_return()
        if val is None:
            writebyte = 'usbdisk\r\n'
        elif str(val) in ("on", "off"):
            writebyte = 'usbdisk ' + str(val) + '\r\n'
        else:
            self.print_message("ERROR: usbdisk() takes None, 'on' or 'off'")
            return self.error_byte_return()
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        return msgbytes

    def nf(self) -> bytearray | None:
        # get the noise floor in dB.
        # This function CAN be used to set nf,
        # but that might bypass a measurement process. UNKNOWN right now.
        # usage: nf {value}\r\n
        # example return: ''
        if not self._check_command("nf"):
            return self.error_byte_return()
        writebyte = 'nf\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("getting saved noise floor value")
        return msgbytes

    def get_nf(self) -> bytearray | None:
        # alias function for nf()
        return self.nf()

    def rbw(self, val: int | float | str = "auto") -> bytearray | None:
        # sets the rbw to either automatic or a specific value.
        # the number specifies the target rbw in kHz
        # usage: rbw auto|0.2..850 (Ultra family), auto|2..600 (Basic)
        # decimals allowed, e.g. rbw(0.3) for 300 Hz
        # NOTE: rbw() with no argument SETS auto. It does not read the value.
        # example return: ''

        #check input
        if (val == "auto"):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        elif (isinstance(val, (int, float))) and (not isinstance(val, bool)):
            writebyte = 'rbw '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        else:
            self.print_message("ERROR: rbw() takes 'auto' or a number in kHz")
            msgbytes = self.error_byte_return()
        return msgbytes

    def set_rbw_auto(self) -> bytearray | None:
        # alias for rbw()
        return self.rbw("auto")

    def self_test(self, val: int = 0) -> bytearray | None:
        # performs one or all selftests
        # usage: selftest 0 0..9.
        # 0 appears to be 'run all'
        # example return: msgbytes = bytearray(b'')

        #check input
        if (isinstance(val, int)):
            writebyte = 'selftest ' + str(val) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("SELFTEST RUNNING. CHECK CONNECTION CAL to RF")
        else:
            self.print_message("ERROR: self_test() takes interger vals. 0 to run all.")
            msgbytes = self.error_byte_return()
        return msgbytes

    def status(self) -> bytearray | None:
        # displays the current device status (paused/resumed)
        # usage: status
        # example return: bytearray(b'Resumed\r')

        writebyte = 'status\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("getting device status() paused/resumed")
        return msgbytes

    def get_status(self) -> bytearray | None:
        # alias for status()
        return self.status()

    def temp(self) -> bytearray | None:
        # gets the temperature
        # usage: k   (NOTE: single letter command)
        # example return:
        #  b'43.25\r'
        writebyte = 'k\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("getting temperature")
        return msgbytes

    def get_temp(self) -> bytearray | None:
        # alias for temp()
        return self.temp()

    def threads(self) -> bytearray | None:
        # lists information of the threads in the tinySA
        # usage: threads
        # example return:
        # bytearray(b'stklimit| ...\r')

        writebyte = 'threads\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("returning thread information for device")
        return msgbytes

    def usart_cfg(self) -> bytearray | None:
        # gets the current serial config
        # usage: usart_cfg
        # example return: bytearray(b'Serial: 115200 baud\r')

        writebyte = 'usart_cfg\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("usart_cfg() returning config vals")
        return msgbytes

    def get_usart_cfg(self) -> bytearray | None:
        #alias for usart_cfg()
        return self.usart_cfg()

    def vbat(self) -> bytearray | None:
        # displays the battery voltage
        # usage: vbat
        # example return: bytearray(b'4132 mV\r')
        writebyte = 'vbat\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("returning current battery voltage")
        return msgbytes

    def get_vbat(self) -> bytearray | None:
        # alias for vbat
        return self.vbat()

    def version(self) -> bytearray | None:
        # displays the version text
        # usage: version
        # example return: tinySA4_v1.4-143-g864bb27\r\nHW Version:V0.4.5.1.1

        writebyte = 'version\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("getting device version information")
        return msgbytes

    def get_version(self) -> bytearray | None:
        # alias for version()
        return self.version()

######################################################################
# Device and library help
######################################################################

    def help(self, val: int = 0) -> "bytes | bytearray | None":
        # val controls if the tinySA help is called or the
        # 1 = library_help(), everything else is the tinySA_help()

        if val == 1:
            msgbytes = self.library_help()
        else:
            msgbytes = self.tinySA_help()
        return msgbytes

    def library_help(self) -> "bytes | bytearray | None":
        self.print_message("Returning command options for this library")
        self.print_message("IN PROGRESS. Include tinySA_help.py")

        return b''

    def tinySA_help(self) -> bytearray | None:
        # dumps a list of the available commands
        # usage: help
        # example return: bytearray(b'commands: freq time dac
        # nf saveconfig clearconfig zero sweep pause resume wait
        #  repeat status caloutput save recall trace trigger
        #  marker line usart_cfg vbat_offset color if if1 lna2
        # agc actual_freq freq_corr attenuate level sweeptime
        #  leveloffset levelchange modulation rbw mode spur
        # lna direct ultra load ext_gain output deviceid
        # correction calc menu text remark\r\nOther commands:
        #  version reset data frequencies scan hop scanraw test
        # touchcal touchtest usart capture refresh touch release
        #  vbat help info selftest sd_list sd_read sd_delete
        # threads\r')

        writebyte = 'help\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)
        self.print_message("Returning command options for tinySA device")
        return msgbytes
