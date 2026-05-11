"""Tests for myviolet.models.dosing."""

from __future__ import annotations

from datetime import timedelta

from myviolet.enums import OutputState
from myviolet.models.dosing import DosingChannel, collect_dosing_channels


def test_collect_documented_channels(get_readings_seed: dict) -> None:
    channels = collect_dosing_channels(get_readings_seed)
    # All six configured channels should be present in the live demo
    assert set(channels.keys()) == {"CL", "ELO", "ELO_REV", "PHM", "PHP", "FLOC"}


def test_cl_channel_state(get_readings_seed: dict) -> None:
    channels = collect_dosing_channels(get_readings_seed)
    cl = channels["CL"]
    assert isinstance(cl, DosingChannel)
    assert cl.code == "CL"
    assert cl.channel_number == 1
    assert cl.state is OutputState.AUTO_OFF
    assert cl.runtime == timedelta(minutes=7, seconds=54)
    assert cl.daily_amount_ml is None  # not in this fixture


def test_phm_channel_state(get_readings_seed: dict) -> None:
    channels = collect_dosing_channels(get_readings_seed)
    phm = channels["PHM"]
    assert phm.channel_number == 4
    assert phm.runtime == timedelta(minutes=25, seconds=16)


def test_with_dosage_fields() -> None:
    """A channel with all DOSAGE fields populated should expose them."""
    raw = {
        "DOS_1_CL": 1,
        "DOS_1_CL_LAST_ON": 1778500800,
        "DOS_1_CL_LAST_OFF": 0,
        "DOS_1_CL_RUNTIME": "00h 05m 30s",
        "DOS_1_CL_DAILY_DOSING_AMOUNT_ML": 120,
        "DOS_1_CL_TOTAL_CAN_AMOUNT_ML": 4500,
        "DOS_1_CL_LAST_CAN_RESET": 1778000000000,
        "DOS_1_CL_USE": 1,
        "DOS_1_CL_TYPE": 1,
        "DOS_1_CL_STATE": ["BLOCKED_BY_PUMP_OFF"],
    }
    channels = collect_dosing_channels(raw)
    cl = channels["CL"]
    assert cl.daily_amount_ml == 120
    assert cl.total_can_amount_ml == 4500
    assert cl.last_can_reset is not None
    assert cl.enabled is True
    assert cl.state_blocks == ["BLOCKED_BY_PUMP_OFF"]


def test_missing_channel_omitted() -> None:
    channels = collect_dosing_channels({})
    assert channels == {}


def test_unknown_output_state_skips_channel() -> None:
    """Forward-compat: an unknown firmware state on a channel drops just that channel."""
    raw = {
        "DOS_1_CL": 99,  # unknown firmware OutputState
        "DOS_1_CL_RUNTIME": "00h 00m 00s",
        "DOS_4_PHM": 0,
        "DOS_4_PHM_RUNTIME": "00h 00m 00s",
    }
    channels = collect_dosing_channels(raw)
    assert "CL" not in channels
    assert "PHM" in channels


def test_unknown_dosing_type_surfaces_as_none() -> None:
    """Forward-compat: an unknown DosingType value should not crash collection."""
    raw = {
        "DOS_1_CL": 0,
        "DOS_1_CL_RUNTIME": "00h 00m 00s",
        "DOS_1_CL_TYPE": 99,  # unknown firmware DosingType
    }
    channels = collect_dosing_channels(raw)
    assert channels["CL"].type is None
