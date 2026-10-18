<!-- Thanks for contributing to tinySA_python. Keep PRs focused: one logical change. -->

## Summary

<!-- What does this change and why? Link the issue it closes. -->
Closes #

## Type of change

- [ ] Bug fix
- [ ] New command / feature
- [ ] Docs / examples
- [ ] Test / CI / tooling
- [ ] Refactor (no behavior change)

## How it was tested

Run from the `tsapython/` directory:

- [ ] `uv run pytest` passes (hardware tests self-skip without a device)
- [ ] `uv run ruff check .` passes
- [ ] `uv run mypy` passes (new code under `src/tsapython/` is fully annotated)
- [ ] Tested against a **real device**: `uv run pytest -m hardware` — paste the pytest tail below
- [ ] Touches the signal generator: `TSAPYTHON_OUTPUT_OK=1 uv run pytest -m hardware_output` with a load on the RF port
- [ ] Mocked fixtures only (no device) — fine for docs, tests and tooling; core changes need the hardware line above

<!-- If real hardware: board (ZS304 / ZS405 / ZS406 / ZS407) and firmware build, from version() / info() -->

## Checklist for new/changed commands

- [ ] Device writes go through `tinySA_serial()` (no direct `self.ser` access from command methods)
- [ ] Gated on the device profile where the command, an argument word or a range differs by model (`_check_command`, `_check_word`, `self.profile.*`) — see "Adding a command" in CONTRIBUTING.md
- [ ] Any attribute a mixin needs from `core.py` is declared in `_host.py`
- [ ] Command-construction test asserting the exact command string via the `tsa` fixture
- [ ] Validation-error test asserting **nothing is sent** on bad input
- [ ] Response parsing (if any) tested with the `parsing_tsa` fixture, ideally against bytes captured from a device (`tests/collect_samples.py`)
- [ ] README command reference updated (and the "Commands added" table if the command needs a minimum firmware build); example under `examples/` if it's a significant public method
- [ ] CHANGELOG entry under the unreleased version

## Notes for reviewers

<!-- Anything tricky, follow-ups intentionally left out, etc. -->
