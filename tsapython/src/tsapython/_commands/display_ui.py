#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/display_ui.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

import numpy as np
import re

from .._host import MixinHost

class DisplayUIMixin(MixinHost):
    def bulk(self) -> bytearray | None:
        # sent by tinySA when in auto refresh mode
        # format: "bulk\r\n{X}{Y}{Width}{Height}
        # {Pixeldata}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian. The Pixeldata is
        # encoded as 2 bytes per pixel. similar to fill()

        writebyte = 'bulk\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("bulk() called for screen data")   
        return msgbytes

    def get_bulk_data(self) -> bytearray | None:
        # alias for bulk()
        return self.bulk()

    def capture(self) -> bytearray | None:
        # requests a screen dump to be sent in binary format 
        # of 320x240 pixels of each 2 bytes
        # usage: capture
        # example return: bytearray(b'\x00 ...\x00\x00\x00')
        writebyte = 'capture\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("capture() called for screen data")   
        return msgbytes

    def capture_screen(self) -> bytearray | None:
        return self.capture()

    def color(self, ID: int | None = None, RGB: str | None = '0xF8FCF8') -> bytearray | None:
        # sets or dumps the colors used
        # usage: color [{id} {rgb24}]
        # example return: 
         
        # explicitly allowed vals
        accepted_ID = np.arange(0, 31, 1) # max exclusive

        if ID == None:
            # get the color       
            writebyte = 'color\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
        elif (ID in accepted_ID) and (RGB is not None) and (self.is_rgb24(RGB)==True):
            # set the color based on ID       
            writebyte = 'color ' + str(ID) + ' ' + str(RGB) + '\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("color() set with ID: " +str(ID) + " RGB: " + str(RGB))
        else:
            self.print_message("ERROR: color() takes either None, or ID as int 0..31 and RGB as a hex value")
            msgbytes = self.error_byte_return()
        return msgbytes

    def get_all_colors(self) -> bytearray | None:
        # alias for color(). returns array of all colors
        return self.color()

    def get_color(self, ID: int) -> "str | bytearray | None":
        # alias for color(). val must be int 1-31
        # returns the rgb24 value as a str (e.g. '0x00FC00') if found; otherwise
        # passes the color() return (or the error byte) through
        msgbytes = self.color()
        # check if something has been returned, otherwise pass the error through
        if (msgbytes is not None) and (len(msgbytes) > 10):
            # Use regex to find the value at index ID. The device reply is a
            # bytearray, so decode before matching with a str pattern.
            pattern = rf'\b{int(ID)}:\s*0x([0-9A-Fa-f]+)'
            match = re.search(pattern, msgbytes.decode("utf-8", errors="replace"))
            if match:
                return f"0x{match.group(1)}" #return rgb24 value if found
        
            # if not found, then 
            self.print_message("ERROR: color() takes either None, or ID as int 0..31 and RGB as a hex value")
            return self.error_byte_return()
        return msgbytes

    def set_color(self, ID: int, val: str) -> bytearray | None:
        # alias for color()
        return self.color(ID, val)

    def fill(self) -> bytearray | None:
        # sent by tinySA when in auto refresh mode
        # format: "fill\r\n{X}{Y}{Width}{Height}
        # {Color}\r\n"
        # where all numbers are binary coded 2
        # bytes little endian. Similar ot bulk()

        writebyte = 'fill\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("fill() called for screen data")   
        return msgbytes

    def get_fill_data(self) -> bytearray | None:
        # alias for fill()
        return self.fill()

    def menu(self, val: int | float | str) -> bytearray | None:
        # The menu command can be used to activate any menu item
        # usage: menu {#} [{#} [{#} [{#}]]]
        # example return: ''

        writebyte = 'menu ' + str(val) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("clicking menu button")
        return msgbytes 

    def refresh(self, val: int | float | str) -> bytearray | None:
        # enables/disables the auto refresh mode
        # usage: refresh on|off
        # example return: ''

        #explicitly allowed vals
        accepted_vals =  ["on", "off"]
        #check input
        if (str(val) in accepted_vals):
            writebyte = 'refresh '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("refresh() set to " + str(val))           
        else:
            self.print_message("ERROR: refresh() takes vals [on|off]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def refresh_on(self) -> bytearray | None:
        # alias for refresh()
        return self.refresh("on")

    def refresh_off(self) -> bytearray | None:
        # alias for refresh()
        return self.refresh("off")

    def release(self) -> bytearray | None:
        # signals a removal of the touch
        # usage: release
        # example return: bytearray(b'')

        writebyte = 'release\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("sending touch release signal")
        return msgbytes 

    def text(self, val: int | float | str = "") -> bytearray | None:
        # specifies the text entry for the active keypad 
        # usage: text(val="")
        # example return: b''
       
        if len(str(val))>0:
            writebyte = 'text ' + str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("text() entered is " + str(val))
        else:
            self.print_message("ERROR: text needs non-empty values")
            msgbytes = self.error_byte_return()
        return msgbytes 

    def touch(self, x: int = 0, y: int = 0) -> bytearray | None:
        # sends the coordinates of a touch. 
        # The upper left corner of the screen is 0 0
        # usage: touch {X coordinate} {Y coordinate}
        # example return:

        # check if valid x
        msgbytes: bytearray | None
        if (x<0) or (self.screenWidth<x):
            self.print_message("ERROR: touch() needs a valid x coordinate")
            msgbytes = self.error_byte_return()
            return msgbytes 
        # check if valid y
        if (y<0) or (self.screenHeight<y):
            self.print_message("ERROR: touch() needs a valid y coordinate")
            msgbytes = self.error_byte_return()
            return msgbytes 
        writebyte = 'touch ' + str(x) + ' ' + str(y) + '\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("setting the touch() (" + str(x)+"," + str(y) + ")")
        return msgbytes 

    def preform_touch(self, x: int = 0, y: int = 0) -> bytearray | None:
        #alias for touch()
        return self.touch(x,y)

    def touch_cal(self) -> bytearray | None:
        # starts the touch calibration
        # usage: touchcal
        # example return: bytearray(b'')
        writebyte = 'touchcal\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("starting touchcal")
        return msgbytes

    def start_touch_cal(self) -> bytearray | None:
        return self.touch_cal()

    def touch_test(self) -> bytearray | None:
        # starts the touch test
        # usage: touchtest
        # example return: bytearray(b'')
        
        writebyte = 'touchtest\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("starting the touch_test()")
        return msgbytes

    def start_touch_test(self) -> bytearray | None:
        return self.touch_test()