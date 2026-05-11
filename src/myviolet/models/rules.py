"""Switching-rule typed views (DIGITALINPUTRULE 1-7)."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from ..enums import RuleState


@dataclass(frozen=True, slots=True)
class SwitchingRule:
    """One digital-input switching rule plus its optional stopwatch remainder."""

    index: int
    state: RuleState
    remaining: timedelta | None = None


def collect_switching_rules(raw: dict[str, Any]) -> dict[int, SwitchingRule]:
    """Return rules keyed by index (1-7), present-only.

    The vendor encodes a negative stopwatch value as "runtime is up"; this
    parser maps that to ``remaining = None`` so callers can use truthiness.
    """
    result: dict[int, SwitchingRule] = {}
    for index in range(1, 8):
        state_key = f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_{index}"
        stopwatch_key = f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH{index}"
        state_raw = raw.get(state_key)
        if state_raw is None:
            continue
        stopwatch_raw = raw.get(stopwatch_key)
        remaining: timedelta | None = None
        if stopwatch_raw is not None and float(stopwatch_raw) >= 0:
            remaining = timedelta(seconds=float(stopwatch_raw))
        result[index] = SwitchingRule(
            index=index,
            state=RuleState(int(state_raw)),
            remaining=remaining,
        )
    return result
