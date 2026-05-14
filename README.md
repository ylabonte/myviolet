# myviolet — Python client for the Pooldigital Violet pool controller

[![Lint](https://github.com/ylabonte/myviolet/actions/workflows/lint.yml/badge.svg)](https://github.com/ylabonte/myviolet/actions/workflows/lint.yml)
[![Test](https://github.com/ylabonte/myviolet/actions/workflows/test.yml/badge.svg)](https://github.com/ylabonte/myviolet/actions/workflows/test.yml)
[![CodeQL](https://github.com/ylabonte/myviolet/actions/workflows/codeql.yml/badge.svg)](https://github.com/ylabonte/myviolet/actions/workflows/codeql.yml)
[![Documentation](https://github.com/ylabonte/myviolet/actions/workflows/docs.yml/badge.svg)](https://ylabonte.github.io/myviolet/)
[![PyPI Package release](https://github.com/ylabonte/myviolet/actions/workflows/python-publish.yml/badge.svg)](https://github.com/ylabonte/myviolet/actions/workflows/python-publish.yml)

[![PyPI](https://img.shields.io/pypi/v/myviolet?label=Current%20Release)](https://pypi.org/project/myviolet/)
[![Python Versions](https://img.shields.io/pypi/pyversions/myviolet)](https://pypi.org/project/myviolet/)

Async Python library for the [Pooldigital Violet pool controller](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/) — the successor to the ProCon.IP unit ([sister library: `proconip`](https://github.com/ylabonte/proconip-pypi)). Primarily intended as the foundation for a Home Assistant integration, but usable on its own for any Python application that talks to the controller.

- **Documentation**: <https://ylabonte.github.io/myviolet/>
- **Live demo controller** (vendor-owned): <https://demo.myviolet.de/getReadings?ALL>
- **Pooldigital community forum** (DE) — links to manuals, demo system, and discussions: <https://www.poolsteuerung.de/>

## Requirements

- Python ≥ 3.13
- `aiohttp >= 3.10, < 4`
- `yarl >= 1.23.0, < 2`

The `aiohttp` lower bound is set wide enough to cover older Home Assistant
Core deployments; `yarl` matches the HA Core 2026.5 pin.

## Install

```bash
pip install myviolet
```

## Usage

### Reading state

```python
import asyncio
import aiohttp
from myviolet import VioletClient

async def main() -> None:
    async with aiohttp.ClientSession() as session:
        async with VioletClient(
            session,
            host="violet.local",
            username="admin",
            password="...",
        ) as client:
            snapshot = await client.readings.get()
            if snapshot.water_chemistry.ph is not None:
                print(f"pH:  {snapshot.water_chemistry.ph.value}")
            if snapshot.water_chemistry.orp is not None:
                print(f"ORP: {snapshot.water_chemistry.orp.value} mV")
            if snapshot.pump is not None and snapshot.pump.state.is_on:
                print(f"Pump running for {snapshot.pump.runtime}")

asyncio.run(main())
```

### Control

```python
async with VioletClient(session, host="violet.local", username="admin", password="...") as client:
    await client.control.pump("ON", speed=2)
    await client.control.heater("AUTO")
    await client.control.dosing("CL", "ON", duration=60)
    await client.targets.set_ph(7.2)                 # validates 6.8-7.8 range
    await client.control.cover_open(acknowledge_unsafe=True)
```

Cover movement is gated behind a mandatory `acknowledge_unsafe=True` keyword
because the vendor disallows fully-automated cover control (people / debris
in the pool). Callers are expected to add their own safety logic.

## The Violet API at a glance

- Pure JSON over HTTP, HTTP Basic auth, no WebSocket / SSE — polling.
- Reads: `GET /getReadings?ALL,DOSAGE,RUNTIMES` returns ~400 keys.
- Writes: `GET /setFunctionManually?<KEY>,<ACTION>,<DURATION>,<VALUE>`,
  `GET /setTargetValues?...`, `POST /setConfig`, `POST /setDosingParameters`.
- ~200 documented fields are exposed via typed views (with shared enums for
  `OutputState`, `CoverState`, etc.); the remaining ~200 firmware-specific
  keys remain accessible via `snapshot.raw[...]`.

## Disclaimer

I have nothing to do with the development, selling, marketing, or support of
the Violet pool controller itself. This library is a community project
intended to make the controller easier to integrate with Home Assistant and
other Python-based automations.

## License

MIT — see [LICENSE](LICENSE).
