#! /usr/bin/python3
"""
diagnose_reset.py -- learn what reset() actually does on real hardware.

reset() disconnects the serial immediately, so the read path (get_serial_return)
may return partial data, raise a SerialException, or HANG forever (its read loop
has no timeout). This probe runs reset() in a worker thread with a hard wall-clock
timeout so it cannot lock up your session, and reports which of the three happened.

WARNING: this WILL reset your tinySA (it reboots). Read-only otherwise.

Run from tsapython/ with the device connected:  python diagnose_reset.py
"""
import sys, os, time, threading
HERE = os.path.dirname(os.path.abspath(__file__))
for cand in (os.path.join(HERE, "src"), os.path.join(HERE, "..", "..", "src"), HERE):
    if os.path.isdir(os.path.join(cand, "tsapython")):
        sys.path.insert(0, cand); break
from tsapython import tinySA

result = {"status": "running", "value": None, "error": None}

def call_reset(tsa):
    try:
        r = tsa.reset()
        result["status"] = "returned"
        result["value"] = r
    except Exception as e:
        result["status"] = "raised"
        result["error"] = f"{type(e).__name__}: {e}"

def main():
    tsa = tinySA()
    tsa.set_verbose(True)
    found, connected = tsa.autoconnect()
    if not connected:
        print("Could not connect."); sys.exit(1)

    print("\nCalling reset() with a 5s hard timeout...")
    print("(the device will reboot)\n")

    t = threading.Thread(target=call_reset, args=(tsa,), daemon=True)
    t.start()
    t.join(timeout=5.0)

    if t.is_alive():
        print("RESULT: reset() HUNG -- did not return or raise within 5s.")
        print("  -> get_serial_return is stuck waiting on the disconnected port.")
        print("  -> clear_and_reset MUST NOT depend on reset()'s return (would hang).")
    elif result["status"] == "returned":
        print(f"RESULT: reset() RETURNED: {result['value']!r}")
    elif result["status"] == "raised":
        print(f"RESULT: reset() RAISED: {result['error']}")
        print("  -> clear_and_reset catches this (it now does).")

    print("\nNOTE: the device has reset. Reconnect for further use.")
    print("If the port is now locked, unplug/replug the tinySA.")

if __name__ == "__main__":
    main()