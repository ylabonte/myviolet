"""Tests for myviolet.models.dmx."""

from __future__ import annotations

from myviolet.enums import DmxSceneState
from myviolet.models.dmx import DmxScene, collect_dmx_scenes


def test_collect_all_12(get_readings_seed: dict) -> None:
    scenes = collect_dmx_scenes(get_readings_seed)
    assert len(scenes) == 12
    assert all(isinstance(s, DmxScene) for s in scenes.values())


def test_scene_1_manual_off(get_readings_seed: dict) -> None:
    """Demo controller has DMX_SCENE1 = 6 (MANUAL_OFF)."""
    scenes = collect_dmx_scenes(get_readings_seed)
    assert scenes[1].state is DmxSceneState.MANUAL_OFF


def test_unknown_state_value_skipped() -> None:
    """Values not in the DmxSceneState enum (e.g. 2, 3, 5) are dropped."""
    raw = {"DMX_SCENE1": 2}
    scenes = collect_dmx_scenes(raw)
    assert scenes == {}
