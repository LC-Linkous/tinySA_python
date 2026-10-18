#! /usr/bin/python3
"""
bench_generator.py -- one-sitting generator check with a receiver (HackRF One or any SDR).

The tinySA firmware cannot report its own output level, frequency or modulation,
so the only proof the generator works is a receiver. This script walks through a
fixed sequence of generator states, holds each one until you press Enter, and
records what you measured. Everything (commands sent, device replies, your
readings) goes to one JSON Lines file via the library's own log plus a 'bench'
record per step, so the session is reproducible and the numbers are kept.

SETUP (do this before running):
  tinySA RF port -> attenuator (30 dB recommended) -> HackRF One input.
  Measure the attenuator + cable loss with the VNA first (S21 at 10, 100, 300 MHz)
  and pass it with --path-loss so expected levels are printed.
  HackRF One: input must stay below about -5 dBm; with 30 dB in line the tinySA's
  top level (-6 dBm) arrives near -36 dBm. Keep the HackRF gains fixed for the
  whole session so relative levels are comparable.

RUN:
  uv run python tests/bench_generator.py --path-loss 31.2 --out bench_results/ultra_v1.4-244

Each step prints what the device was told and what you should see. Type the
reading (dBm, or Hz, or a note) and press Enter; type 's' to skip a step or 'q'
to stop. The output is switched OFF between sections and at the end, including
on Ctrl-C.
"""

import argparse
import datetime
import json
import os
import sys

from tsapython import tinySA

LEVEL_MIN = -76


def main():
    parser = argparse.ArgumentParser(description="Generator check with a receiver.")
    parser.add_argument("--port")
    parser.add_argument("--path-loss", type=float, default=None,
                        help="attenuator + cable loss in dB, from the VNA; used only to print expected levels")
    parser.add_argument("--out", default=None)
    parser.add_argument("--freqs", default="1e6,10e6,100e6,300e6", help="CW frequencies in Hz")
    parser.add_argument("--levels", default="-76,-60,-40,-30.5,-20,-10,-6", help="levels in dBm")
    parser.add_argument("--yes", action="store_true", help="skip the confirmation prompt")
    args = parser.parse_args()

    if not args.yes:
        print("This switches the tinySA RF OUTPUT ON. Confirm an attenuator or load is on the RF port")
        print("and the receiver input will stay within its limits.")
        if input("Type ON to continue: ").strip() != "ON":
            sys.exit("stopped")

    tsa = tinySA()
    tsa.set_error_byte_return(True)
    tsa.set_verbose(True)
    connected = tsa.connect(args.port) if args.port else tsa.autoconnect()[1]
    if not connected:
        sys.exit("ERROR: could not connect to a tinySA")

    started = datetime.datetime.now().isoformat(timespec="seconds")
    out_dir = args.out or os.path.join("bench_results", started.replace(":", "-"))
    os.makedirs(out_dir, exist_ok=True)
    log_path = os.path.join(out_dir, "bench.jsonl")
    tsa.set_log_file(log_path, level="commands")
    bench_log = open(os.path.join(out_dir, "readings.jsonl"), "a", encoding="utf-8")

    def record(step, expect, reading, note=""):
        rec = {"t": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="milliseconds"),
               "step": step, "expected": expect, "reading": reading, "note": note}
        bench_log.write(json.dumps(rec) + "\n")
        bench_log.flush()

    def ask(step, expect):
        line = "  [%s]  expect: %s\n  reading (Enter=next, s=skip, q=quit): " % (step, expect)
        answer = input(line).strip()
        if answer.lower() == "q":
            raise KeyboardInterrupt
        record(step, expect, None if answer.lower() in ("", "s") else answer)

    def expected_dbm(level):
        if args.path_loss is None:
            return "%g dBm at the tinySA port" % level
        return "%g dBm at the tinySA port, about %g dBm at the receiver" % (level, level - args.path_loss)

    freqs = [float(f) for f in args.freqs.split(",")]
    levels = [float(v) for v in args.levels.split(",")]
    profile = tsa.profile
    print("\nDevice: %s, firmware build %s, profile verified from %s" % (profile.name, tsa.firmwareBuild, profile.verified))
    print("Readings and the command log go to %s\n" % out_dir)

    try:
        tsa.set_output_allowed(True)

        # 1. output setting and on/off
        print("== 1. output on/off")
        tsa.set_output_allowed(False)
        refused = tsa.output("on") == bytearray(b"ERROR")
        record("gate", "output on refused while setting is off", "refused" if refused else "SENT")
        tsa.set_output_allowed(True)
        assert tsa.setup_generator(10e6, LEVEL_MIN) is True, "setup_generator failed"
        ask("output off (after setup)", "no carrier at 10 MHz")
        tsa.output("on")
        ask("output on, 10 MHz, %g dBm" % LEVEL_MIN, "carrier at 10 MHz, " + expected_dbm(LEVEL_MIN))
        tsa.output("off")
        ask("output off", "carrier gone")

        # 2. frequency
        print("== 2. frequency")
        tsa.output("on")
        for f in freqs:
            tsa.set_generator(freq_hz=f)
            ask("cw %g Hz" % f, "carrier at %g MHz" % (f / 1e6))
        tsa.set_generator(freq_hz=10e6)
        tsa.output("off")

        # 3. level steps
        print("== 3. level steps at 10 MHz (gains fixed)")
        tsa.output("on")
        for v in levels:
            tsa.set_generator(level_dbm=v)
            ask("level %g" % v, expected_dbm(v))
        tsa.pause(); tsa.command("level 10"); tsa.resume()   # out of range on purpose (bypasses the library check)
        ask("level 10 (out of range)", "same as the maximum level, the device clamps")
        tsa.set_generator(level_dbm=LEVEL_MIN)
        tsa.output("off")

        # 4. modulation
        print("== 4. modulation at 10 MHz, -30 dBm")
        tsa.set_generator(level_dbm=-30)
        tsa.output("on")
        tsa.set_generator(modulation_type="am", modulation_rate_hz=1000)
        ask("am, 1 kHz", "sidebands at +-1 kHz / 1 kHz envelope")
        if "fm" in profile.modulation_words:
            tsa.set_generator(depth_percent=30)
            ask("am depth 30 %", "sidebands lower than at the default depth")
            tsa.set_generator(modulation_type="fm", deviation_hz=3000)
            ask("fm, 1 kHz rate, 3 kHz deviation", "FM spectrum, demodulated 1 kHz tone")
        else:
            tsa.set_generator(modulation_type="nfm")
            ask("nfm, 1 kHz", "narrow FM, demodulated 1 kHz tone")
            tsa.set_generator(modulation_type="wfm")
            ask("wfm, 1 kHz", "wide FM")
        tsa.set_generator(modulation_type="off")
        ask("modulation off", "clean carrier")
        tsa.output("off")

        # 5. output path (Ultra family)
        if "mixer" in profile.output_words:
            print("== 5. output path")
            tsa.output("on")
            tsa.output("normal")
            ask("output normal", "carrier present")
            tsa.output("mixer")
            ask("output mixer", "carrier present")
            tsa.output("off")

        # 6. mode change mutes
        print("== 6. mode change")
        tsa.output("on")
        ask("output on", "carrier present")
        tsa.mode("low", "input")
        ask("mode low input", "carrier gone (firmware mutes on a mode change)")
        tsa.mode("low", "output")
        ask("mode low output", "still no carrier; level has reset to the maximum")

        # 7. level sweep
        print("== 7. level sweep")
        tsa.pause()
        tsa.set_sweep_start(int(10e6)); tsa.set_sweep_stop(int(11e6)); tsa.sweep_time(2)
        tsa.level(-40); tsa.level_change(20)
        tsa.resume()
        tsa.output("on")
        ask("levelchange 20 over a 2 s sweep", "level rises 20 dB across each sweep")
        tsa.pause(); tsa.level_change(0); tsa.resume()
        tsa.output("off")

        # 8. caloutput
        print("== 8. calibration output")
        tsa.mode("low", "input")
        tsa.cal_output(30)
        ask("caloutput 30", "30 MHz reference and its harmonics")
        tsa.cal_output("off")
        ask("caloutput off", "gone")
        print("\nDone.")
    except KeyboardInterrupt:
        print("\nstopped by user")
    finally:
        try:
            tsa.output("off")
            tsa.modulation("off")
            tsa.level_change(0)
            tsa.cal_output("off")
            tsa.mode("low", "input")
        finally:
            tsa.close_log_file()
            bench_log.close()
            try:
                tsa.disconnect()
            except Exception as err:
                print("note: disconnect raised", err)
    print("readings: %s" % os.path.join(out_dir, "readings.jsonl"))
    print("commands: %s" % log_path)


if __name__ == "__main__":
    main()
