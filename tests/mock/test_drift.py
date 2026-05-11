"""Tests for tools.myviolet_mock.drift."""

from __future__ import annotations

from tools.myviolet_mock.drift import apply_drift


def test_drift_modifies_ph() -> None:
    snap = {"pH_value": 7.3, "pH_value_min": 7.0, "pH_value_max": 7.5}
    drifted = apply_drift(snap.copy(), elapsed_seconds=0.0)
    assert "pH_value" in drifted
    # Drift should produce a value reasonably close to seed
    assert abs(drifted["pH_value"] - 7.3) < 0.5


def test_drift_does_not_modify_constants() -> None:
    snap = {
        "pH_value": 7.3,
        "PUMP": 1,
        "COVER_STATE": "OPEN",
        "SW_VERSION": "1.1.9",
    }
    drifted = apply_drift(snap.copy(), elapsed_seconds=10.0)
    # Non-sensor keys must not be touched
    assert drifted["PUMP"] == 1
    assert drifted["COVER_STATE"] == "OPEN"
    assert drifted["SW_VERSION"] == "1.1.9"


def test_drift_is_deterministic() -> None:
    """Two snapshots drifted from the same baseline + elapsed should match."""
    snap1 = {"pH_value": 7.3, "orp_value": 700.0}
    snap2 = {"pH_value": 7.3, "orp_value": 700.0}
    d1 = apply_drift(snap1, elapsed_seconds=42.0)
    d2 = apply_drift(snap2, elapsed_seconds=42.0)
    assert d1["pH_value"] == d2["pH_value"]
    assert d1["orp_value"] == d2["orp_value"]
