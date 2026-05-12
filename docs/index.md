# myviolet

Async Python library for the [Pooldigital Violet pool controller](https://www.pooldigital.de/poolsteuerungen/violet-poolsteuerung/).
Primarily intended as the foundation for a Home Assistant integration, but
useful on its own for any Python application that needs to talk to the
controller.

## Install

```bash
pip install myviolet
```

Requires Python 3.13+. The runtime dependencies (`aiohttp`, `yarl`) are
declared with version ranges that match the Home Assistant Core 2026.5 pins,
so installing `myviolet` alongside Home Assistant Core should not produce
resolver conflicts.

## Quickstart

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

See the [API Reference](api.md) for the full surface, including control
methods, setpoints, dosing, and DMX scenes.

## Project layout

- **API Reference** — auto-generated from the source via mkdocstrings.
- **Changelog** — what changed in each release.
- **Contributing** — how to set up a local dev environment.

The source lives at <https://github.com/ylabonte/myviolet>; PyPI page at
<https://pypi.org/project/myviolet/>.
