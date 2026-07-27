# Changelog

All notable changes to tinySA_python / `tsapython` are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Continuous integration: GitHub Actions workflow running the hardware-free
  test suite across Windows, Linux, and macOS on Python 3.10–3.13, plus a
  ruff lint job and a package build check, on every push and pull request.
- Committed `uv.lock` and a PEP 735 `dev` dependency group, making
  `uv sync` / `uv run pytest` the blessed development workflow (the previous
  README warning against `uv run pytest` no longer applies).
- Ruff configuration in `pyproject.toml`. The blocking ruleset is deliberately
  small (E9 syntax errors + F pyflakes); style rules are a planned follow-up.
- Community health files: `CONTRIBUTING.md`, `CODE_OF_CONDUCT.md`,
  `SECURITY.md`, `CHANGELOG.md`, issue templates, and a pull request template.

### Fixed
- README no longer references `requirements.txt` / `test_requirements.txt`,
  which were removed from the repository in the 3.0.0 packaging restructure;
  install instructions now go through the `pyproject.toml` extras.
- README repository-structure diagrams updated to match the actual tree
  (added `examples/filtering_scan_artifacts.py`, `examples/find_peaks.py`,
  and `tests/diagnose_reset.py`; removed the requirements files).
- Removed unused imports and dead local variables flagged by lint
  (`core.py`, `_commands/system_info.py`, `_commands/output_signal.py`,
  tests, and examples). No behavior change.
- Removed `examples/__init__.py` — the examples directory is a collection of
  runnable scripts, not a package.
- Merged two near-duplicate README sections documenting
  `tests/collect_samples.py`.

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
