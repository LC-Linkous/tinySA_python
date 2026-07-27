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

- [ ] `uv run pytest -m "not hardware"` passes locally (from the `tsapython/` directory)
- [ ] `uv run ruff check .` passes
- [ ] Tested against a **real device** (describe below)
- [ ] Tested with the **mocked fixtures only** (no device)

<!-- If real hardware: which model (Basic / Ultra / Ultra+) and firmware version (from info())? -->

## Checklist for new/changed commands

- [ ] Device writes go through `tinySA_serial()` (no direct `self.ser` access from command methods)
- [ ] Added a command-construction test asserting the exact command string via the `recorder` fixture
- [ ] Added a validation-error test asserting **nothing is sent** on bad input
- [ ] Response parsing (if any) is tested with the `fake_port` fixture, ideally against captured device bytes
- [ ] README command reference updated; example added under `examples/` if it's a significant public method

## Notes for reviewers

<!-- Anything tricky, follow-ups intentionally left out, etc. -->
