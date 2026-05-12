# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
