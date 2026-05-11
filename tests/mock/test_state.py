"""Tests for tools.myviolet_mock.state."""

from __future__ import annotations

from tools.myviolet_mock.state import MockState


def _seed_snapshot() -> dict:
    return {
        "PUMP": 0,
        "PUMP_LAST_ON": 0,
        "PUMP_LAST_OFF": 0,
        "PUMP_RUNTIME": "00h 00m 00s",
        "HEATER": 0,
        "DMX_SCENE1": 0,
        "DOS_1_CL": 0,
        "EXT1_3": 0,
        "pH_value": 7.3,
        "pH_value_min": 7.0,
        "pH_value_max": 7.5,
    }


def test_initial_snapshot_matches_seed() -> None:
    seed = _seed_snapshot()
    state = MockState(seed)
    assert state.snapshot()["PUMP"] == 0


def test_apply_set_function_pump_on() -> None:
    state = MockState(_seed_snapshot())
    state.apply_set_function("PUMP", "ON", 0, 0)
    snap = state.snapshot()
    assert snap["PUMP"] == 4  # OutputState.MANUAL_ON


def test_apply_set_function_pump_off() -> None:
    state = MockState(_seed_snapshot())
    state.apply_set_function("PUMP", "OFF", 0, 0)
    assert state.snapshot()["PUMP"] == 6  # OutputState.MANUAL_OFF


def test_apply_set_function_pump_auto() -> None:
    state = MockState(_seed_snapshot())
    state.apply_set_function("PUMP", "ON", 0, 0)
    state.apply_set_function("PUMP", "AUTO", 0, 0)
    assert state.snapshot()["PUMP"] == 0  # OutputState.AUTO_OFF


def test_apply_set_function_unknown_key_raises() -> None:
    state = MockState(_seed_snapshot())
    try:
        state.apply_set_function("FOO_BAR_BAZ", "ON", 0, 0)
    except KeyError:
        pass
    else:
        raise AssertionError("expected KeyError for unknown control key")


def test_apply_set_target_value_pH() -> None:
    state = MockState(_seed_snapshot())
    state.apply_set_target("pH", 7.2)
    assert state.snapshot()["pH_target"] == 7.2


def test_apply_set_config_merges() -> None:
    state = MockState(_seed_snapshot())
    state.apply_set_config({"newSetting": 42})
    assert state.config_snapshot()["newSetting"] == 42
