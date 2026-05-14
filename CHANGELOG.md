# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Changed

- **Loosened `yarl` pin from `>=1.23.0,<2` to `>=1.17,<2`** for older Home Assistant Core compatibility (PR #8, merged after v0.1.1 shipped). Pairs with the same-cycle aiohttp loosen recorded in 0.1.1 below.

### Fixed

- README's `## Requirements` section was stale — still claimed `aiohttp >=3.13.5` and `yarl >=1.23.0`. Updated to match the actual pins in `pyproject.toml` (`aiohttp >=3.10,<4`, `yarl >=1.17,<2`).

## [0.1.1] - 2026-05-14

### Changed

- **Loosened `aiohttp` pin from `>=3.13.5,<4` to `>=3.10,<4`.** Lets the library install into Home Assistant Core environments that still ship an older aiohttp than the most recent release. `yarl >=1.23.0,<2` unchanged.
- **Development dependencies moved from `[project.optional-dependencies]` to `[dependency-groups]`** (PEP 735). The `dev`, `test`, and `docs` groups were never user-facing extras; they're for working *on* the package, not *with* it. They no longer appear as `Provides-Extra:` on PyPI. Local install: `pip install -e . --group dev --group test --group docs` (requires pip ≥ 25.1). CI workflows (`test.yml`, `lint.yml`, `docs.yml`) and `CONTRIBUTING.md` updated accordingly.
- **License changed from Apache-2.0 to MIT.** The `LICENSE` file now contains the canonical MIT License text; `pyproject.toml`'s SPDX expression (`license = "MIT"`) and Trove classifier (`"License :: OSI Approved :: MIT License"`) updated to match. v0.1.0 on PyPI stays as Apache-2.0 (published releases are immutable); from 0.1.1 onwards the package ships as MIT. Downstream consumers should review the new license terms before upgrading.

## [0.1.0] - 2026-05-12

### Added

- Initial scaffold based on the `proconip-pypi` stack: hatchling+hatch-vcs
  build, ruff/mypy strict tooling, mkdocs-material docs site, devcontainer,
  CI workflows (lint, test, codeql, docs, automerge, release-drafter,
  PyPI Trusted Publishing).
- Apache-2.0 license (chosen for Home Assistant Core compatibility).
- Async `VioletClient` targeting the Pooldigital Violet pool controller API.
- Typed view layer (~200 documented fields) over the raw `/getReadings`
  JSON response, with shared enums (`OutputState`, `CoverState`,
  `OnewireState`, `DmxSceneState`, `RuleState`, `SimpleOnOff`, `YesNo`,
  `DosingType`, `PvSurplusState`).
- Setpoint validators with vendor-documented ranges.
- Cover control guarded by mandatory `acknowledge_unsafe=True` opt-in.
- Stateful aiohttp mock service in `tools/myviolet_mock/`.
- Test + coverage summary rendered to the GitHub Actions step summary
  via `.github/scripts/summarize_tests.py`.

[Unreleased]: https://github.com/ylabonte/myviolet/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/ylabonte/myviolet/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/ylabonte/myviolet/releases/tag/v0.1.0
