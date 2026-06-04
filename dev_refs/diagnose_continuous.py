#! /usr/bin/python3
"""
diagnose_continuous.py -- v2. Mode 2 returned a SINGLE frame + ch> (not an
open stream). So test the likely real pattern for continuous scanning:
  (A) call scan_raw() in a LOOP (known-length mode) -- does each return clean?
  (B) does mode 3 (unbuffered+continuous) behave differently from mode 2?
  (C) raw: send 'scanraw ... 3' and drain 2.5s -- multiple frames or just one?

Run from tsapython/ with the device connected:  python diagnose_continuous.py
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (os.path.join(HERE, "src"), os.path.join(HERE, "..", "..", "src"), HERE):
    if os.path.isdir(os.path.join(cand, "tsapython")):
        sys.path.insert(0, cand); break
from tsapython import tinySA

def drain(ser, seconds):
    chunks=[]; deadline=time.time()+seconds
    while time.time() < deadline:
        n=ser.in_waiting
        if n: chunks.append(ser.read(n))
        else: time.sleep(0.02)
    return b"".join(chunks)

def main():
    tsa=tinySA(); tsa.set_verbose(False)   # quiet; we print our own
    found, connected = tsa.autoconnect()
    if not connected:
        print("Could not connect."); sys.exit(1)
    ser=tsa.ser
    start, stop, pts = 150_000_000, 200_000_000, 15

    # (A) loop scan_raw() via the library (known-length get_binary_return)
    print("=== (A) scan_raw() called 5x in a loop (mode 1, known-length) ===")
    for i in range(5):
        t0=time.time()
        data = tsa.scan_raw(start, stop, pts, 1)
        dt=(time.time()-t0)*1000
        ok = len(data) == 1 + 3*pts   # '{' + 3*pts, trailing '}' dropped
        print(f"  iter {i+1}: {len(data)}B  expected {1+3*pts}B  ok={ok}  ({dt:.0f} ms)")

    # (B)+(C) raw drain of mode 3 to see if it streams differently
    print("\n=== (C) raw 'scanraw ... 3' (unbuffered+continuous), drain 2.5s ===")
    ser.reset_input_buffer(); ser.reset_output_buffer()
    ser.write(f"scanraw {start} {stop} {pts} 3\r\n".encode())
    raw = drain(ser, 2.5)
    print(f"  total {len(raw)}B  '{{'={raw.count(b'{')}  '}}'={raw.count(b'}')}  'ch>'={raw.count(b'ch>')}")
    print(f"  head: {raw[:40]!r}")
    print(f"  tail: {raw[-24:]!r}")
    # stop if needed
    ser.write(b"pause\r\n"); drain(ser, 0.4)
    ser.write(b"resume\r\n"); drain(ser, 0.4)

    tsa.disconnect()
    print("\nIf (A) shows 5 clean frames -> continuous scanning = loop scan_raw().")
    print("If (C) shows many '{' -> mode 3 DOES open-stream and needs a streaming reader.")

if __name__ == "__main__":
    main()