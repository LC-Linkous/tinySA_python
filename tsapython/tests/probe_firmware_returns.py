#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tests/probe_firmware_returns.py  --  hardware probe, run by hand
#
#   Written from reading the tinySA firmware source (commit 650f538, v1.4-244) and tsapython
#   3.0.1. First run on hardware 2026-10-17 (tinySA Ultra ZS405, tinySA4_v1.4-143): every
#   firmware prediction it could test came out as predicted.
#
#   Devices: tinySA Basic (ZS304), Ultra (ZS405), Ultra+ (ZS406, ZS407). Predictions exist
#   for the Basic and for the Ultra family; the three Ultra boards share one command set.
#   The Basic predictions come from the shared source only and are the least certain.
#
#   What it does
#       Asks a connected tinySA what its firmware actually accepts, and records what the
#       tsapython library does with the same requests. The output is a JSON file and a
#       markdown table that can be pasted into firmware_command_tracker.md.
#
#       1. identity      version, info, help (the list of commands this unit has)
#       2. usage         sends each command in a query form so the device prints its own
#                        usage line: the firmware's statement of what it accepts
#       3. accept        sends specific old/new argument forms and classifies the reply
#       4. library       calls tsapython functions and records whether the library blocked
#                        the call, sent it, or raised
#       B. backup        (--backup) read-only dump of calibration and config values, to keep
#                        before a firmware update (an update can reset stored config)
#       5. capture       (--capture) compares capture() with a read-by-length of the screen
#       6. generator     (--generator) signal generator command forms, OUTPUT MUTED THROUGHOUT
#
#   Safety
#       * No command here writes calibration or config (no clearconfig, saveconfig, save,
#         leveloffset/correction/dac/zero setters, deviceid setter, touchcal, selftest, reset).
#       * No SD card command that takes a filename is sent.
#       * The generator section never sends "output on". The firmware mutes the output on
#         every mode change, and the script sends "output off" again straight after.
#         Still: disconnect anything sensitive from the RF port before using --generator.
#       * The script changes sweep settings while it runs. At the end it sends "load 0"
#         (reload the startup preset) and "resume". Use --no-restore to skip that.
#       * tsapython's serial read has no timeout, so every call runs under a watchdog here.
#         If one hangs, the run stops, the reports are still written, and the device needs
#         a replug before the next run.
#
#   Usage
#       python probe_firmware_returns.py                      # sections 1-4
#       python probe_firmware_returns.py --port COM7 --capture
#       python probe_firmware_returns.py --generator          # adds section 6
#       python probe_firmware_returns.py --only backup        # before a firmware update
#       python probe_firmware_returns.py --only usage         # one section
##--------------------------------------------------------------------------------------------------\

import argparse
import datetime
import json
import os
import re
import sys
import threading
import time

from importlib.metadata import PackageNotFoundError, version as package_version

from tsapython import tinySA

# The 'library' predictions (L.. and G30..G41) describe tsapython 3.0.1, the release this
# script was written against. On any other version a difference is reported as
# 'changed since 3.0.1' instead of DIFFERENT: it shows what a later version fixed.
PREDICTED_FOR = "3.0.1"
try:
    LIBRARY_VERSION = package_version("tsapython")   # __version__ is stale in 3.0.1
except PackageNotFoundError:
    LIBRARY_VERSION = "unknown"
# An editable install of a development branch may still report an older version, so
# also detect by features the later versions added.
if LIBRARY_VERSION == PREDICTED_FOR and hasattr(tinySA, "set_log_file"):
    LIBRARY_VERSION = PREDICTED_FOR + "+dev"
LIBRARY_V4 = hasattr(tinySA, "set_output_allowed")

SECTIONS = ["identity", "backup", "usage", "accept", "library", "capture", "generator"]

# reply classes
TIMEOUT = "timeout"            # no prompt came back inside the watchdog time
READ_FAILED = "read-failed"    # library returned None
EMPTY = "empty"                # prompt only: accepted, OR silently ignored
USAGE = "usage"                # device printed a usage line: argument rejected
UNKNOWN = "unknown-command"    # device printed 'name?': command not in this firmware
DATA = "data"                  # any other text
BLOCKED = "blocked-by-library" # library returned its error value and sent nothing
RAISED = "python-exception"    # library raised before or while sending
REFUSED = "device-refused"     # 'usb disk mode active', 'Command timeout', range errors

# the same outcomes in the words the tsapython log file uses
LOG_STATUS = {"device-rejected": "usage", EMPTY: "ok", DATA: "ok", USAGE: "usage", UNKNOWN: "unknown-command",
              REFUSED: "device-refused", TIMEOUT: "timeout", READ_FAILED: "read-failed",
              BLOCKED: "blocked", RAISED: "python-exception"}

DEVICE_REFUSALS = (
    "usb disk mode active",
    "Command timeout",
    "frequency range is invalid",
    "sweep points exceeds range",
    "scan point count is invalid",
    "sweep point count is invalid",
    "Key unmatched",
)


class ProbeAbort(Exception):
    pass


def classify(command, reply):
    """Turn a cleaned tsapython reply into one of the classes above."""
    if reply is None:
        return READ_FAILED
    text = bytes(reply).decode("utf-8", errors="replace").strip()
    if text == "":
        return EMPTY
    name = command.strip().split(" ")[0]
    if text == name + "?":
        return UNKNOWN
    if "usage:" in text:
        return USAGE
    # a few commands print their usage without the 'usage:' prefix
    if re.match(r"^(save|recall) \{id\}$", text) or text.startswith("trigger {value}") \
            or text.startswith("trace {") or text.startswith("marker [n]") \
            or text.startswith("channel [1-3]") or text.startswith("leveloffset ["):
        return USAGE
    for refusal in DEVICE_REFUSALS:
        if refusal in text:
            return REFUSED
    return DATA


class Prober:
    def __init__(self, tsa, timeout):
        self.tsa = tsa
        self.timeout = timeout
        self.records = []
        self.sent_log = []      # every string the library wrote to the port
        self.dead = False
        self.family = "unknown"
        self.board = "unknown"
        self.hw_version = ""
        self.build = None       # (major, minor, commits since tag) from the version reply
        self.commands = set()   # from the device's help reply

        # record exactly what the library writes, without changing the library
        original = tsa.tinySA_serial

        def recording_serial(writebyte, *args, **kwargs):
            self.sent_log.append(writebyte)
            return original(writebyte, *args, **kwargs)

        tsa.tinySA_serial = recording_serial

    # ---- watchdog -------------------------------------------------------------------

    def _guarded(self, func, timeout=None):
        """Run func in a thread. Returns (finished, result, exception)."""
        if self.dead:
            raise ProbeAbort("an earlier call timed out; serial state is unknown")
        box = {}

        def runner():
            try:
                box["result"] = func()
            except Exception as err:  # recorded, not swallowed
                box["error"] = err

        thread = threading.Thread(target=runner, daemon=True)
        thread.start()
        thread.join(timeout or self.timeout)
        if thread.is_alive():
            self.dead = True
            return False, None, None
        return True, box.get("result"), box.get("error")

    # ---- one probe ------------------------------------------------------------------

    def raw(self, section, pid, command, expect=None, note="", timeout=None):
        """Send a raw command string through tsapython's command()."""
        finished, reply, error = self._guarded(lambda: self.tsa.command(command), timeout)
        if not finished:
            observed = TIMEOUT
        elif error is not None:
            observed = RAISED
        else:
            observed = classify(command, reply)
        record = self._record(section, pid, "raw", command, command, expect, observed,
                              reply, error, note)
        if not finished:
            raise ProbeAbort("no reply to %r within %s s" % (command, timeout or self.timeout))
        time.sleep(0.05)
        return record

    def lib(self, section, pid, label, func, expect=None, note="", timeout=None, cleanup=None):
        """Call a tsapython function and record what it sent and returned.
        cleanup is sent only if the device accepted something."""
        mark = len(self.sent_log)
        finished, reply, error = self._guarded(func, timeout)
        sent = self.sent_log[mark:]
        wire = " | ".join(s.strip() for s in sent)
        if not finished:
            observed = TIMEOUT
        elif error is not None:
            observed = RAISED
        elif not sent:
            observed = BLOCKED
        elif LIBRARY_V4 and reply is not None and bytes(reply) in (b"ERROR", b""):
            # 4.0.0 returns the error value for a device rejection; the raw reply is
            # in the library log, not here. Report what the device did from the
            # command classification of a bare 'empty' as accepted.
            observed = "device-rejected" if bytes(reply) == b"ERROR" else EMPTY
        else:
            observed = classify(sent[-1], reply)
        record = self._record(section, pid, "library", label, wire, expect, observed,
                              reply, error, note,
                              changed_label=(LIBRARY_VERSION != PREDICTED_FOR))
        if not finished:
            raise ProbeAbort("no reply to %s within %s s" % (label, timeout or self.timeout))
        time.sleep(0.05)
        if cleanup and observed in (EMPTY, DATA):
            self.quiet(cleanup)
        return record

    def _record(self, section, pid, kind, call, wire, expect, observed, reply, error, note,
                changed_label=False):
        # expect may be a class, a tuple of classes, or a dict keyed by family
        if isinstance(expect, dict):
            expect = expect.get(self.family)
        if expect is None:
            verdict = "info"
        else:
            allowed = expect if isinstance(expect, (tuple, list)) else (expect,)
            verdict = "as predicted" if observed in allowed else (
                "changed since " + PREDICTED_FOR if changed_label else "DIFFERENT")
            expect = "/".join(allowed)
        text = "" if reply is None else bytes(reply).decode("utf-8", errors="replace")
        record = {
            "section": section, "id": pid, "kind": kind, "call": call, "sent": wire,
            "expected": expect, "observed": observed, "verdict": verdict,
            # 'status' and 'reply_len' use the vocabulary of the tsapython log file
            # (README section "Logging"), so both can be read by the same code
            "status": LOG_STATUS.get(observed, observed),
            "reply": text, "reply_len": 0 if reply is None else len(reply),
            "error": repr(error) if error else "", "note": note,
        }
        self.records.append(record)
        flag = {"as predicted": " ", "DIFFERENT": "!", "info": "."}.get(verdict, "~")
        print("%s %-4s %-44s %-20s %s" % (flag, pid, call[:44], observed,
                                          text.strip().replace("\r\n", " / ")[:60]))
        return record

    def quiet(self, command):
        """Cleanup command: sent, not recorded as a probe. Never raises on a dead port."""
        if self.dead:
            return None
        finished, reply, _ = self._guarded(lambda: self.tsa.command(command))
        time.sleep(0.05)
        return reply if finished else None


# =====================================================================================
# 1. identity
# =====================================================================================

# HW Version text printed by the Ultra family's 'version' reply. The exact strings
# changed between firmware builds (V0.5.2, V0.5.3, V0.5.3.2, V0.5.4 are all the ZS407),
# so match on the prefix.
ULTRA_BOARD_PREFIXES = [
    ("V0.4.5", "Ultra ZS405"),
    ("V0.4.6", "Ultra+ ZS406"),
    ("V0.5.", "Ultra+ ZS407"),
]


def board_name(family, hw_version, info_first_line):
    if family == "basic":
        return "Basic ZS304"
    for prefix, name in ULTRA_BOARD_PREFIXES:
        if hw_version.startswith(prefix):
            return name
    # firmware from v1.4-190 on also names the board on the first info line
    found = re.search(r"ZS40[567]", info_first_line)
    if found:
        return ("Ultra+ " if "+" in info_first_line else "Ultra ") + found.group(0)
    return "Ultra family, board not recognised (HW Version %r)" % hw_version


def firmware_build(version_reply):
    """'tinySA4_v1.4-143-g864bb27' -> (1, 4, 143). None for self-built or unknown strings."""
    found = re.search(r"_v(\d+)\.(\d+)-(\d+)-g[0-9a-f]+", version_reply)
    return tuple(int(x) for x in found.groups()) if found else None


def section_identity(p):
    r = p.raw("identity", "I01", "version")
    version = r["reply"].strip()
    # Basic firmware is built as 'tinySA_...', the Ultra family as 'tinySA4_...'
    p.family = "ultra" if version.startswith("tinySA4") else "basic"
    hw = re.search(r"HW Version:\s*(\S+)", version)
    p.hw_version = hw.group(1) if hw else ""
    p.build = firmware_build(version)

    r = p.raw("identity", "I02", "info")
    if "tinySA" not in r["reply"]:
        # the NanoVNA shares this USB ID; do not send tinySA commands to it
        raise ProbeAbort("info reply does not name a tinySA: %r" % r["reply"][:60])

    first_line = r["reply"].strip().split("\r\n")[0]
    p.board = board_name(p.family, p.hw_version, first_line)

    r = p.raw("identity", "I03", "help")
    words = re.sub(r"(Other )?commands:", " ", r["reply"]).split()
    p.commands = set(words)

    p.raw("identity", "I04", "deviceid", expect=DATA)
    p.raw("identity", "I05", "status", expect=DATA)
    p.raw("identity", "I06", "vbat", expect=DATA)
    print("  family: %s, board: %s, firmware build: %s, %d commands listed by help" % (
        p.family, p.board, p.build, len(p.commands)))


# =====================================================================================
# B. backup: read-only dump of what a firmware update may reset
#    The firmware discards stored config and presets when its config layout version
#    changes, and that version changed several times between v1.4-143 and v1.4-244.
#    Nothing here writes to the device. The full replies are in probe_results.json.
# =====================================================================================

CORRECTION_TABLES = {
    "ultra": ["low", "lna", "ultra", "ultra_lna", "direct", "direct_lna", "harm", "harm_lna",
              "out", "out_direct", "out_adf", "out_ultra"],
    "basic": ["low", "high", "out"],
}


def section_backup(p):
    s = "backup"
    queries = ["leveloffset", "dac ?", "vbat_offset ?", "deviceid", "color", "sweep", "trace",
               "marker", "zero ?"]
    if p.family == "ultra":
        queries += ["actual_freq ?", "freq_corr ?", "if1 ?", "nf ?", "ultra ?", "direct ?"]
    else:
        queries += ["actual_freq ?"]
    queries += ["correction " + table for table in CORRECTION_TABLES.get(p.family, [])]
    for i, query in enumerate(queries, start=1):
        p.raw(s, "B%02d" % i, query)
    print("  Touch calibration values have no read-only query; note them from the device")
    print("  if you rely on them. Keep probe_results.json with the unit's records.")


# =====================================================================================
# 2. usage harvest
#    Each entry is a query form that prints usage or the current value and changes
#    nothing. Forms were chosen per command from the firmware source; do not replace
#    them with a blanket '?' (for example 'repeat ?' and 'levelchange ?' SET a value,
#    and 'sd_delete ?' could match single-character file names).
# =====================================================================================

USAGE_QUERIES = [
    # generator and mode
    "mode ?", "modulation ?", "output ?", "level ?", "levelchange", "caloutput",
    # measurement settings
    "calc ?", "rbw ?", "attenuate ?", "sweeptime ?", "spur ?", "lna ?", "lna2 ?", "agc ?",
    "avoid ?", "ext_gain ?", "trigger ?", "line ?", "if ?", "if1 ?", "ultra ?", "direct ?",
    # sweep, traces, markers, data
    "sweep", "sweep ?", "trace", "trace ?", "marker", "marker ?", "data ?", "scanraw",
    "hop", "channel", "channel ?", "wait ?", "waitscan ?", "abort ?",
    # presets (query forms only; nothing is saved or loaded here)
    "load ?", "save ?", "recall ?",
    # read-only calibration and system values
    "zero ?", "nf ?", "dac ?", "actual_freq ?", "freq_corr ?", "vbat_offset ?",
    "leveloffset", "leveloffset ?", "correction ?", "correction low", "selftest ?",
    "freq ?", "time ?", "usart_cfg ?", "color", "refresh", "usbdisk", "sweep_voltage ?",
    "sd_list", "k",
]


def section_usage(p):
    for i, query in enumerate(USAGE_QUERIES, start=1):
        p.raw("usage", "U%02d" % i, query)


# =====================================================================================
# 3. acceptance probes (input mode, no RF output involved)
# =====================================================================================

def section_accept(p):
    s = "accept"
    ULTRA_ONLY = {"ultra": EMPTY, "basic": USAGE}    # accepted on the Ultra family only
    BASIC_ONLY = {"ultra": USAGE, "basic": EMPTY}    # accepted on the Basic only

    # calc: library sends 'quasip'; firmware renamed it 'quasi' on 2022-05-25
    p.raw(s, "A01", "calc quasip", expect=USAGE, note="library keyword")
    p.raw(s, "A02", "calc quasi", expect=EMPTY, note="firmware keyword")
    p.raw(s, "A03", "calc ?", note="readback: should show QUASI")
    p.raw(s, "A04", "calc aver", expect=EMPTY, note="not offered by library")
    p.quiet("calc off")

    # mode: the Ultra has no 'high'
    p.raw(s, "A05", "mode high input", expect=BASIC_ONLY, note="library set_high_input_mode()")
    p.raw(s, "A06", "mode low input", expect=EMPTY)
    p.raw(s, "A07", "mode input", expect=ULTRA_ONLY, note="Ultra short form, since 2022-10-04")

    # rbw: decimals are valid; library accepts integers only
    p.raw(s, "A08", "rbw 0.3", expect=EMPTY)
    p.raw(s, "A09", "rbw ?", note="readback after rbw 0.3")
    p.quiet("rbw auto")

    # attenuate: 31 is valid; library stops at 30
    p.raw(s, "A10", "attenuate 31", expect=EMPTY)
    p.raw(s, "A11", "attenuate ?", note="readback: should show 31")
    p.quiet("attenuate auto")

    # spur auto: Ultra only
    p.raw(s, "A12", "spur auto", expect=ULTRA_ONLY, note="already the Ultra default in input mode")

    # trace unit dBV: added 2026-08-12. Older firmware ignores it silently, so the
    # class is 'empty' either way; A14 is the real answer.
    p.raw(s, "A13", "trace dBV", expect=EMPTY)
    p.raw(s, "A14", "trace", note="readback: 'dBV' means accepted, 'dBm' means ignored")
    p.quiet("trace dBm")

    # markers 5-8 exist on the Ultra family; the Basic has 4
    p.raw(s, "A15", "marker 5 on", expect=ULTRA_ONLY)
    p.raw(s, "A16", "marker 5", expect={"ultra": DATA, "basic": USAGE}, note="readback of marker 5")
    p.quiet("marker 5 off")

    # trace sub-commands. The library forms are parsed and then ignored, so they
    # return 'empty' exactly like an accepted command. There is no serial readback
    # for freeze; watch the device screen for these four.
    p.raw(s, "A17", "trace 2 freeze", expect=EMPTY, note="MANUAL: library form, expect no effect")
    p.raw(s, "A18", "trace 2 freeze on", expect=EMPTY, note="MANUAL: firmware form")
    p.quiet("trace 2 freeze off")
    p.raw(s, "A19", "trace 2 clear", expect=EMPTY, note="MANUAL: library form, keyword removed 2021-07-05")
    p.raw(s, "A20", "trace 2 view on", expect=EMPTY, note="MANUAL: trace 2 should appear")
    p.quiet("trace 2 view off")

    # scan: zero span is valid, one point is not
    p.raw(s, "A21", "scan 100000000 100000000 20 3", expect=DATA,
          note="zero span. Before v1.4-230 a value of exactly -100 prints as -:.000000e+01")
    p.raw(s, "A22", "scan 100000000 200000000 1 3",
          note="1 point: refused from v1.4-228, returned data before that")
    p.raw(s, "A23", "scan 150e6 200e6 5 3", expect=DATA,
          note="e-notation: firmware reads 150 Hz and 200 Hz; check the frequency column")
    if "hop" in p.commands:
        p.raw(s, "A24", "hop 100000000 200000000 5 3", expect=DATA, note="outmask 3")
    if "waitscan" in p.commands:
        p.raw(s, "A25", "waitscan 1", expect=EMPTY, timeout=60)
    p.quiet("resume")


# =====================================================================================
# 4. library probes: what does tsapython do with the same requests?
# =====================================================================================

def section_library(p):
    s = "library"
    t = p.tsa
    t.set_error_byte_return(True)

    p.lib(s, "L01", "hop(100e6, 200e6, 5, 3)", lambda: t.hop(100e6, 200e6, 5, 3),
          expect=RAISED, note="outmask 3 leaves writebyte unassigned")
    p.lib(s, "L02", "wait()", lambda: t.wait(), expect=BLOCKED, note="default val=0")
    p.lib(s, "L03", "attenuate(31)", lambda: t.attenuate(31), expect=BLOCKED,
          cleanup="attenuate auto")
    p.lib(s, "L04", "rbw(0.3)", lambda: t.rbw(0.3), expect=BLOCKED, cleanup="rbw auto")
    p.lib(s, "L05", "calc('quasi')", lambda: t.calc("quasi"), expect=BLOCKED, cleanup="calc off")
    p.lib(s, "L06", "calc('quasip')", lambda: t.calc("quasip"), expect=USAGE, cleanup="calc off")
    p.lib(s, "L07", "mode('high', 'input')", lambda: t.mode("high", "input"),
          expect={"ultra": USAGE, "basic": EMPTY}, cleanup="mode low input")
    # a valid IF for this board: the library only knows the Basic's range
    if_value = {"Basic ZS304": 434000000, "Ultra ZS405": 977000000}.get(p.board, 1070000000)
    p.lib(s, "L08", "set_IF(%d)" % if_value, lambda: t.set_IF(if_value),
          expect={"ultra": BLOCKED, "basic": EMPTY}, cleanup="if 0",
          note="valid IF for %s" % p.board)
    p.lib(s, "L09", "trace_units(1, 'dBV')", lambda: t.trace_units(1, "dBV"), expect=BLOCKED,
          cleanup="trace dBm")
    p.lib(s, "L10", "spur('auto')", lambda: t.spur("auto"), expect=BLOCKED)
    p.lib(s, "L11", "scan(100e6, 100e6, 20, 3)", lambda: t.scan(100e6, 100e6, 20, 3),
          expect=BLOCKED, note="zero span")
    p.lib(s, "L12", "trace_freeze(2)", lambda: t.trace_freeze(2), expect=EMPTY,
          cleanup="trace 2 freeze off", note="MANUAL: sends 'trace 2 freeze' with no on|off")
    p.lib(s, "L13", "marker_on(5)", lambda: t.marker_on(5),
          expect={"ultra": EMPTY, "basic": USAGE},
          cleanup="marker 5 off")
    p.lib(s, "L14", "rbw()", lambda: t.rbw(), expect=EMPTY,
          note="no-argument call SETS auto; it is not a getter")
    p.quiet("resume")


# =====================================================================================
# 5. capture: text reader versus read-by-length
# =====================================================================================

def section_capture(p):
    s = "capture"
    t = p.tsa
    width, height = (480, 320) if p.family == "ultra" else (320, 240)
    expected = width * height * 2

    # not recorded through lib(): the reply is binary and only its length matters
    finished, reply, error = p._guarded(lambda: t.capture(), 60)
    if not finished or error is not None:
        raise ProbeAbort("capture() hung or raised: %r" % (error,))
    library_len = len(reply) if reply is not None else 0

    def read_by_length():
        ser = t.ser
        ser.reset_input_buffer()
        ser.write(b"capture\r\n")
        want = len(b"capture\r\n") + expected + len(b"ch> ")
        buf = b""
        last = time.time()
        while len(buf) < want and (time.time() - last) < 5.0:
            n = ser.in_waiting
            if n:
                buf += ser.read(n)
                last = time.time()
            else:
                time.sleep(0.01)
        return buf

    finished, buf, error = p._guarded(read_by_length, 90)
    if not finished or error is not None:
        raise ProbeAbort("direct capture read failed: %r" % (error,))
    start = buf.find(b"capture\r\n")
    payload = buf[start + 9:start + 9 + expected] if start != -1 else b""
    first_gt = payload.find(b">")
    result = {
        "expected_bytes": expected,
        "library_capture_len": library_len,
        "direct_payload_len": len(payload),
        "direct_tail": repr(buf[-6:]),
        "count_0x3E_in_payload": payload.count(b">"),
        "first_0x3E_offset": first_gt,
        "prediction": "library length = first_0x3E_offset + 1 when a 0x3E byte is present "
                      "(read stops at the first '>'), otherwise expected_bytes - 1 "
                      "(clean_return strips 4 bytes for a 3 byte 'ch>')",
    }
    p.records.append({"section": s, "id": "C01", "kind": "direct", "call": "capture() vs read by length",
                      "sent": "capture", "expected": None, "observed": DATA, "status": "ok",
                      "reply_len": len(payload), "verdict": "info",
                      "reply": json.dumps(result), "error": "", "note": ""})
    for key, value in result.items():
        print("    %-24s %s" % (key, value))


# =====================================================================================
# 6. signal generator, output muted throughout
# =====================================================================================

def section_generator(p):
    s = "generator"
    t = p.tsa
    t.set_error_byte_return(True)
    ULTRA_ONLY = {"ultra": EMPTY, "basic": USAGE}
    BASIC_ONLY = {"ultra": USAGE, "basic": EMPTY}
    # NOTE: no cleanup= on any call in this section may contain "output on"

    try:
        p.raw(s, "G01", "output off", expect=EMPTY, note="mute before changing mode")
        p.raw(s, "G02", "mode low output", expect=EMPTY, note="firmware mutes on mode change")
        p.raw(s, "G03", "output off", expect=EMPTY, note="mute again; level defaults to MAX here")
        p.raw(s, "G04", "level ?", expect=USAGE,
              note="prints the range for the current output mode; empty means not in output mode")
        p.raw(s, "G05", "level -76", expect=EMPTY, note="minimum level")
        p.raw(s, "G06", "level -30.5", expect=EMPTY, note="decimal level")
        p.raw(s, "G07", "level -76", expect=EMPTY)

        # frequency: zero-span sweep. 'sweep' with no arguments is the only readback.
        p.raw(s, "G08", "sweep cw 10000000", expect=EMPTY)
        p.raw(s, "G09", "sweep", expect=DATA, note="readback: start and stop should both be 10000000")

        # modulation keywords the library sends today. Matching is case-sensitive,
        # so the capitalised forms fail on both families.
        for i, word in enumerate(["AM_1kHz", "AM_10Hz", "NFM", "WFM"]):
            p.raw(s, "G%02d" % (10 + i), "modulation " + word, expect=USAGE, note="library keyword")
        p.raw(s, "G14", "modulation extern", expect=BASIC_ONLY, note="library keyword")
        # modulation grammar in current firmware
        p.raw(s, "G15", "modulation am", expect=EMPTY)
        p.raw(s, "G16", "modulation freq 1000", expect=EMPTY, note="Hz, clamped to 1..10000")
        p.raw(s, "G17", "modulation depth 50", expect=ULTRA_ONLY, note="percent")
        p.raw(s, "G18", "modulation fm", expect=ULTRA_ONLY)
        p.raw(s, "G19", "modulation deviation 3000", expect=ULTRA_ONLY,
              note="Hz, stored in 100 Hz steps")
        p.raw(s, "G26", "modulation nfm", expect=BASIC_ONLY)
        p.raw(s, "G27", "modulation wfm", expect=BASIC_ONLY)
        p.raw(s, "G20", "modulation off", expect=EMPTY)

        # level sweep: the firmware does not range-check this value
        p.raw(s, "G21", "levelchange 80", expect=EMPTY,
              note="library limit is 70; usage says 90 (Ultra) or 70 (Basic)")
        p.raw(s, "G22", "levelchange 0", expect=EMPTY)

        # output path (Ultra family): neither of these unmutes
        p.raw(s, "G23", "output normal", expect=ULTRA_ONLY)
        p.raw(s, "G24", "output mixer", expect=ULTRA_ONLY, note="firmware default path")
        p.raw(s, "G25", "output off", expect=EMPTY)

        # the same requests through the library
        p.lib(s, "G30", "modulation('AM_1kHz')", lambda: t.modulation("AM_1kHz"), expect=USAGE)
        p.lib(s, "G31", "modulation('am')", lambda: t.modulation("am"), expect=BLOCKED)
        p.lib(s, "G32", "modulation('off')", lambda: t.modulation("off"), expect=EMPTY)
        p.lib(s, "G33", "level(-30.5)", lambda: t.level(-30.5), expect=BLOCKED)
        p.lib(s, "G34", "level(-76)", lambda: t.level(-76), expect=EMPTY)
        p.lib(s, "G35", "level(10)", lambda: t.level(10), expect=EMPTY,
              note="outside the low-output range; firmware clamps, library does not object")
        p.quiet("level -76")
        p.lib(s, "G36", "level_change(80)", lambda: t.level_change(80), expect=BLOCKED)
        p.quiet("levelchange 0")
        p.lib(s, "G37", "output('mixer')", lambda: t.output("mixer"), expect=BLOCKED)
        p.lib(s, "G38", "output('off')", lambda: t.output("off"), expect=EMPTY)
        p.lib(s, "G39", "set_high_output_mode()", lambda: t.set_high_output_mode(),
              expect=BASIC_ONLY, note="Basic only: switches to high output, muted by the mode change")
        p.quiet("output off")
        if p.family == "basic":
            # the Basic's second generator range; read its level limits, then go back
            p.raw(s, "G44", "level ?", expect=USAGE, note="high output range, expect -38..13")
            p.raw(s, "G45", "output off", expect=EMPTY)
            p.raw(s, "G46", "mode low output", expect=EMPTY, note="muted again by the mode change")
            p.quiet("output off")
        p.lib(s, "G40", "set_sweep_cw(10e6)", lambda: t.set_sweep_cw(10e6), expect=EMPTY)
        p.raw(s, "G41", "sweep", expect=DATA, note="readback after library set_sweep_cw")
    finally:
        # always leave the generator muted and the unit back in input mode
        p.quiet("modulation off")
        p.quiet("levelchange 0")
        p.quiet("output off")
        p.quiet("mode low input")
    p.raw(s, "G50", "level ?", expect=EMPTY, note="empty confirms the unit is back in input mode")


# =====================================================================================
# reports
# =====================================================================================

def write_reports(p, out_dir, started):
    os.makedirs(out_dir, exist_ok=True)
    version = next((r["reply"].strip() for r in p.records if r["id"] == "I01"), "unknown")
    meta = {"started": started, "firmware": version, "family": p.family, "board": p.board,
            "firmware_build": p.build,
            "library": LIBRARY_VERSION,
            "aborted": p.dead, "help_commands": sorted(p.commands)}
    with open(os.path.join(out_dir, "probe_results.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "records": p.records}, f, indent=2)

    def cell(text, limit=90):
        text = text.strip().replace("\r\n", " / ").replace("\r", "").replace("|", "\\|")
        return text[:limit] + ("..." if len(text) > limit else "")

    lines = ["# Probe results", "",
             "- Started: %s" % started,
             "- Firmware: `%s`" % version.replace("\r\n", " / "),
             "- Library: tsapython %s" % LIBRARY_VERSION,
             "- Family: %s" % p.family,
             "- Board: %s" % p.board,
             "- Firmware build: %s" % (p.build,),
             "- Run aborted by watchdog: %s" % ("yes" if p.dead else "no"), ""]
    for section in SECTIONS:
        rows = [r for r in p.records if r["section"] == section]
        if not rows:
            continue
        lines += ["## %s" % section, "",
                  "| ID | Call | Sent | Expected | Observed | Verdict | Reply | Note |",
                  "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in rows:
            lines.append("| %s | `%s` | `%s` | %s | %s | %s | %s | %s |" % (
                r["id"], cell(r["call"]), cell(r["sent"]) or "(nothing)", r["expected"] or "",
                r["observed"], r["verdict"], cell(r["reply"] or r["error"]), cell(r["note"])))
        lines.append("")
    with open(os.path.join(out_dir, "probe_results.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    different = [r for r in p.records if r["verdict"] == "DIFFERENT"]
    changed = [r for r in p.records if r["verdict"].startswith("changed since")]
    print("\n%d probes, %d as predicted, %d DIFFERENT, %d informational" % (
        len(p.records), sum(r["verdict"] == "as predicted" for r in p.records),
        len(different), sum(r["verdict"] == "info" for r in p.records)))
    if changed:
        print("%d library calls behave differently from tsapython %s (library is %s):" % (
            len(changed), PREDICTED_FOR, LIBRARY_VERSION))
        for r in changed:
            print("  ~ %s %s: %s -> %s" % (r["id"], r["call"], r["expected"], r["observed"]))
    for r in different:
        print("  ! %s %s: expected %s, observed %s" % (r["id"], r["call"], r["expected"], r["observed"]))
    print("reports written to %s" % out_dir)


# =====================================================================================
# main
# =====================================================================================

def main():
    parser = argparse.ArgumentParser(description="Probe what a tinySA's firmware accepts.")
    parser.add_argument("--port", help="serial port; default is tsapython autoconnect()")
    parser.add_argument("--out", default=None, help="output folder")
    parser.add_argument("--timeout", type=float, default=30.0,
                        help="watchdog per call in seconds (firmware's own limit is about 20)")
    parser.add_argument("--backup", action="store_true",
                        help="add a read-only dump of calibration and config values")
    parser.add_argument("--capture", action="store_true", help="add the capture comparison")
    parser.add_argument("--generator", action="store_true",
                        help="add signal generator probes (output stays muted)")
    parser.add_argument("--only", choices=SECTIONS, help="run identity plus this one section")
    parser.add_argument("--no-restore", action="store_true", help="skip 'load 0' at the end")
    parser.add_argument("--yes", action="store_true", help="skip the generator confirmation")
    args = parser.parse_args()

    wanted = ["identity", "usage", "accept", "library"]
    if args.backup:
        wanted.append("backup")
    if args.capture:
        wanted.append("capture")
    if args.generator:
        wanted.append("generator")
    if args.only:
        wanted = ["identity", args.only]

    if "generator" in wanted and not args.yes:
        print("Generator probes switch the unit to low output mode. The output is muted the\n"
              "whole time and 'output on' is never sent. Disconnect anything sensitive from\n"
              "the RF port first.")
        if input("Type MUTED to continue: ").strip() != "MUTED":
            print("generator section skipped")
            wanted.remove("generator")

    tsa = tinySA()
    if args.port:
        connected = tsa.connect(args.port)
    else:
        _, connected = tsa.autoconnect()
    if not connected:
        sys.exit("ERROR: could not connect to a tinySA")

    started = datetime.datetime.now().isoformat(timespec="seconds")
    out_dir = args.out or os.path.join("probe_results", started.replace(":", "-"))
    prober = Prober(tsa, args.timeout)
    runners = {"identity": section_identity, "backup": section_backup, "usage": section_usage, "accept": section_accept,
               "library": section_library, "capture": section_capture,
               "generator": section_generator}
    try:
        for name in SECTIONS:
            if name in wanted:
                print("\n== %s ==" % name)
                runners[name](prober)
    except ProbeAbort as stop:
        print("\nSTOPPED: %s" % stop)
    except KeyboardInterrupt:
        print("\ninterrupted")
    finally:
        if not prober.dead:
            if not args.no_restore:
                prober.quiet("load 0")
            prober.quiet("resume")
        write_reports(prober, out_dir, started)
        if prober.dead:
            print("A call hung. Unplug and replug the tinySA before running again.")
            os._exit(2)   # the hung reader thread cannot be joined
        try:
            tsa.disconnect()
        except Exception:
            pass


if __name__ == "__main__":
    main()