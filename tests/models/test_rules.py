"""Tests for myviolet.models.rules."""

from __future__ import annotations

from datetime import timedelta

from myviolet.enums import RuleState
from myviolet.models.rules import SwitchingRule, collect_switching_rules


def test_collect_all_7_when_present() -> None:
    raw = {}
    for i in range(1, 8):
        raw[f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_{i}"] = 0
        raw[f"DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH{i}"] = -1.0
    rules = collect_switching_rules(raw)
    assert len(rules) == 7
    assert all(isinstance(r, SwitchingRule) for r in rules.values())


def test_active_rule_with_remaining_time() -> None:
    raw = {
        "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1": 1,
        "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1": 42.5,
    }
    rules = collect_switching_rules(raw)
    assert rules[1].state is RuleState.ACTIVE
    assert rules[1].remaining == timedelta(seconds=42.5)


def test_negative_stopwatch_is_none() -> None:
    """Negative stopwatch values mean the timer is up (no remaining time)."""
    raw = {
        "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_1": 0,
        "DIGITALINPUTRULE_STATE_DIGITALINPUT_RULE_STOPWATCH1": -1.0,
    }
    rules = collect_switching_rules(raw)
    assert rules[1].remaining is None
