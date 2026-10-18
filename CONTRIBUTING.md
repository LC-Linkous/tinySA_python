# Contributing to tinySA_python

Thanks for your interest in improving tinySA_python (`tsapython` on PyPI). This
is an **unofficial** community library. It is not endorsed by the official
tinySA product or company, and nothing here should be read as an authoritative
statement about device behavior — always defer to the
[official tinySA documentation](https://tinysa.org/wiki/).

This project drives real hardware over serial. Improper usage may **destroy
your device** — please read the safety notes in the README before contributing
anything that changes what gets sent to the device, especially around output /
signal-generator commands.

## Ways to contribute

- **Report a bug** — open an issue with the bug template. Include your OS,
  Python version, device model (Basic / Ultra / Ultra+), and the firmware
  version (from `info()`).
- **Request a feature** — open an issue with the feature template. Note that
  GUI features are out of scope; this is deliberately a non-GUI API.
- **Improve docs** — README fixes, clearer examples, and beginner notes are all
  welcome and don't require hardware.
- **Submit code** — see the workflow below.

## Development setup

The installable project lives in the `tsapython/` subdirectory (the one with
`pyproject.toml`). This project uses [uv](https://docs.astral.sh/uv/) with a
committed `uv.lock`.

```bash
cd tsapython
uv sync                 # pyserial + numpy + dev group, editable install of tsapython
uv run pytest           # hardware tests self-skip without a device
```

Run everything through `uv run` so the synced environment is used. A bare
`python ...` can silently create or use a second environment.

## Before you open a pull request

Run these from the `tsapython/` directory:

```bash
uv run pytest -m "not hardware"     # full hardware-free suite must pass
uv run ruff check .                 # lint (blocking ruleset: E9 + F + W)
uv run mypy                         # type check (blocking; the package ships py.typed)
```

CI runs the same suite across Windows, Linux, and macOS on Python 3.10–3.13,
plus the lint + type checks and a package build check. New and changed code
must be fully annotated (`disallow_untyped_defs` is enforced on
`src/tsapython`); tests and examples are not type-gated.

Also expected with a code PR:

- **A CHANGELOG entry** under `[Unreleased]` — say what changed and why.
- **Coverage** — CI gates at 85% (`--cov-fail-under=85`); new code arrives
  with its tests.
- **Hardware evidence for core changes** — any change under `src/tsapython/`
  should include evidence of a run against a real tinySA (hardware tests
  passing); paste the pytest tail in the PR. Docs, examples, and test-only
  changes are exempt. CI cannot attach a device, so this half of the gate is
  enforced by review.

## Test coverage and platform policy

CI gates coverage at **85% minimum** (`--cov-fail-under=85`) on every leg of
the matrix. Coverage below the gate fails the build; new code arrives with
the tests that keep it above.

**Supported platforms are the ones verified against a real tinySA** —
currently Windows (primary). A platform is promoted when the full suite,
hardware tests included, passes there with a real device, and is then held
to the same standards.

## Adding a command

The `tinySA` class is composed from mixins in `src/tsapython/_commands/`, wired
together in `core.py`. The class talks to the device only through `self.ser`
(a pyserial `Serial`) and the single method `tinySA_serial()` — the two seams
the test fixtures exploit. To add a command:

1. Add the method to the appropriate mixin (`acquisition.py`, `calibration.py`,
   `display_ui.py`, `levels_gain.py`, `markers_traces.py`, `output_signal.py`,
   `presets_config.py`, or `system_info.py`).
2. Route the device write through `tinySA_serial()` — don't touch `self.ser`
   directly from a command method.
3. Add a **command-construction test** in the matching `tests/test_*.py` file:
   use the `tsa` fixture (a `tinySA` wired to the recorder) to assert the exact
   command string the method builds (e.g. `"rbw 100\r\n"`) on the happy path, and assert that **nothing
   is sent** on the validation-error path.
4. If the command's *response* needs parsing, add a parsing test using the
   `parsing_tsa` fixture against canned bytes — ideally frozen from real
   hardware via `tests/collect_samples.py` rather than hand-written.
5. Follow the existing input-validation pattern (accepted-values checks with
   `verbose` / `error_byte` behavior) so error handling stays consistent.
6. **Gate it on the device profile** (since 4.0.0). Before sending, check what
   the connected model accepts, and return `self.error_byte_return()` if it
   does not:
   - a command that only some models have: `if not self._check_command("hop"): return self.error_byte_return()`
   - an argument word that varies by family: `if not self._check_word("spur", val, self.profile.spur_words): ...`
   - a numeric range that varies: read it from `self.profile` (`if_hz`, `levelchange_db`, `markers`, ...)
   Every ERROR message printed before the return is picked up by the log file as
   the `reason`, so word it for a reader.
7. If the command's reply is a **query** (the device answers with a usage line
   that carries the current value), send it through `tinySA_serial(..., _raw=True)`
   so the usage line is not treated as a rejection, and parse it the way the
   getters in `core.py` do (`_query_value()`).
8. Add the command to the README's command list and, if it exists only from a
   certain firmware build, to the "Commands added" table with that build.

### Adding or changing a device profile

Profiles live in `src/tsapython/_profiles.py`, one frozen `DeviceProfile` per
model, built from the tinySA firmware source (`nanovna.h`, `sa_cmd.c`, `main.c`).

- Values come from the firmware, not from the wiki: `POINTS_COUNT`, `MARKER_COUNT`,
  `TRACES_MAX`, `LCD_WIDTH/HEIGHT`, the `usage_printf` strings in `sa_cmd.c` for
  ranges and word lists, and the `commands[]` table in `main.c` for the command set.
- A new board of an existing family (another Ultra+ revision, say) is a
  `replace(_ULTRA_BASE, board=..., name=..., ...)` plus an entry in `PROFILES`
  and, if it reports a new `HW Version` prefix, a line in
  `_identify.py::_ULTRA_BOARD_PREFIXES`.
- Set `verified="source"` until the probe script has run on a real unit of that
  board; then change it to `"hardware"` and record the firmware build and date in
  the README's Supported Devices table.
- Add the board to `tests/test_identify.py` (a reconstructed `version`/`info`
  reply) and to `tests/test_v4_profiles.py` (the gates that differ).

### How device replies are classified

`_identify.py::classify_reply()` turns a cleaned reply into one of `ok`,
`usage`, `unknown-command`, `device-refused`, `read-failed`. `tinySA_serial()`
returns the error value for the last three (except with `_raw=True`) and the log
records the status. If a firmware change adds a new refusal message, add it to
`_DEVICE_REFUSALS`; if a command prints its usage without the `usage:` prefix,
add the prefix to `_BARE_USAGE_PREFIXES`.

## Tests that touch hardware

Three layers, from safest to least:

| Layer | Marker | Runs when | What it needs |
| --- | --- | --- | --- |
| Hardware | `@pytest.mark.hardware` | `uv run pytest -m hardware`; self-skips without a device | A tinySA on USB. Nothing switches the RF output on; each test restores what it changes |
| Hardware, output on | `@pytest.mark.hardware_output` | `TSAPYTHON_OUTPUT_OK=1 uv run pytest -m hardware_output`; deselected by default in `pyproject.toml` and skipped without the environment variable | A load or attenuator on the RF port. Proves the device accepted each generator setting, not what came out |
| Bench | `tests/bench_generator.py` (a script, not pytest) | By hand, once per release | Attenuator, a receiver (HackRF One or any SDR), ideally the path loss measured with a VNA. Steps through the generator states and records your readings |

Two manual helpers complete the set:

- `tests/probe_firmware_returns.py` asks a connected device what its firmware
  accepts and writes `probe_results.json` / `.md`. Run it before and after a
  firmware update, and attach the result to an issue when reporting a board the
  library has not been verified on. `--backup` dumps calibration values before a
  firmware update; `--generator` adds muted generator probes.
- `tests/collect_samples.py` freezes read-only replies into `tests/fixtures/`
  for the parsing tests. If you add a parser, add a captured fixture rather than
  a hand-written one where possible, and note which device model and firmware
  produced it.

The fake ports in `tests/conftest.py` (`tsa` / `recorder`, `parsing_tsa`) and the
`ScriptedPort` classes in `tests/test_log.py`, `tests/test_v4_profiles.py` and
`tests/test_core_paths.py` cover everything else without a device; CI runs only
those.

`parsing_tsa`'s `FakePort` behaves like pyserial where the readers care:
`reset_input_buffer()` flushes (so a reply loaded before the command is thrown
away, as a stale reply would be on hardware), and replies are queued per write:

```python
port = parsing_tsa.ser
port.answer(b"deviceid\r\ndeviceid 3\r\nch> ")            # the next write gets this reply
port.answer(reply, chunks=5)                               # ...delivered over five reads
port.answer_chunked([b"deviceid\r\ndevi", b"ceid 3\r\nch", b"> "])   # exact packet boundaries
```

Test a parser with the reply in pieces as well as whole: a real port delivers
USB packets, and the bugs that reached hardware (a prompt cut at `>`, a stale
reply accepted as the answer) were all boundary bugs. Load `_buf` directly only
when calling a reader (`get_serial_return`, `get_binary_return`, ...) on its own.

## Releasing

1. Bump `version` in `tsapython/pyproject.toml`, `CITATION.cff` and `zenodo.json`
   together; move the `[Unreleased]` changelog entries into a dated section and
   add the compare link at the bottom.
2. Push the commit, then push a tag `vX.Y.Z`. The `build-release.yml` workflow
   checks that the tag matches `pyproject.toml`, runs the suite, builds the
   wheel and sdist, installs the wheel into a clean environment, and attaches
   the files and `SHA256SUMS.txt` to a **draft** GitHub release.
3. Paste the release notes into the draft and publish it. Publishing runs
   `release.yml`, which rebuilds and uploads to PyPI by trusted publishing.
4. State in the notes which board and firmware build the release was verified
   on (`probe_firmware_returns.py` and `pytest -m hardware` on that unit).

A breaking change (a call returns something different, a default changes, a
command is refused that used to be sent) is a major version. Add it to the
README's "Upgrading" table with the 3.x behaviour, the new behaviour and what
to change.

## Commit and PR conventions

- Keep PRs focused; one logical change per PR is easiest to review.
- Reference the issue the PR closes (`Closes #123`).
- Describe what you tested, and whether it was tested against a real device
  (which model and firmware) or the mocked fixtures only.
- New public methods need a README entry in the command reference and, ideally,
  a runnable example under `examples/`.

## License

By contributing, you agree that your contributions are licensed under the
project's **GPL-2.0** license.
