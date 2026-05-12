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

    Forward-compat: a rule whose ``state`` is an unknown firmware value is
    skipped (the rest of the rules still parse); a non-numeric stopwatch
    degrades to ``remaining = None`` rather than crashing.
    """
    result: dict[int, SwitchingRule] = {}
    for index in range(1, 8):
        state_key = f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_{index}"
        stopwatch_key = f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH{index}"
        state_raw = raw.get(state_key)
        if state_raw is None:
            continue
        try:
            state = RuleState(int(state_raw))
        except (ValueError, TypeError):
            continue
        stopwatch_raw = raw.get(stopwatch_key)
        remaining: timedelta | None = None
        if stopwatch_raw is not None:
            try:
                stopwatch_seconds = float(stopwatch_raw)
            except (ValueError, TypeError):
                stopwatch_seconds = -1.0  # treat as "timer is up"
            if stopwatch_seconds >= 0:
                remaining = timedelta(seconds=stopwatch_seconds)
        result[index] = SwitchingRule(index=index, state=state, remaining=remaining)
    return result
