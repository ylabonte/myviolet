"""Tests for myviolet.validators."""

from __future__ import annotations

import pytest

from myviolet.exceptions import SetpointValidationError
from myviolet.validators import validate_setpoint


class TestValidateSetpoint:
    @pytest.mark.parametrize(
        ("field", "value"),
        [("pH", 6.8), ("pH", 7.2), ("pH", 7.8), ("ORP", 700)],
    )
    def test_within_range_returns_silently(self, field: str, value: float) -> None:
        validate_setpoint(field, value)

    def test_below_range_raises(self) -> None:
        with pytest.raises(SetpointValidationError) as excinfo:
            validate_setpoint("pH", 6.5)
        assert excinfo.value.field == "pH"
        assert excinfo.value.value == 6.5
        assert excinfo.value.low == 6.8
        assert excinfo.value.high == 7.8

    def test_above_range_raises(self) -> None:
        with pytest.raises(SetpointValidationError):
            validate_setpoint("ORP", 900)

    def test_unknown_field_raises_value_error(self) -> None:
        with pytest.raises(ValueError, match="unknown setpoint"):
            validate_setpoint("not_a_field", 1.0)
