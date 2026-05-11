"""Exception hierarchy for the myviolet client.

All exceptions raised by the client (transport-level HTTP errors, payload
problems, validation failures, deliberate safety guards) subclass
`VioletApiException` so callers can catch the entire library's failure modes
with a single blanket clause, or narrow to a specific subclass when needed.
"""

from __future__ import annotations


class VioletApiException(Exception):
    """Base for every error raised by the myviolet client."""


class BadCredentialsException(VioletApiException):
    """The controller rejected the supplied credentials (HTTP 401 or 403)."""

    def __init__(self, status_code: int) -> None:
        self.status_code = status_code
        super().__init__(f"authentication failed (HTTP {status_code})")


class BadStatusCodeException(VioletApiException):
    """The controller returned an unexpected non-auth error HTTP status."""

    def __init__(self, status_code: int, message: str = "") -> None:
        self.status_code = status_code
        suffix = f": {message}" if message else ""
        super().__init__(f"unexpected HTTP {status_code}{suffix}")


class TimeoutException(VioletApiException):
    """An HTTP request to the controller exceeded the configured timeout."""


class InvalidPayloadException(VioletApiException):
    """The controller's response was malformed, truncated, or unparseable."""


class UnsafeOperationException(VioletApiException):
    """A potentially unsafe operation was attempted without acknowledgment.

    Currently raised by cover open/close calls when the caller has not passed
    ``acknowledge_unsafe=True``.
    """

    def __init__(self, operation: str) -> None:
        super().__init__(
            f"{operation!r} is potentially unsafe; pass acknowledge_unsafe=True "
            f"to confirm the caller has implemented external safety logic"
        )


class SetpointValidationError(VioletApiException, ValueError):
    """A setpoint value was outside its documented valid range.

    Subclasses both `VioletApiException` (for blanket library catches) and
    `ValueError` (so generic input-validation code keeps working).
    """

    def __init__(self, field: str, value: float, low: float, high: float) -> None:
        self.field = field
        self.value = value
        self.low = low
        self.high = high
        super().__init__(f"{field} setpoint {value} is outside the valid range [{low}, {high}]")
