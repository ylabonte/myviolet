"""Tests for myviolet.models.system_states."""

from __future__ import annotations

from datetime import UTC, datetime

from myviolet.enums import PvSurplusState, SimpleOnOff
from myviolet.models.system_states import (
    BackwashStatus,
    BathingAi,
    OverflowState,
    PvSurplus,
)


def test_overflow_state(get_readings_seed: dict) -> None:
    ovf = OverflowState.from_raw(get_readings_seed)
    assert ovf is not None
    assert ovf.dryrun is SimpleOnOff.OFF
    assert ovf.overfill is SimpleOnOff.OFF
    assert ovf.refill is SimpleOnOff.OFF


def test_overflow_state_missing() -> None:
    assert OverflowState.from_raw({}) is None


def test_backwash_status(get_readings_seed: dict) -> None:
    status = BackwashStatus.from_raw(get_readings_seed)
    assert status is not None
    assert status.delay_running is False
    assert status.delay_started_at is None  # timestamp == 0
    assert status.last_auto_run is not None
    assert status.last_auto_run.tzinfo is UTC
    assert status.raw_state == "NEXT_BW_IN 6 BW_DAY5"
    assert status.step == 0


def test_backwash_status_missing() -> None:
    assert BackwashStatus.from_raw({}) is None


def test_bathing_ai(get_readings_seed: dict) -> None:
    ai = BathingAi.from_raw(get_readings_seed)
    assert ai is not None
    assert ai.surveillance_state == "TRIGGERED"
    assert ai.pump_state is SimpleOnOff.OFF
    assert ai.start_level == 57.9
    assert ai.last_level == 57.9
    assert ai.pump_started_at == datetime.fromtimestamp(1778500830.313, tz=UTC)


def test_bathing_ai_missing() -> None:
    assert BathingAi.from_raw({}) is None


def test_pv_surplus_off(get_readings_seed: dict) -> None:
    pv = PvSurplus.from_raw(get_readings_seed)
    assert pv is not None
    assert pv.state is PvSurplusState.OFF


def test_pv_surplus_missing() -> None:
    assert PvSurplus.from_raw({}) is None


# ---- Forward-compatibility: unknown firmware enum values ---------------------


def test_overflow_state_unknown_value_returns_none() -> None:
    """An unknown SimpleOnOff value drops the snapshot rather than crashing."""
    raw = {
        "OVERFLOW_DRYRUN_STATE": "FUTURE_STATE",
        "OVERFLOW_OVERFILL_STATE": "OFF",
        "OVERFLOW_REFILL_STATE": "OFF",
    }
    assert OverflowState.from_raw(raw) is None


def test_backwash_status_unknown_delay_running_defaults_false() -> None:
    raw = {
        "BACKWASH_STATE": "IDLE",
        "BACKWASH_DELAY_RUNNING": "FUTURE_VALUE",
    }
    status = BackwashStatus.from_raw(raw)
    assert status is not None
    assert status.delay_running is False


def test_backwash_status_unknown_omni_moving_returns_none() -> None:
    raw = {
        "BACKWASH_STATE": "IDLE",
        "BACKWASH_OMNI_MOVING": "FUTURE_VALUE",
    }
    status = BackwashStatus.from_raw(raw)
    assert status is not None
    assert status.omni_moving is None


def test_bathing_ai_unknown_pump_state_returns_none() -> None:
    raw = {
        "BATHING_AI_SURVEILLANCE_STATE": "TRIGGERED",
        "BATHING_AI_PUMP_STATE": "FUTURE_STATE",
    }
    ai = BathingAi.from_raw(raw)
    assert ai is not None
    assert ai.pump_state is None
    assert ai.surveillance_state == "TRIGGERED"


def test_pv_surplus_unknown_value_returns_none() -> None:
    assert PvSurplus.from_raw({"PVSURPLUS": 99}) is None
