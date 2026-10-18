# Changelog

All notable changes to tinySA_python / `tsapython` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

Work on the current development branch. Entries move to a versioned section on
release.

## [4.0.0] - unreleased

API changes. See the README section "Upgrading to 4.0.0". Developed on top of
3.1.0; to be verified on current tinySA firmware before release.

### Changed (breaking)
- A command the device rejects (`usage:` line, `name?`, or a refusal such as
  `usb disk mode active`) returns the library's error value (`b''`, or
  `b'ERROR'` with `set_error_byte_return(True)`) instead of the device's text.
  `command()` still returns the raw text.
- The generator output is gated: `output("on")`, `set_output_on()` and
  `cal_output()` with any value other than `"off"` return the error value and
  send nothing until `set_output_allowed(True)` has been called.
- The library identifies the device at `connect()`/`autoconnect()` (sends
  `version`, `info`, `help`) and applies a per-model profile. Commands the
  device lacks, words its model lacks, out-of-range `if`/`level`/`levelchange`
  values and marker/trace numbers above the model's count are refused before
  sending. `identifyOnConnect = False` skips identification.
- `scan_raw()` accepts `unbuf` 0 or 1 only.
- The serial read timeout defaults to 120 s instead of waiting indefinitely.
  `tinySA.DEFAULT_SERIAL_TIMEOUT`, `tinySA(serial_timeout=...)` and
  `set_serial_timeout(None)` adjust or disable it.
- Oldest supported firmware is v1.4-182 (October 2024). Older firmware connects
  with a warning and a `firmware-below-floor` log event.

### Added
- `_profiles.py`: `DeviceProfile` dataclass and the `BASIC`, `ZS405`, `ZS406`,
  `ZS407` profiles; `identify()`, `get_profile()`, `profile`, `profileDetected`,
  `deviceCommands`, `firmwareBuild`; `select_existing_device()` now selects a
  profile by name.
- `set_output_allowed()`, `get_output_allowed()`, `setup_generator()`,
  `set_generator()`. Both helpers pause the sweep around settings changes:
  in output mode the firmware services `level`/`sweep`/`mode` only between
  generator sweeps (about 20 s on hardware), immediately while paused.
- The text reader requires the command's own echo before accepting a prompt,
  so a late reply from a timed-out command is discarded instead of being
  returned as the answer to the next command.
- `scan_raw_stream()`: the device-side continuous scanraw (firmware v1.4-177 or
  later), experimental until run on hardware.
- README sections: Upgrading to 4.0.0, Device Profiles, RF Output Setting; web
  UI link (https://lc-linkous.github.io/tinysa-web/).
- Hardware tests for identification, the gates and the output setting.

### Fixed
- Output mode: a between-sweeps command (`pause`, `level`, `sweep`, `resume`,
  `mode`, ...) sent within a few ms of `output`, `modulation`, `caloutput` or
  `leveloffset` was dropped by the firmware and answered with `Command timeout`
  20 s later (ZS405, v1.4-252). The library now waits
  `SETTLE_AFTER_IMMEDIATE_SETTER_S` (0.4 s) after those four commands and
  resends a command once when the device replies `Command timeout`.
- `Command timeout` (firmware v1.4-222+) is recognised as the end of a reply,
  so a dropped command costs about 20 s instead of the full read timeout.
- A log record for a read that timed out now keeps the bytes that did arrive.
- `tests/test_hardware_output.py`: the fixture releases the port and restores
  the device when setup fails, so later tests no longer skip with
  "no tinySA device connected"; `TSAPYTHON_LOG=<path>` turns logging on.

## [3.1.0] - 2026-10-17

Non-breaking firmware-compatibility release: every call that worked before
behaves the same. Read from the tinySA firmware source (v1.4-244). Verified on
hardware with a tinySA Ultra ZS405 running tinySA4_v1.4-143 (the probe script
matched its predictions 36 of 36 times); the Basic and Ultra+ boards are from
firmware source only.

### Added
- Optional JSON Lines log file: `set_log_file(path, level)`, `close_log_file()`,
  `get_log_file()`. Records every command, the reply, a status (`ok`, `usage`,
  `unknown-command`, `device-refused`, `timeout`, `read-failed`, `blocked`) and
  the reason. Off by default; nothing is kept in memory.
- `set_serial_timeout(seconds)` / `get_serial_timeout()`. The default stays
  `None` (wait indefinitely), so long sweeps are unaffected.
- Signal generator: `modulation()` accepts the current firmware words
  (`am`, `fm`, `nfm`, `wfm`, `extern`, `off`); new `modulation_freq()`,
  `modulation_depth()`, `modulation_deviation()`, `set_mod_AM()`, `set_mod_FM()`;
  `output()` accepts `normal` and `mixer` with aliases
  `set_output_path_normal()` / `set_output_path_mixer()`.
- `calc()` accepts `aver`, `quasi`, `log`, `lin`; `spur()` accepts `auto`
  (`spur_auto()`); `trace_units()` accepts `dBV`; `level_offset()` accepts
  `high`, `shift4`, `direct_output`, `low_output`; `set_IF()` accepts the Ultra
  (975M..979M) and Ultra+ (1067M..1073M) ranges.
- `trace_freeze(ID, val="on"|"off")`, `trace_unfreeze(ID)`, and an optional
  third argument on `trace_action()`.
- Getters: `get_rbw()`, `get_attenuation()`, `get_sweep_time()`, `get_IF()`,
  `get_scanraw_offset()`, `get_noise_figure()`, `get_dac_value()`, `get_calc()`,
  `get_sweep_range()`; `decode_number()` for the pre-v1.4-230 `:` artifact.
- New command wrappers: `waitscan()`, `channel()`, `avoid()`, `usbdisk()`,
  `time()`, `correction_reset()`, `sweep_mode()`, `marker_mode()`,
  `marker_all_off()`, `marker_read()`, `resume(count)`, `sd_list(pattern)`.
- SD card: `list_sd_files()`, `save_sd_file()`, `save_firmware_dump()` (copies
  the device's own firmware dump, made with DUMP FIRMWARE on the device, to the
  computer).
- `tests/probe_firmware_returns.py`: manual hardware probe with JSON/markdown
  reports; seven hardware set-and-read-back tests in `tests/test_hardware.py`.
- README sections: Logging, Firmware Compatibility, Change Summary,
  Deprecated Functions, Reading Values Back, Commands added in 3.1.0.
- Internal helpers `identify_device()` and `classify_reply()` (`_identify.py`).

### Changed
- `level()`, `level_change()`, `rbw()` and `trigger_level()` accept decimals;
  `level_change()` accepts -90..90.
- `scan()` and `scan_raw()` accept `start == stop` (zero span); `scan_raw()`
  accepts `unbuf=0`.
- `calc("quasip")` and `set_calc_quasip()` send `calc quasi`. The firmware
  renamed the keyword in May 2022 and rejects `quasip`.
- `modulation("AM_1kHz" | "AM_10Hz" | "NFM" | "WFM")` and their aliases send the
  current firmware equivalent; the firmware has rejected the old keywords since
  Nov 2020.
- `capture()` is read by length and returns exactly `width * height * 2` bytes.
- `sd_read()` reads the 4-byte size prefix and returns exactly the file's bytes.
- A text reply is complete at the `ch> ` prompt rather than at the first `>`
  byte, so replies containing `>` are no longer cut short.
- The serial read loop sleeps 1 ms when no data is waiting, instead of spinning
  a CPU core.
- `tsapython.__version__` is read from the installed package metadata.

### Deprecated
- `set_mod_AM_1khz()`, `set_mod_AM_10Hz()`, `trace_clear()`. Still callable;
  see the README section "Deprecated Functions".

### Fixed
- `hop()` raised `UnboundLocalError` for any `outmask` other than 1, 2 or
  `None`. 3 (the firmware default) is now accepted; other values return the
  error value.
- `wait()` with no argument returned the error value; it now sends `wait`.
- `attenuate(31)` and `color(31, ...)` were refused by an off-by-one.
- `trace_freeze(ID)` sent `trace {ID} freeze`, which the firmware parses and
  ignores; it now sends `trace {ID} freeze on`.
- `capture()` stopped at the first `0x3E` pixel byte and returned one byte too
  few.
- `examples/using_command_func.py` and the README sent `scan 150e6 200e6`,
  which the firmware reads as 150 Hz to 200 Hz.

## [3.0.1] - 2026-09-19

Tooling, metadata, and repository-hygiene release. No API or behavior
changes: the shipped package gains full type annotations (now CI-enforced,
making the long-standing `py.typed` marker a kept promise) and the
repository gains the quality gates and health files below.

### Added
- Repository and packaging polish, ported from the hackrfpy hardening pass:
  `SECURITY.md` (private vulnerability reporting, scope, and the
  hardware-damage carve-out), a `.gitattributes` line-ending policy (LF
  everywhere, binary protections, one-time renormalize), PyPI metadata
  (`Homepage` and `Changelog` project URLs, `keywords`, richer classifiers),
  a CI coverage gate at 85% minimum (measured 86% at adoption), the ruff
  blocking ruleset expanded to `E9 + F + W` (pre-existing whitespace
  findings autofixed; full `E` remains a deferred, reviewed cleanup), a
  written coverage-and-platform policy plus PR expectations in
  CONTRIBUTING, and Keep-a-Changelog compare links in this file.
- Continuous integration: GitHub Actions workflow running the hardware-free
  test suite across Windows, Linux, and macOS on Python 3.10–3.13, plus a
  ruff + mypy lint job and a package build check, on every push and pull
  request.
- Type annotations across the entire shipped package (all 226 definitions),
  and `mypy` added as a blocking CI gate (`disallow_untyped_defs`). The package
  has always shipped a `py.typed` marker, which tells downstream type-checkers
  the inline annotations are real; previously 0 of 226 definitions were
  annotated, so that marker was a false promise. It is now enforced.
- `MixinHost` base class (`_host.py`) making the contract between the `tinySA`
  host class and the command mixins explicit and type-checkable. At runtime it
  is an empty class; composition and behavior are unchanged.
- Committed `uv.lock` and a PEP 735 `dev` dependency group, making
  `uv sync` / `uv run pytest` the blessed development workflow (the previous
  README warning against `uv run pytest` no longer applies).
- Ruff configuration in `pyproject.toml`. The blocking ruleset is deliberately
  small (E9 syntax errors + F pyflakes); style rules are a planned follow-up.
- Release workflow now runs the test suite, lint, and type check before
  building or publishing, so a release cannot ship with a red suite.
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `CHANGELOG.md`, issue templates, and a pull request template.
- Captured-fixture provenance: `tests/collect_samples.py` now records the
  device model and firmware in the generated fixture header, and the existing
  `captured_responses.py` header was retrofitted (tinySA ULTRA,
  tinySA4_v1.4-143-g864bb27).
- `zenodo.json` now carries a `version` field matching `CITATION.cff`.

### Fixed
- `get_color()` crashed with a `TypeError` whenever a color lookup matched: it
  applied a `str` regex pattern to the raw `bytearray` device reply. Found by
  the new type checking. The reply is now decoded before matching, and a `None`
  reply no longer crashes the length check.
- `color()` no longer crashes if called with a valid ID but `RGB=None`; it
  returns the error byte instead.
- Serial-touching methods now raise a clear `RuntimeError` ("not connected:
  call connect() or autoconnect() first") instead of an opaque
  `AttributeError` on `NoneType` when used before connecting.
- A failed serial read inside `tinySA_serial()` now propagates `None` instead
  of crashing in `clean_return()`.
- Out-of-range *string* inputs to `correction()` and `set_IF1()` now return
  the error byte instead of raising `TypeError` on comparison.
- README no longer references `requirements.txt` / `test_requirements.txt`,
  which were removed from the repository in the 3.0.0 packaging restructure;
  install instructions now go through the `pyproject.toml` extras.
- README repository-structure diagrams updated to match the actual tree
  (added `examples/filtering_scan_artifacts.py`, `examples/find_peaks.py`,
  and `tests/diagnose_reset.py`; removed the requirements files).
- Removed unused imports and dead local variables flagged by lint. No
  behavior change.
- Removed `examples/__init__.py` — the examples directory is a collection of
  runnable scripts, not a package.
- Merged two near-duplicate README sections documenting
  `tests/collect_samples.py`.

### Changed
- Alias-function signatures aligned with the methods they delegate to
  (`set_color`, `preform_touch`, `restart_device`, `get_sample_pts`,
  `trigger_level`, `set_ultra_start`/`set_ultra_harmonic`).

## [3.0.0]

### Added
- Published to PyPI as [`tsapython`](https://pypi.org/project/tsapython/).
- Automated test suite (pytest): command-construction tests via a recorded
  serial seam, parsing tests against captured device responses, and
  `@pytest.mark.hardware` tests that self-skip without a connected device.
- `tests/collect_samples.py` helper for freezing real device responses into
  parsing fixtures.
- Runnable examples under `examples/`, including scan/scanraw plotting,
  static and realtime waterfalls, artifact filtering, and peak finding.
- Trusted-publishing release workflow (`release.yml`) building with uv and
  publishing to PyPI on GitHub release.
- Zenodo archival with DOI (`zenodo.json`, `CITATION.cff`).

### Changed
- Restructured into an installable package with a `src/` layout: the `tinySA`
  class is now composed from per-category mixins under
  `src/tsapython/_commands/`, with shared state, serial handling, and helpers
  in `core.py`. The public API (`from tsapython import tinySA`) is unchanged.
- Packaging moved fully to `pyproject.toml` (uv build backend), with
  `plotting` and `test` extras replacing the loose requirements files.

## [2.0.0] and earlier

See the [GitHub releases](https://github.com/LC-Linkous/tinySA_python/releases)
for pre-3.0.0 history, when the library shipped as a single-class module.

[Unreleased]: https://github.com/LC-Linkous/tinySA_python/compare/v4.0.0...HEAD
[4.0.0]: https://github.com/LC-Linkous/tinySA_python/compare/v3.1.0...v4.0.0
[3.1.0]: https://github.com/LC-Linkous/tinySA_python/compare/v3.0.1...v3.1.0
[3.0.1]: https://github.com/LC-Linkous/tinySA_python/compare/v3.0.0...v3.0.1
[3.0.0]: https://github.com/LC-Linkous/tinySA_python/releases/tag/v3.0.0
