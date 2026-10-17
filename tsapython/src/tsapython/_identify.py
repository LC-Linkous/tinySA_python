#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_identify.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Pure text helpers: no serial access and no state. They answer two questions from the
#   text a device has already sent back:
#
#       identify_device()  - which tinySA is this (family, board, firmware build)?
#       classify_reply()   - did the device accept the command, or reject it?
#
#   Both are derived from the tinySA firmware source (github.com/erikkaashoek/tinySA).
#   At the time of writing they are verified against captured replies from one device only:
#   a tinySA Ultra ZS405 on tinySA4_v1.4-143. The other boards are from the source.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

import re

# reply statuses, as written to the log file
STATUS_OK = "ok"
STATUS_USAGE = "usage"
STATUS_UNKNOWN = "unknown-command"
STATUS_REFUSED = "device-refused"
STATUS_TIMEOUT = "timeout"
STATUS_READ_FAILED = "read-failed"
STATUS_BLOCKED = "blocked"

# The Ultra family reports its board in the 'HW Version:' line of the 'version' reply.
# The exact strings changed between firmware builds (V0.5.2, V0.5.3, V0.5.3.2 and V0.5.4
# are all the ZS407), so boards are matched on the prefix.
_ULTRA_BOARD_PREFIXES = (
    ("V0.4.5", "ZS405"),   # tinySA Ultra
    ("V0.4.6", "ZS406"),   # tinySA Ultra+
    ("V0.5.", "ZS407"),    # tinySA Ultra+
)

# messages the firmware prints when it refuses a well-formed command
_DEVICE_REFUSALS = (
    "usb disk mode active",
    "Command timeout",
    "frequency range is invalid",
    "sweep points exceeds range",
    "scan point count is invalid",
    "sweep point count is invalid",
    "Key unmatched",
)

# a few commands print their usage without the 'usage:' prefix
_BARE_USAGE_PREFIXES = (
    "save {id}",
    "recall {id}",
    "trigger {value}",
    "trace {",
    "marker [n]",
    "channel [1-3]",
    "leveloffset [",
)


def identify_device(version_reply: str, info_reply: str = "") -> "dict[str, object]":
    """
    Work out which tinySA sent these replies.

    version_reply: text returned by the 'version' command
    info_reply:    text returned by the 'info' command (optional)

    Returns a dict with:
        family      'basic' | 'ultra' | 'unknown'
        board       'ZS304' | 'ZS405' | 'ZS406' | 'ZS407' | 'unknown'
        hw_version  the text after 'HW Version:' ('' on the Basic)
        build       [major, minor, commits] parsed from e.g. 'tinySA4_v1.4-143-g864bb27',
                    or None for firmware with no parsable version (self-built, 'unknown')
    """
    version_reply = version_reply.strip()
    info_first_line = info_reply.strip().split("\r\n")[0] if info_reply else ""

    # The Basic is built as 'tinySA_...', the Ultra family as 'tinySA4_...'
    if version_reply.startswith("tinySA4"):
        family = "ultra"
    elif version_reply.startswith("tinySA"):
        family = "basic"
    else:
        family = "unknown"

    hw_match = re.search(r"HW Version:\s*(\S+)", version_reply)
    hw_version = hw_match.group(1) if hw_match else ""

    board = "unknown"
    if family == "basic":
        board = "ZS304"
    elif family == "ultra":
        for prefix, name in _ULTRA_BOARD_PREFIXES:
            if hw_version.startswith(prefix):
                board = name
                break
        else:
            # firmware from v1.4-190 on also names the board on the first info line
            info_match = re.search(r"ZS40[567]", info_first_line)
            if info_match:
                board = info_match.group(0)

    build_match = re.search(r"_v(\d+)\.(\d+)-(\d+)-g[0-9a-f]+", version_reply)
    build = [int(x) for x in build_match.groups()] if build_match else None

    return {"family": family, "board": board, "hw_version": hw_version, "build": build}


def classify_reply(sent: str, reply: "bytes | bytearray | None") -> "tuple[str, str]":
    """
    Classify a cleaned device reply. Returns (status, reason).

    sent:  the command string that was written (with or without the trailing CRLF)
    reply: what tinySA_serial() returned for it

    A usage line is only a rejection when the command carried an argument. A bare
    command, or one with '?', is a query: the usage line IS the answer.
    """
    if reply is None:
        return STATUS_READ_FAILED, "no reply was read from the serial port"

    words = sent.strip().split()
    name = words[0] if words else ""
    is_query = (len(words) <= 1) or words[1].startswith("?")

    text = bytes(reply).decode("utf-8", errors="replace").strip()
    if text == "":
        return STATUS_OK, ""
    if name and text == name + "?":
        return STATUS_UNKNOWN, "this firmware does not have the '" + name + "' command"
    for refusal in _DEVICE_REFUSALS:
        if refusal in text:
            return STATUS_REFUSED, "device replied: " + refusal
    if not is_query:
        if "usage:" in text or text.startswith(_BARE_USAGE_PREFIXES):
            return STATUS_USAGE, "device rejected the argument"
    return STATUS_OK, ""
