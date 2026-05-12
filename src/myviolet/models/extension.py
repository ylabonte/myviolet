"""Extension-relay typed views (buses 1 and 2)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any

from ..enums import OutputState
from ._common import OutputBase


@dataclass(frozen=True, slots=True)
class ExtensionRelay:
    """One relay on a relay-extension board. Bus 1 is documented; bus 2 is observed."""

    bus: int
    index: int
    state: OutputState
    last_on: datetime | None
    last_off: datetime | None
    runtime: timedelta


def collect_extension_relays(raw: dict[str, Any]) -> dict[int, dict[int, ExtensionRelay]]:
    """Collect relays from both buses, keyed by ``{bus: {index: ExtensionRelay}}``.

    Only buses with at least one relay present are included.
    """
    result: dict[int, dict[int, ExtensionRelay]] = {}
    for bus in (1, 2):
        bus_relays: dict[int, ExtensionRelay] = {}
        for index in range(1, 9):
            key = f"EXT{bus}_{index}"
            base = OutputBase.from_raw(raw, key)
            if base is None:
                continue
            bus_relays[index] = ExtensionRelay(
                bus=bus,
                index=index,
                state=base.state,
                last_on=base.last_on,
                last_off=base.last_off,
                runtime=base.runtime,
            )
        if bus_relays:
            result[bus] = bus_relays
    return result
