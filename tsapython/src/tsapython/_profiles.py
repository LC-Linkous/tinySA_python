#! /usr/bin/python3

##------------------------------------------------------------------------------------------------\
#   tinySA_python (tsapython)
#   'src/tsapython/_profiles.py'
#   UNOFFICIAL Python API based on the tinySA official documentation at https://www.tinysa.org/wiki/
#
#   Device profiles: what each tinySA model accepts. Values are read from the tinySA firmware
#   source (github.com/erikkaashoek/tinySA, v1.4-244). The library chooses a profile from the
#   'version' and 'info' replies at connect time, or from select_existing_device().
#
#   Verification status (which profiles have been checked against a real unit) is in the
#   README section "Firmware Compatibility".
#
#   Author(s): Lauren Linkous
##--------------------------------------------------------------------------------------------------\

from dataclasses import dataclass, field, replace

# Oldest firmware build the library is written for (commits after the v1.4 tag).
# Older firmware still connects; the log records that it is below the floor.
FIRMWARE_FLOOR = (1, 4, 182)

# Build where the 4th scanraw argument became a bit field (2 = repeat until interrupted)
SCANRAW_STREAM_BUILD = (1, 4, 177)


@dataclass(frozen=True)
class DeviceProfile:
    family: str                      # 'basic' | 'ultra'
    board: str                       # 'ZS304' | 'ZS405' | 'ZS406' | 'ZS407' | 'unknown'
    name: str                        # human readable
    verified: str                    # 'hardware' | 'source'

    # size limits
    max_points: int
    markers: int
    traces: int
    screen_width: int
    screen_height: int

    # frequency limits in Hz
    min_freq: float
    max_freq_normal: float           # top of the range with ultra mode off
    max_freq_ultra: float            # top of the range with ultra mode on (Ultra family)
    min_sg_freq: float
    max_sg_freq: float

    # numeric ranges
    rbw_khz: tuple[float, float]
    levelchange_db: tuple[float, float]
    level_low_output: tuple[float, float]
    level_high_output: tuple[float, float] | None
    if_hz: tuple[float, float]
    scanraw_offset: int
    palette_entries: int

    # words the firmware accepts
    mode_words: tuple[str, ...]
    modulation_words: tuple[str, ...]
    output_words: tuple[str, ...]
    spur_words: tuple[str, ...]
    calc_words: tuple[str, ...]
    unit_words: tuple[str, ...]
    leveloffset_words: tuple[str, ...]
    correction_words: tuple[str, ...]

    # commands present in this family's build (the device's own 'help' reply is
    # consulted first when one has been read; this is the fallback)
    commands: frozenset[str] = field(default_factory=frozenset)

    def has_command(self, name: str) -> bool:
        return name in self.commands


_COMMON_COMMANDS = frozenset("""
version reset freq dac saveconfig clearconfig data frequencies scan scanraw abort zero sweep test
touchcal touchtest pause resume wait waitscan repeat status caloutput save recall trace trigger
marker line usart usart_cfg capture refresh touch release vbat vbat_offset help info color if
actual_freq attenuate level sweeptime leveloffset levelchange modulation rbw mode spur load
ext_gain output deviceid selftest correction calc menu text remark threads channel
""".split())

_ULTRA_ONLY_COMMANDS = frozenset("""
hop lna lna2 agc if1 freq_corr avoid direct ultra nf time restart usbdisk k sd_list sd_read sd_delete
""".split())

BASIC = DeviceProfile(
    family="basic", board="ZS304", name="tinySA Basic (ZS304)", verified="source",
    max_points=290, markers=4, traces=3, screen_width=320, screen_height=240,
    min_freq=100e3, max_freq_normal=350e6, max_freq_ultra=350e6,
    min_sg_freq=100e3, max_sg_freq=960e6,
    rbw_khz=(2.0, 600.0), levelchange_db=(-70.0, 70.0),
    level_low_output=(-76.0, -6.0), level_high_output=(-38.0, 13.0),
    if_hz=(433e6, 435e6), scanraw_offset=128, palette_entries=32,
    mode_words=("low", "high"),
    modulation_words=("off", "am", "nfm", "wfm", "extern"),
    output_words=("on", "off"),
    spur_words=("off", "on"),
    calc_words=("off", "minh", "maxh", "maxd", "aver4", "aver16", "aver", "quasi"),
    unit_words=("dBm", "dBmV", "dBuV", "RAW", "V", "Vpp", "W", "dBV"),
    leveloffset_words=("low", "high", "switch", "receive_switch"),
    correction_words=("low", "high", "out"),
    commands=_COMMON_COMMANDS,
)

_ULTRA_BASE = DeviceProfile(
    family="ultra", board="ZS405", name="tinySA Ultra (ZS405)", verified="hardware",
    max_points=450, markers=8, traces=4, screen_width=480, screen_height=320,
    min_freq=100e3, max_freq_normal=800e6, max_freq_ultra=5.33e9,
    min_sg_freq=100e3, max_sg_freq=1130e6,
    rbw_khz=(0.2, 850.0), levelchange_db=(-90.0, 90.0),
    level_low_output=(-76.0, -6.0), level_high_output=None,
    if_hz=(975e6, 979e6), scanraw_offset=174, palette_entries=32,
    mode_words=("low",),
    modulation_words=("off", "am", "fm"),
    output_words=("on", "off", "normal", "mixer"),
    spur_words=("off", "on", "auto"),
    calc_words=("off", "minh", "maxh", "maxd", "aver4", "aver16", "aver", "quasi", "log", "lin"),
    unit_words=("dBm", "dBmV", "dBuV", "RAW", "V", "Vpp", "W", "dBV"),
    leveloffset_words=("low", "switch", "receive_switch", "out_switch", "lna", "harmonic",
                       "shift", "shift1", "shift2", "shift3", "shift4", "drive1", "drive2",
                       "drive3", "direct", "direct_lna", "ultra", "ultra_lna", "harmonic_lna",
                       "adf", "direct_output", "low_output"),
    correction_words=("low", "lna", "ultra", "ultra_lna", "direct", "direct_lna", "harm",
                      "harm_lna", "out", "out_direct", "out_adf", "out_ultra", "off", "on"),
    commands=_COMMON_COMMANDS | _ULTRA_ONLY_COMMANDS,
)

ULTRA_ZS405 = _ULTRA_BASE
ULTRA_PLUS_ZS406 = replace(_ULTRA_BASE, board="ZS406", name="tinySA Ultra+ (ZS406)", verified="source",
                           max_freq_normal=900e6, max_freq_ultra=5.42e9, if_hz=(1067e6, 1073e6))
ULTRA_PLUS_ZS407 = replace(_ULTRA_BASE, board="ZS407", name="tinySA Ultra+ (ZS407)", verified="source",
                           max_freq_normal=900e6, max_freq_ultra=7.37e9, if_hz=(1067e6, 1073e6))
ULTRA_UNKNOWN_BOARD = replace(_ULTRA_BASE, board="unknown", name="tinySA Ultra family (board not recognised)",
                              verified="source")

# before a device is identified: the widest Ultra limits, as 3.x behaved
DEFAULT = replace(_ULTRA_BASE, board="unknown", name="not identified (Ultra family defaults)",
                  verified="source", max_freq_ultra=15e9)

PROFILES: dict[str, DeviceProfile] = {
    "BASIC": BASIC, "ZS304": BASIC,
    "ULTRA": ULTRA_ZS405, "ZS405": ULTRA_ZS405,
    "ULTRA+": ULTRA_PLUS_ZS407, "ZS406": ULTRA_PLUS_ZS406, "ZS407": ULTRA_PLUS_ZS407,
}


def profile_for(family: str, board: str) -> DeviceProfile:
    """Profile for an identify_device() result."""
    if family == "basic":
        return BASIC
    if family == "ultra":
        return PROFILES.get(board, ULTRA_UNKNOWN_BOARD)
    return DEFAULT
