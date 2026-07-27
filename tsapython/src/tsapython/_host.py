#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_host.py'
#
#   The type-checking contract between the tinySA host class (core.py) and the
#   command mixins under _commands/.
#
#   The mixins call a handful of methods and attributes that live on the host
#   class (tinySA_serial, print_message, error_byte_return, the device-limit
#   attributes, ...). That dependency used to be implicit; this base class makes
#   it explicit and lets mypy check each mixin standalone.
#
#   At RUNTIME this is an empty class: the declarations below only exist under
#   TYPE_CHECKING, so composition, behavior, and the MRO of the tinySA class
#   are unchanged. Because tinySA (core.py) really implements these members,
#   mypy also verifies the host's signatures stay compatible with what the
#   mixins expect -- the contract is enforced from both sides.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import serial


class MixinHost:
    if TYPE_CHECKING:
        # serial port (None until connect()/autoconnect() succeeds)
        ser: "serial.Serial | None"

        # message feedback
        verboseEnabled: bool
        returnErrorByte: bool

        # library mode flags
        ultraEnabled: bool
        abortEnabled: bool
        harmonicEnabled: bool

        # device parameter boundaries (library-side error checking)
        maxPoints: int
        minSADeviceFreq: float
        maxSADeviceFreq: float
        minSGDeviceFreq: float
        maxSGDeviceFreq: float
        maxDeviceBattery: int
        screenWidth: int
        screenHeight: int

        # host methods the mixins rely on (implemented in core.py)
        def tinySA_serial(
            self, writebyte: str, printBool: bool = ..., pts: "int | None" = ...
        ) -> "bytearray | None": ...

        def print_message(self, msg: object) -> None: ...

        def error_byte_return(self) -> bytearray: ...

        def is_rgb24(self, hexStr: str) -> bool: ...
