#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_commands/acquisition.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Part of the tsapython package. This module is a mixin for the tinySA class in core.py;
#   it is not intended to be instantiated on its own.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

class AcquisitionMixin:
    def data(self, val=0):
        # dumps the trace data. 
        # usage: data [0-2]
        # 0=temp value, 1=stored trace, 2=measurement
        # example return: bytearray(b'-8.671875e+01\r\n... -8.337500e+01\r\n-8.237500e+01\r')
        
        #explicitly allowed vals
        accepted_vals = [0,1,2]
        #check input
        if val in accepted_vals:
            writebyte = 'data '+str(val)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)  
            if val == 0:
                self.print_message("returning temp value data") 
            elif val == 1:
                self.print_message("returning stored trace data") 
            elif val == 2:
                self.print_message("returning measurement data") 
        else:
            self.print_message("ERROR: data() takes vals [0-2]")
            msgbytes = self.error_byte_return()
        return msgbytes

    def get_temporary_data(self):
        # alias func for data()
        return self.data(val=0)

    def get_stored_trace_data(self):
        # alias func for data()
        return self.data(val=1)

    def dump_measurement_data(self):
        # alias func for data()
        return self.data(val=2)

    def frequencies(self):
        # gets the frequencies used by the last sweep
        # usage: frequencies
        # example return: bytearray(b'1500000000\r\n... \r\n3000000000\r')

        writebyte = 'frequencies\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("getting frequencies from the last sweep")
        return msgbytes

    def get_last_freqs(self):
        # get frequencies of last sweep
        return self.frequencies()

    def hop(self, start, stop, inc, outmask=None):
        # this is a measurement, maybe a sample measurement. format looks like hop freqval integer
        # usage: hop {start(Hz)} {stop(Hz)} {step(Hz) | points} [outmask]
        # outmask: 1 is frequency, 2 is level
        # example return: ''

        if (isinstance(start, (int, float))) and (isinstance(stop, (int, float))) and (isinstance(inc, (int, float))):
            if (isinstance(outmask, int)) and (0<outmask<3):
                writebyte = 'hop ' + str(start) + ' ' + str(stop)  + ' ' + str(inc) + ' ' + str(outmask) + '\r\n'

            elif outmask ==None:
                writebyte = 'hop ' + str(start) + ' ' + str(stop) + ' ' + str(inc) + '\r\n'

            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("sampling over frequency range")
            return msgbytes

        else: 
            self.print_message("hop() takes arguments start=Int, stop=Int, inc=Int, outmask=None|Int")

        return None

    def get_sample_pts(self, start, stop, pts):
        # alias for hop()
        return self.hop(start, stop, pts, outmask=1)

    def pause(self):
        # pauses the sweeping in either input or output mode
        # usage: pause
        # example return: ''

        writebyte = 'pause\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("pausing tinySA device")
        return msgbytes 

    def resume(self):
        # resumes the sweeping in either input or output mode
        # usage: resume
        # example return: ''

        writebyte = 'resume\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False) 
        self.print_message("resuming sweep")
        return msgbytes 

    def scan(self, start, stop, pts=250, outmask=None):
        # Performs a scan and optionally outputs the measured data.
        # usage: scan {start(Hz)} {stop(Hz)} [points] [outmask]
            # where the outmask is a binary OR of:
            # 1=frequencies, 2=measured data,
            # 4=stored data and max points is device dependent

        if (0<=start) and (start < stop) and (pts <= self.maxPoints):
            if outmask == None:
                writebyte = 'scan '+str(start)+' '+str(stop)+' '+str(pts)+'\r\n'
            else: 
                 writebyte = 'scan '+str(start)+' '+str(stop)+' '+str(pts)+ ' '+str(outmask)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)
            self.print_message("scanning...")           
        else:
            self.print_message("ERROR: scan takes START STOP PTS OUTMASK as args. Check doc for format and limits")
            msgbytes = self.error_byte_return()
        return msgbytes

    def scan_raw(self, start, stop, pts=250, unbuf=1):
        # performs a scan of unlimited amount of points 
        # and sends the data in binary form
        # usage: scanraw {start(Hz)} {stop(Hz)} [points] [unbuffered]
            # The measured data is sent as:
            #  '{' ('x' MSB LSB)*points '}' 
            #  where the 16 bit data is scaled by 32 & shifted based on device.
            # the README has examples for processing

        if (0<=start) and (start < stop) and (pts <= self.maxPoints):
            if (unbuf == 1) or (unbuf==2) or (unbuf==3):
                writebyte = 'scanraw '+str(start)+' '+str(stop)+' '+str(pts)+ ' '+str(unbuf)+'\r\n'

                # write out to serial, get message back, clean up, return
                self.print_message("scanning...")  
                msgbytes = self.tinySA_serial(writebyte, printBool=False, pts=pts) #pts added for error checking
                return msgbytes
            else:
                self.print_message("ERROR: unrecognized UBUF for scanraw")
                msgbytes = self.error_byte_return()
        else:
            self.print_message("ERROR: scanraw takes START STOP PTS UNBUF as args. Check doc for format and limits")
            msgbytes = self.error_byte_return()
        return msgbytes

    def continious_scanraw(self, start, stop, pts=250, unbuf=1, count=None):
        # Continuous SCANRAW acquisition.
        #
        # The tinySA returns exactly ONE binary frame per scanraw call (it does
        # not open an unbounded multi-frame stream over USB, even with the
        # 'continuous' bit set in unbuf). So continuous acquisition is done by
        # calling scan_raw() repeatedly. This is a GENERATOR: it yields one raw
        # frame per iteration so the caller can decode/plot/store as they go.
        #
        # usage:
        #     for frame in tsa.continious_scanraw(start, stop, pts):
        #         ...process frame...           # runs until you break
        #
        #     for frame in tsa.continious_scanraw(start, stop, pts, count=10):
        #         ...process frame...           # stops after 10 frames
        #
        # Each yielded value is the raw bytes from scan_raw() for that sweep
        # ('{' + 3*pts data bytes). Decode like the scanraw examples (skip the
        # leading '{', struct.unpack '<' + 'xH'*pts, then /32 - SCALE for dBm).
        #
        # count: number of frames to yield. None = run indefinitely (break out
        #        of the loop, or stop iterating, to end).

        # validate once up front (same checks as scan_raw) so a bad call fails
        # immediately rather than on the first iteration.
        if not ((0 <= start) and (start < stop) and (pts <= self.maxPoints)):
            self.print_message("ERROR: continious_scanraw takes START STOP PTS UNBUF; check limits")
            return
        if unbuf not in (1, 2, 3):
            self.print_message("ERROR: unrecognized UNBUF for continious_scanraw")
            return

        emitted = 0
        while (count is None) or (emitted < count):
            frame = self.scan_raw(start, stop, pts, unbuf)
            yield frame
            emitted += 1

    def config_sweep(self, argName=None, val=None): 
            # split call for SWEEP
            # Set sweep boundaries.
            # Sweep without arguments lists the current sweep 
            # settings. The frequencies specified should be 
            # within the permissible range. The sweep commands 
            # apply both to input and output modes        
            # usage: 
            # sweep [(start|stop|center|span|cw {frequency}) | 
            #   ({start(Hz)} {stop(Hz)} [0..290])]
            # EXAMPLES:
            # sweep start {frequency}: sets the start frequency of the sweep.
            # sweep stop {frequency}: sets the stop frequency of the sweep.
            # sweep center {frequency}: sets the center frequency of the sweep.
            # sweep span {frequency}: sets the span of the sweep.
            # sweep cw {frequency}: sets the continuous wave frequency (zero span sweep). 
            # # example return:  b'' 

        # explicitly allowed vals
        accepted_table_args = ["start", "stop", "center", 
                               "span", "cw"]

        if (argName==None) and (val==None):
            # do sweep
            writebyte = 'sweep\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)

        elif (argName in accepted_table_args): 
            if val == None:
                #error
                self.print_message("ERROR: sweep " + str(argName) + " needs a value")
                msgbytes = self.error_byte_return()
            else:
                #do stuff, error checking needed
                writebyte = 'sweep ' + str(argName)+ ' ' + str(val)+ '\r\n'
                self.print_message("sweep " +str(argName) + " is " + str(val))
                msgbytes = self.tinySA_serial(writebyte, printBool=False)

        else: #not in table of accepted args, so doesn't matter what val is
            self.print_message("ERROR: " + str(argName) + " invalid argument for sweep")
            msgbytes = self.error_byte_return()

        return msgbytes

    def get_sweep_params(self):
        # alias for config_sweep() 
        return self.config_sweep()

    def set_sweep_start(self, val):
        # alias for config_sweep() 
        return self.config_sweep("start", val)

    def set_sweep_stop(self, val):
        # alias for config_sweep() 
        return self.config_sweep("stop", val)

    def set_sweep_center(self, val):
        # alias for config_sweep() 
        return self.config_sweep("center", val)

    def set_sweep_span(self, val):
        # alias for config_sweep() 
        return self.config_sweep("span", val)

    def set_sweep_cw(self, val):
        # alias for config_sweep() 
        return self.config_sweep("cw", val)   

    def run_sweep(self, startVal=None, stopVal=None, pts=250):
            # split call for SWEEP
            # Execute sweep.
            # The frequencies specified should be 
            # within the permissible range. The sweep commands 
            # apply both to input and output modes        
            # usage: 
            # sweep [(start|stop|center|span|cw {frequency}) | 
            #   ({start(Hz)} {stop(Hz)} [0..290])]
            # # example return:  
        if (startVal==None) or (stopVal==None):
            self.print_message("ERROR: sweep start and stop need non-empty values")
            msgbytes = self.error_byte_return()
        elif (int(startVal) >= int(stopVal)):
            self.print_message("ERROR: sweep start must be less than sweep stop value")
            msgbytes = self.error_byte_return()
        else:
            #do stuff, error checking needed
            self.print_message("sweeping...")
            writebyte = 'sweep '+str(startVal)+' '+str(stopVal)+' '+str(pts)+'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False)

        return msgbytes 

    def sweep_time(self, val):
        # sets the sweeptime
        # usage: sweep {time(Seconds)}the time
        # specified may end in a letter where
        # m=mili and u=micro
        # example return:  b''
        
        
        # needs some error checking

        writebyte = 'sweeptime '+str(val)+'\r\n'
        msgbytes = self.tinySA_serial(writebyte, printBool=False)   
        self.print_message("sweeptime set to " + str(val))
        return msgbytes

    def trigger(self, val, freq=None):
        # sets the trigger type or level
        # usage: trigger auto|normal|single|{level(dBm)}
        # the trigger level is always set in dBm and is the only numerical input
        # example return:  
        # #explicitly allowed vals
        accepted_vals =  ["auto", "normal", "single"]        

        if str(val) in accepted_vals:
            writebyte = 'trigger ' + str(val) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("setting trigger to " + str(val))
        elif val==None and isinstance(freq,int):
            writebyte = 'trigger ' + str(freq) +'\r\n'
            msgbytes = self.tinySA_serial(writebyte, printBool=False) 
            self.print_message("setting trigger level (dBm) to " + str(freq))
        else:
            self.print_message("ERROR: trigger takes inputs auto|normal|single|{level(dBm)}")
            msgbytes = self.error_byte_return()
        return msgbytes

    def trigger_auto(self):
        # alias for trigger
        return self.trigger("auto")

    def trigger_normal(self):
        # alias for trigger
        return self.trigger("normal")    

    def trigger_single(self):
        # alias for trigger
        return self.trigger("single")

    def trigger_level(self, val):
        # alias for trigger
        return self.trigger(None, val)