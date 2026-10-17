#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_log.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Optional log file, turned on with tinySA.set_log_file(). Off by default.
#
#   FORMAT: JSON Lines. One JSON object per line, UTF-8. Each record is written and
#   flushed as it happens; nothing is kept in memory. See the README section "Logging"
#   for the record types and fields.
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

import base64
import datetime
import json
import typing

LOG_FORMAT = 1                  # bump when a field is renamed or removed
LOG_LEVELS = ("commands", "data")
COMMANDS_LEVEL_MAX_CHARS = 256  # reply text kept per record at the 'commands' level


def utc_timestamp() -> str:
    # ISO 8601, UTC, millisecond resolution, e.g. 2026-10-09T19:22:04.118Z
    now = datetime.datetime.now(datetime.timezone.utc)
    return now.strftime("%Y-%m-%dT%H:%M:%S.") + ("%03d" % (now.microsecond // 1000)) + "Z"


class JsonlLog:
    def __init__(self, path: str, level: str = "commands") -> None:
        if level not in LOG_LEVELS:
            raise ValueError("log level must be one of " + str(LOG_LEVELS))
        self.path = path
        self.level = level
        self.seq = 0
        # append: one file can hold several sessions, each starting with a 'session' record
        self._file: "typing.IO[str] | None" = open(path, "a", encoding="utf-8", newline="\n")

    def write(self, record_type: str, fields: "dict[str, object]") -> None:
        if self._file is None:
            return
        record: "dict[str, object]" = {"t": utc_timestamp(), "type": record_type}
        record.update(fields)
        self._file.write(json.dumps(record, separators=(",", ":")) + "\n")
        self._file.flush()

    def write_command(self, function: str, sent: str, status: str, elapsed_ms: int,
                      reply: "bytes | bytearray | None", binary: bool, reason: str) -> None:
        self.seq += 1
        data = bytes(reply) if reply is not None else b""
        fields: "dict[str, object]" = {
            "seq": self.seq,
            "function": function,
            "sent": sent.strip(),
            "status": status,
            "elapsed_ms": elapsed_ms,
        }
        if binary:
            # binary replies (scanraw, capture) are never written as text
            fields["reply"] = ""
            fields["reply_len"] = len(data)
            fields["truncated"] = self.level != "data"
            if self.level == "data":
                fields["reply_b64"] = base64.b64encode(data).decode("ascii")
        else:
            text = data.decode("utf-8", errors="replace")
            keep_all = (self.level == "data") or (len(text) <= COMMANDS_LEVEL_MAX_CHARS)
            fields["reply"] = text if keep_all else text[:COMMANDS_LEVEL_MAX_CHARS]
            fields["reply_len"] = len(data)
            fields["truncated"] = not keep_all
        fields["reason"] = reason
        self.write("command", fields)

    def close(self) -> None:
        if self._file is not None:
            self._file.close()
            self._file = None
