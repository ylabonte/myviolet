"""In-memory mutable state for the myviolet mock controller.

Reads return a snapshot of the mock state (with optional sensor drift applied
by the route handler). Writes mutate the state so subsequent reads observe
the change — letting integration tests assert true round-trip semantics.
"""

from __future__ import annotations

import time
from typing import Any

from myviolet.constants import DOSING_CHANNELS, UNSAFE_COVER_KEYS
from myviolet.enums import CoverState, OutputState

_ACTION_TO_STATE: dict[str, OutputState] = {
    "ON": OutputState.MANUAL_ON,
    "OFF": OutputState.MANUAL_OFF,
    "AUTO": OutputState.AUTO_OFF,
}


class MockState:
    """Mutable snapshot of a Violet controller.

    Seeded from a captured `/getReadings?ALL,DOSAGE,RUNTIMES` JSON dict.
    Holds an in-memory dict and exposes operations matching the controller's
    write endpoints. The route handler is responsible for sensor drift; the
    state object only tracks deliberate mutations.
    """

    def __init__(self, seed: dict[str, Any]) -> None:
        self._snapshot: dict[str, Any] = dict(seed)
        self._config: dict[str, Any] = {}
        self._dosing_parameters: dict[str, Any] = {}
        self._epoch_start = time.time()

    def snapshot(self) -> dict[str, Any]:
        """Return a shallow copy of the current readings snapshot."""
        return dict(self._snapshot)

    def config_snapshot(self) -> dict[str, Any]:
        return dict(self._config)

    def dosing_parameters_snapshot(self) -> dict[str, Any]:
        return dict(self._dosing_parameters)

    @property
    def epoch_start(self) -> float:
        return self._epoch_start

    def apply_set_function(self, key: str, action: str, duration: int, value: int) -> None:
        """Apply a `/setFunctionManually` write to the in-memory state.

        Maps the action to an `OutputState` and updates the canonical state
        field. Unknown keys raise `KeyError` (the real controller would
        respond with an error too).
        """
        if key in UNSAFE_COVER_KEYS or key == "COVER_STOP":
            self._apply_cover_action(key)
            return

        if key.startswith("DMX_SCENE"):
            self._apply_dmx_action(key, action)
            return

        if key not in self._snapshot:
            # Allow keys we haven't seeded if they look like a valid output
            valid_prefixes = (
                "PUMP",
                "HEATER",
                "SOLAR",
                "LIGHT",
                "REFILL",
                "ECO",
                "BACKWASH",
                "EXT1_",
                "EXT2_",
                "DOS_",
                "PVSURPLUS",
            )
            if not key.startswith(valid_prefixes):
                raise KeyError(f"unknown control key: {key}")

        if action not in _ACTION_TO_STATE:
            # Unhandled action (e.g., PUSH, COLOR) — leave state untouched
            return

        new_state = _ACTION_TO_STATE[action]
        now = int(time.time())
        self._snapshot[key] = int(new_state)
        if new_state.is_on:
            self._snapshot[f"{key}_LAST_ON"] = now
        else:
            self._snapshot[f"{key}_LAST_OFF"] = now

    def _apply_cover_action(self, key: str) -> None:
        mapping = {
            "COVER_OPEN": CoverState.OPENING,
            "COVER_CLOSE": CoverState.CLOSING,
            "COVER_STOP": CoverState.STOPPED,
        }
        self._snapshot["COVER_STATE"] = mapping[key].value

    def _apply_dmx_action(self, key: str, action: str) -> None:
        mapping = {"ON": 4, "OFF": 6, "AUTO": 0}
        if action in mapping:
            self._snapshot[key] = mapping[action]

    def apply_set_target(self, target: str, value: float) -> None:
        """Apply a `/setTargetValues` write. Stores it as `<target>_target` for inspection."""
        self._snapshot[f"{target}_target"] = value

    def apply_set_config(self, payload: dict[str, Any]) -> None:
        """Merge a new config payload into the in-memory config snapshot."""
        self._config.update(payload)

    def apply_set_dosing_parameters(self, payload: dict[str, Any]) -> None:
        self._dosing_parameters.update(payload)


# Re-export for completeness
__all__ = ["DOSING_CHANNELS", "MockState"]
