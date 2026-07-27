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
uv run ruff check .                 # lint (blocking ruleset: E9 + F)
```

CI runs the same suite across Windows, Linux, and macOS on Python 3.10–3.13,
plus the lint check and a package build check.

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
   use the `recorder` fixture to assert the exact command string the method
   builds (e.g. `"rbw 100\r\n"`) on the happy path, and assert that **nothing
   is sent** on the validation-error path.
4. If the command's *response* needs parsing, add a parsing test using the
   `fake_port` fixture against canned bytes — ideally frozen from real
   hardware via `tests/collect_samples.py` rather than hand-written.
5. Follow the existing input-validation pattern (accepted-values checks with
   `verbose` / `error_byte` behavior) so error handling stays consistent.

## Tests that touch hardware

Tests that need a real device are marked `@pytest.mark.hardware` and self-skip
when no tinySA is detected. Captured-response fixtures live in
`tests/fixtures/` and are frozen from real device output via
`tests/collect_samples.py` (read-only commands only). If you add a parser, add
a captured fixture rather than a hand-written one where possible, and note
which device model and firmware produced it.

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
