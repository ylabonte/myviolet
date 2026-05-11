"""`VioletClient` — the public async client for the Violet pool controller.

The client is constructed once per controller and exposes domain-grouped
namespaces (`readings`, `control`, `targets`, `config`, `dosing`,
`calibration`, `history`). All namespaces share a single `VioletTransport`
instance, so retries / observability hooks can be added in one place.
"""

from __future__ import annotations

import re
from functools import cached_property
from types import TracebackType
from typing import Any

import aiohttp
from yarl import URL

from . import constants
from ._safe_auth import SafeBasicAuth
from .exceptions import UnsafeOperationException
from .readings import VioletReadings
from .transport import VioletTransport
from .validators import validate_setpoint

# Hostname (RFC 1123 simplified) or IPv4 literal, optional :port
_HOST_RE = re.compile(
    r"^(?:[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)"
    r"(?:\.[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?)*"
    r"(?::\d{1,5})?$"
)
_ALLOWED_SCHEMES = frozenset({"http", "https"})

# Control keys are uppercase identifiers; subscripts like `EXT1_3` use `_`.
_CONTROL_KEY_RE = re.compile(r"^[A-Z][A-Z0-9_]*$")


def _validate_control_key(key: str) -> str:
    if not isinstance(key, str) or not _CONTROL_KEY_RE.match(key):
        raise ValueError(f"invalid control key {key!r}; must match [A-Z][A-Z0-9_]*")
    return key


def _validate_control_action(action: str) -> str:
    if action not in constants.CONTROL_ACTIONS:
        raise ValueError(f"unknown action {action!r}; allowed: {sorted(constants.CONTROL_ACTIONS)}")
    return action


def _validate_host(host: str) -> tuple[str, int | None]:
    """Validate `host` and split it into ``(hostname, optional port)``.

    Rejects userinfo (``user@host``), paths/queries/fragments, whitespace,
    and control characters — accepting only a bare hostname or IPv4 literal,
    optionally followed by ``:port``. This guards against URL smuggling
    when `host` is sourced from a config-flow text field.
    """
    if not isinstance(host, str) or not host or not _HOST_RE.match(host):
        raise ValueError(f"invalid host: {host!r}")
    if ":" in host:
        hostname, _, port_str = host.rpartition(":")
        port = int(port_str)
        if not (0 < port < 65536):
            raise ValueError(f"port out of range: {port}")
        return hostname, port
    return host, None


def _validate_scheme(scheme: str) -> str:
    if scheme not in _ALLOWED_SCHEMES:
        raise ValueError(f"invalid scheme {scheme!r}; allowed: {sorted(_ALLOWED_SCHEMES)}")
    return scheme


class VioletClient:
    """Async client for one Violet controller.

    Args:
        session: A reusable `aiohttp.ClientSession`. The client does not own
            the session; the caller is responsible for closing it.
        host: Hostname or IP of the controller (e.g. ``"violet.local"`` or
            ``"violet.local:8080"``). Must be a bare hostname/IP with an
            optional ``:port`` suffix — userinfo, paths, queries, and other
            URL components are rejected to prevent URL smuggling.
        username: Optional. Required for write endpoints and `/getConfig`.
        password: Optional. Required if `username` is set.
        timeout: Default per-request timeout in seconds.
        scheme: ``"http"`` (default) or ``"https"``.

    Raises:
        ValueError: if `host` or `scheme` is malformed.
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        host: str,
        *,
        username: str | None = None,
        password: str | None = None,
        timeout: float = 10.0,
        scheme: str = "http",
    ) -> None:
        scheme = _validate_scheme(scheme)
        hostname, port = _validate_host(host)
        auth: aiohttp.BasicAuth | None = None
        if username is not None and password is not None:
            auth = SafeBasicAuth(username, password)
        base_url = URL.build(scheme=scheme, host=hostname, port=port)
        self._transport = VioletTransport(session, base_url, auth=auth, default_timeout=timeout)

    async def __aenter__(self) -> VioletClient:
        """No-op. The aiohttp session lifecycle is the caller's responsibility.

        Implemented so callers can use ``async with VioletClient(...) as client``
        as a stylistic convention. If you add per-request retry pools or
        connection caches in the future, this is where setup/teardown belongs.
        """
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:
        return None

    # ---- namespaces -------------------------------------------------------

    @cached_property
    def readings(self) -> _ReadingsNamespace:
        return _ReadingsNamespace(self._transport)

    @cached_property
    def control(self) -> _ControlNamespace:
        return _ControlNamespace(self._transport)

    @cached_property
    def targets(self) -> _TargetsNamespace:
        return _TargetsNamespace(self._transport)

    @cached_property
    def config(self) -> _ConfigNamespace:
        return _ConfigNamespace(self._transport)

    @cached_property
    def dosing_parameters(self) -> _DosingParametersNamespace:
        """`/setDosingParameters` writes. Distinct from `client.control.dosing`,
        which dispatches per-channel ON/OFF/AUTO commands."""
        return _DosingParametersNamespace(self._transport)

    @cached_property
    def history(self) -> _HistoryNamespace:
        return _HistoryNamespace(self._transport)

    @cached_property
    def calibration(self) -> _CalibrationNamespace:
        return _CalibrationNamespace(self._transport)


# -------- namespaces --------------------------------------------------------


class _ReadingsNamespace:
    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def get(
        self,
        keys: list[str] | None = None,
        *,
        timeout: float | None = None,
    ) -> VioletReadings:
        """Fetch `/getReadings`. With no `keys`, fetches everything."""
        query = constants.DEFAULT_READINGS_QUERY if keys is None else ",".join(keys)
        raw = await self._transport.get(constants.PATH_GET_READINGS, query=query, timeout=timeout)
        return VioletReadings(raw)


class _ControlNamespace:
    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def set_function(
        self,
        key: str,
        action: str,
        duration: int = 0,
        value: int = 0,
        *,
        timeout: float | None = None,
    ) -> Any:
        """Generic escape hatch for `/setFunctionManually?<KEY>,<ACTION>,<DURATION>,<VALUE>`.

        Raises `ValueError` if `key` is not an uppercase identifier or `action`
        is not in `constants.CONTROL_ACTIONS`. `duration` and `value` are
        coerced to ints — fractional values are not supported by the vendor.
        """
        _validate_control_key(key)
        _validate_control_action(action)
        query = f"{key},{action},{int(duration)},{int(value)}"
        return await self._transport.get(
            constants.PATH_SET_FUNCTION_MANUALLY, query=query, timeout=timeout
        )

    async def pump(
        self,
        action: str,
        *,
        speed: int = 0,
        duration: int = 0,
        timeout: float | None = None,
    ) -> Any:
        """Control the pump. `speed` 0=stop, 1-3=speed presets."""
        return await self.set_function("PUMP", action, duration, speed, timeout=timeout)

    async def heater(self, action: str, *, duration: int = 0, timeout: float | None = None) -> Any:
        return await self.set_function("HEATER", action, duration, 0, timeout=timeout)

    async def solar(self, action: str, *, duration: int = 0, timeout: float | None = None) -> Any:
        return await self.set_function("SOLAR", action, duration, 0, timeout=timeout)

    async def light(
        self,
        action: str,
        *,
        value: int = 0,
        duration: int = 0,
        timeout: float | None = None,
    ) -> Any:
        return await self.set_function("LIGHT", action, duration, value, timeout=timeout)

    async def refill(self, action: str, *, duration: int = 0, timeout: float | None = None) -> Any:
        return await self.set_function("REFILL", action, duration, 0, timeout=timeout)

    async def eco(self, action: str, *, duration: int = 0, timeout: float | None = None) -> Any:
        return await self.set_function("ECO", action, duration, 0, timeout=timeout)

    async def backwash(
        self, action: str, *, duration: int = 0, timeout: float | None = None
    ) -> Any:
        return await self.set_function("BACKWASH", action, duration, 0, timeout=timeout)

    async def dosing(
        self,
        code: str,
        action: str,
        *,
        duration: int = 0,
        timeout: float | None = None,
    ) -> Any:
        """Control a dosing channel by code (`CL`, `ELO`, `PHM`, `PHP`, `FLOC`, `ELO_REV`)."""
        if code not in constants.DOSING_CODES:
            raise ValueError(f"unknown dosing code {code!r}")
        # Find the channel number for the code
        channel_num = next(n for n, c in constants.DOSING_CHANNELS.items() if c == code)
        key = f"DOS_{channel_num}_{code}"
        return await self.set_function(key, action, duration, 0, timeout=timeout)

    async def cover_open(
        self,
        *,
        acknowledge_unsafe: bool = False,
        timeout: float | None = None,
    ) -> Any:
        """Open the cover. Pass literal `acknowledge_unsafe=True` to confirm."""
        if acknowledge_unsafe is not True:
            raise UnsafeOperationException("cover_open")
        return await self.set_function(
            constants.CONTROL_KEY_COVER_OPEN, "PUSH", 0, 0, timeout=timeout
        )

    async def cover_close(
        self,
        *,
        acknowledge_unsafe: bool = False,
        timeout: float | None = None,
    ) -> Any:
        """Close the cover. Pass literal `acknowledge_unsafe=True` to confirm."""
        if acknowledge_unsafe is not True:
            raise UnsafeOperationException("cover_close")
        return await self.set_function(
            constants.CONTROL_KEY_COVER_CLOSE, "PUSH", 0, 0, timeout=timeout
        )

    async def cover_stop(self, *, timeout: float | None = None) -> Any:
        """Stop the cover motion. Safe — no acknowledgment required."""
        return await self.set_function(
            constants.CONTROL_KEY_COVER_STOP, "PUSH", 0, 0, timeout=timeout
        )

    async def dmx_scene(
        self,
        index: int,
        action: str,
        *,
        timeout: float | None = None,
    ) -> Any:
        if not (1 <= index <= 12):
            raise ValueError(f"DMX scene index must be 1-12, got {index}")
        return await self.set_function(f"DMX_SCENE{index}", action, 0, 0, timeout=timeout)

    async def extension_relay(
        self,
        key: str,
        action: str,
        *,
        duration: int = 0,
        timeout: float | None = None,
    ) -> Any:
        """Control an extension relay by its key (e.g. ``"EXT1_3"``)."""
        return await self.set_function(key, action, duration, 0, timeout=timeout)


class _TargetsNamespace:
    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def _set(self, field: str, value: float, *, timeout: float | None) -> Any:
        validate_setpoint(field, value)
        query = f"target={field}&value={value}"
        return await self._transport.get(
            constants.PATH_SET_TARGET_VALUES, query=query, timeout=timeout
        )

    async def set_ph(self, value: float, *, timeout: float | None = None) -> Any:
        return await self._set("pH", value, timeout=timeout)

    async def set_orp(self, value: float, *, timeout: float | None = None) -> Any:
        return await self._set("ORP", value, timeout=timeout)

    async def set_chlorine(self, value: float, *, timeout: float | None = None) -> Any:
        return await self._set("MinChlorine", value, timeout=timeout)

    async def set_heater_temp(self, value: float, *, timeout: float | None = None) -> Any:
        return await self._set("Heater", value, timeout=timeout)

    async def set_solar_temp(self, value: float, *, timeout: float | None = None) -> Any:
        return await self._set("Solar", value, timeout=timeout)


class _ConfigNamespace:
    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def get(self, *, timeout: float | None = None) -> Any:
        return await self._transport.get(constants.PATH_GET_CONFIG, timeout=timeout)

    async def update(self, config: dict[str, Any], *, timeout: float | None = None) -> Any:
        return await self._transport.post(constants.PATH_SET_CONFIG, json=config, timeout=timeout)


class _DosingParametersNamespace:
    """Namespace for `/setDosingParameters` writes (dosing config, not per-channel control)."""

    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def set(self, params: dict[str, Any], *, timeout: float | None = None) -> Any:
        """POST a dosing-parameters payload to `/setDosingParameters`."""
        return await self._transport.post(
            constants.PATH_SET_DOSING_PARAMETERS, json=params, timeout=timeout
        )


class _HistoryNamespace:
    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def get(
        self,
        hours: int,
        *,
        sensor: str | None = None,
        timeout: float | None = None,
    ) -> Any:
        query_parts = [f"hours={hours}"]
        if sensor is not None:
            query_parts.append(f"sensor={sensor}")
        return await self._transport.get(
            constants.PATH_GET_HISTORY, query="&".join(query_parts), timeout=timeout
        )


class _CalibrationNamespace:
    def __init__(self, transport: VioletTransport) -> None:
        self._transport = transport

    async def raw_values(self, *, timeout: float | None = None) -> Any:
        return await self._transport.get(constants.PATH_GET_CALIBRATION_RAW, timeout=timeout)

    async def history(self, sensor: str, *, timeout: float | None = None) -> Any:
        return await self._transport.get(
            constants.PATH_GET_CALIBRATION_HISTORY,
            query=f"sensor={sensor}",
            timeout=timeout,
        )
