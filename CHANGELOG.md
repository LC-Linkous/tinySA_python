# Changelog

All notable changes to tinySA_python / `tsapython` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
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
