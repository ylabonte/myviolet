"""Tests for myviolet.exceptions."""

from __future__ import annotations

import pytest

from myviolet.exceptions import (
    BadCredentialsException,
    BadStatusCodeException,
    InvalidPayloadException,
    SetpointValidationError,
    TimeoutException,
    UnsafeOperationException,
    VioletApiException,
)


class TestBaseHierarchy:
    @pytest.mark.parametrize(
        "subclass",
        [
            BadCredentialsException,
            BadStatusCodeException,
            TimeoutException,
            InvalidPayloadException,
            UnsafeOperationException,
            SetpointValidationError,
        ],
    )
    def test_subclass_of_base(self, subclass: type[Exception]) -> None:
        assert issubclass(subclass, VioletApiException)


class TestBadCredentialsException:
    def test_carries_status_code(self) -> None:
        exc = BadCredentialsException(401)
        assert exc.status_code == 401
        assert "401" in str(exc)


class TestBadStatusCodeException:
    def test_carries_status_code(self) -> None:
        exc = BadStatusCodeException(500, "internal server error")
        assert exc.status_code == 500
        assert "500" in str(exc)


class TestSetpointValidationError:
    def test_is_also_value_error(self) -> None:
        """Callers should be able to catch ValueError generically."""
        assert issubclass(SetpointValidationError, ValueError)

    def test_message_includes_field_and_bounds(self) -> None:
        with pytest.raises(SetpointValidationError) as excinfo:
            raise SetpointValidationError("pH", 8.5, 6.8, 7.8)
        msg = str(excinfo.value)
        assert "pH" in msg
        assert "8.5" in msg
        assert "6.8" in msg
        assert "7.8" in msg


class TestUnsafeOperationException:
    def test_carries_operation_name(self) -> None:
        exc = UnsafeOperationException("cover_open")
        assert "cover_open" in str(exc)
        assert "acknowledge_unsafe" in str(exc)
