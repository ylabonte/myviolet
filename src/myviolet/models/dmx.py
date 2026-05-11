"""DMX scene typed views (12 scenes total)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from ..enums import DmxSceneState


@dataclass(frozen=True, slots=True)
class DmxScene:
    """One DMX scene (12 documented). The subset enum forbids priority states."""

    index: int
    state: DmxSceneState


def collect_dmx_scenes(raw: dict[str, Any]) -> dict[int, DmxScene]:
    """Return DMX scenes keyed by index (1-12), present-only.

    Values outside the documented subset (0, 1, 4, 6) are silently dropped —
    the controller does not produce them today, but we'd rather skip than
    crash if a future firmware introduces a new state we don't know.
    """
    result: dict[int, DmxScene] = {}
    for index in range(1, 13):
        state_raw = raw.get(f"DMX_SCENE{index}")
        if state_raw is None:
            continue
        try:
            state = DmxSceneState(int(state_raw))
        except ValueError:
            continue
        result[index] = DmxScene(index=index, state=state)
    return result
