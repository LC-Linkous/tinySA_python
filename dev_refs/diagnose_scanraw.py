#! /usr/bin/python3
"""
diagnose_scanraw.py -- v2: drains the full frame AND reports where 0x3e ('>')
and 0x7d ('}') bytes fall inside the binary payload. This shows exactly why the
default get_serial_return (which stops at the first '>') truncates large frames.

Run from tsapython/ with the device connected:  python diagnose_scanraw.py
"""
import sys, os, time
HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (os.path.join(HERE, "src"), os.path.join(HERE, "..", "..", "src"), HERE):
    if os.path.isdir(os.path.join(cand, "tsapython")):
        sys.path.insert(0, cand); break
from tsapython import tinySA

def drain(ser, cmd, window=4.0):
    ser.reset_input_buffer(); ser.reset_output_buffer()
    ser.write(cmd.encode())
    chunks=[]; deadline=time.time()+window; last=time.time()
    while time.time() < deadline:
        n=ser.in_waiting
        if n:
            chunks.append(ser.read(n)); last=time.time()
        else:
            if chunks and (time.time()-last) > 1.0: break
            time.sleep(0.02)
    return b"".join(chunks)

def report(raw, pts):
    fs=raw.find(b'{'); fe=raw.rfind(b'}')
    frame=raw[fs:fe+1] if (fs!=-1 and fe!=-1 and fe>fs) else None
    print(f"  requested {pts}: raw={len(raw)}B", end="")
    if not frame:
        print(" -- NO COMPLETE FRAME"); return
    payload=frame[1:-1]
    print(f"  frame={len(frame)}B payload={len(payload)}B (~{len(payload)//3} pts)")
    # where does the FIRST 0x3e fall? that's where get_serial_return would stop.
    pos3e=[i for i,b in enumerate(frame) if b==0x3e]
    pos7d=[i for i,b in enumerate(payload) if b==0x7d]
    first3e = pos3e[0] if pos3e else None
    print(f"     0x3e ('>') count in frame: {len(pos3e)}; FIRST at index {first3e}"
          + (f"  <-- get_serial_return truncates here ({first3e+1}B)" if first3e is not None else "  (none -> would NOT truncate)"))
    print(f"     0x7d ('}}') count inside payload: {len(pos7d)}")

def main():
    tsa=tinySA(); tsa.set_verbose(True)
    found, connected = tsa.autoconnect()
    if not connected:
        print("Could not connect."); sys.exit(1)
    ser=tsa.ser
    start, stop = 150_000_000, 500_000_000
    for pts in [200, 450]:
        print(f"\n=== scanraw {pts} pts (2 runs) ===")
        for _ in range(2):
            report(drain(ser, f"scanraw {start} {stop} {pts} 1\r\n"), pts)
    tsa.disconnect()
    print("\nIf 200-pt frames have NO early 0x3e but 450-pt do, that's why small worked.")
    print("If BOTH have early 0x3e, then timing (not byte content) explains 200 working.")

if __name__ == "__main__":
    main()