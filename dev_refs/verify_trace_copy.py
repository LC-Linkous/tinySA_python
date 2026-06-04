#! /usr/bin/python3
"""
verify_trace_copy.py -- round 4. Traces are 1-INDEXED. Retest the spaced
grammar with valid trace numbers (1,2,3). Low-risk, hard timeout.
Run from tsapython/ with device connected:  python verify_trace_copy.py
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (os.path.join(HERE, "src"), os.path.join(HERE, "..", "..", "src"), HERE):
    if os.path.isdir(os.path.join(cand, "tsapython")):
        sys.path.insert(0, cand); break
from tsapython import tinySA

def send_and_read(ser, cmd, settle=0.4, window=2.0):
    ser.reset_input_buffer(); ser.reset_output_buffer()
    ser.write(cmd.encode()); time.sleep(settle)
    chunks=[]; deadline=time.time()+window
    while time.time()<deadline:
        n=ser.in_waiting
        if n:
            chunks.append(ser.read(n))
            if b"ch>" in b"".join(chunks): break
        else: time.sleep(0.05)
    return b"".join(chunks)

def main():
    tsa=tinySA(); tsa.set_verbose(True)
    found, connected = tsa.autoconnect()
    if not connected:
        print("Could not connect."); sys.exit(1)
    ser=tsa.ser
    probes=[
        "trace 1 copy 2\r\n",       # spaced copy, valid 1-based #s
        "trace 1 subtract 2\r\n",   # spaced subtract
        "trace 1 view on\r\n",      # toggle on
        "trace 1 view off\r\n",     # toggle off
        "trace 1 freeze\r\n",       # freeze
        "trace 1 value\r\n",        # value query
        "trace 1 scale auto\r\n",   # scale with trace#
        "trace 1 dBm\r\n",          # units with trace#
    ]
    for cmd in probes:
        raw=send_and_read(ser,cmd)
        print("\n"+"="*60)
        print(f"SENT: {cmd!r}")
        print(f"RECV ({len(raw)}B): {raw!r}")
    tsa.disconnect()
    print("\nclean echo + 'ch>' = accepted;  usage string = rejected.")

if __name__=="__main__":
    main()