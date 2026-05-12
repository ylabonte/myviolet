"""aiohttp app for the myviolet mock controller.

Exposes the same routes as a real Violet controller, backed by a `MockState`
instance. Reads return the current state (with sensor drift applied); writes
mutate the state so subsequent reads see the change.
"""

from __future__ import annotations

import base64
import binascii
import hmac
import json
import logging
import time
from typing import Any

from aiohttp import web

from myviolet.constants import (
    PATH_GET_CONFIG,
    PATH_GET_READINGS,
    PATH_SET_CONFIG,
    PATH_SET_DOSING_PARAMETERS,
    PATH_SET_FUNCTION_MANUALLY,
    PATH_SET_TARGET_VALUES,
)

from .drift import apply_drift
from .state import MockState

_LOG = logging.getLogger(__name__)

_STATE_KEY = web.AppKey("state", MockState)
_USERNAME_KEY = web.AppKey("username", str)
_PASSWORD_KEY = web.AppKey("password", str)


def create_app(state: MockState, *, username: str, password: str) -> web.Application:
    """Build the aiohttp application backed by `state`."""
    app = web.Application(middlewares=[_basic_auth_middleware])
    app[_STATE_KEY] = state
    app[_USERNAME_KEY] = username
    app[_PASSWORD_KEY] = password

    app.router.add_get(PATH_GET_READINGS, _handle_get_readings)
    app.router.add_get(PATH_GET_CONFIG, _handle_get_config)
    app.router.add_get(PATH_SET_FUNCTION_MANUALLY, _handle_set_function)
    app.router.add_get(PATH_SET_TARGET_VALUES, _handle_set_target)
    app.router.add_post(PATH_SET_CONFIG, _handle_set_config)
    app.router.add_post(PATH_SET_DOSING_PARAMETERS, _handle_set_dosing_parameters)

    return app


@web.middleware
async def _basic_auth_middleware(request: web.Request, handler: Any) -> web.StreamResponse:
    # /getReadings is anonymous on the demo controller; everything else requires auth
    if request.path == PATH_GET_READINGS:
        return await handler(request)

    auth_header = request.headers.get("Authorization", "")
    expected_user = request.app[_USERNAME_KEY]
    expected_pass = request.app[_PASSWORD_KEY]
    if not _valid_basic_auth(auth_header, expected_user, expected_pass):
        return web.Response(
            status=401,
            headers={"WWW-Authenticate": 'Basic realm="violet"'},
        )
    return await handler(request)


def _valid_basic_auth(header: str, username: str, password: str) -> bool:
    if not header.startswith("Basic "):
        return False
    try:
        decoded = base64.b64decode(header[6:], validate=True).decode("utf-8")
    except (binascii.Error, ValueError, UnicodeDecodeError):
        # `binascii.Error` covers padding / non-base64 alphabet rejections from
        # `validate=True`; the others guard the subsequent UTF-8 decode.
        return False
    expected = f"{username}:{password}"
    # Constant-time compare to avoid leaking credentials byte-by-byte via timing.
    return hmac.compare_digest(decoded, expected)


async def _handle_get_readings(request: web.Request) -> web.Response:
    """Return the readings snapshot, optionally filtered by query selectors."""
    query = request.query_string
    if not query:
        # Matches real controller behavior
        return web.Response(status=500, text="missing query parameters")

    state = request.app[_STATE_KEY]
    snapshot = state.snapshot()
    elapsed = time.time() - state.epoch_start
    snapshot = apply_drift(snapshot, elapsed_seconds=elapsed)

    keywords = {part for part in query.split(",") if part}
    if "ALL" in keywords:
        return web.json_response(snapshot)

    # Selective fetch: keep only the requested keys plus their _min/_max siblings.
    selected: dict[str, Any] = {}
    for key in keywords:
        for full_key in (key, f"{key}_min", f"{key}_max"):
            if full_key in snapshot:
                selected[full_key] = snapshot[full_key]
    return web.json_response(selected)


async def _handle_get_config(request: web.Request) -> web.Response:
    return web.json_response(request.app[_STATE_KEY].config_snapshot())


async def _handle_set_function(request: web.Request) -> web.Response:
    raw = request.query_string
    parts = raw.split(",")
    if len(parts) < 2:
        return web.Response(status=400, text="expected KEY,ACTION,DURATION,VALUE")
    key = parts[0]
    action = parts[1]
    try:
        duration = int(parts[2]) if len(parts) > 2 and parts[2] else 0
        value = int(parts[3]) if len(parts) > 3 and parts[3] else 0
    except ValueError:
        _LOG.debug("setFunctionManually got non-integer duration/value", exc_info=True)
        return web.Response(status=400, text="duration and value must be integers")
    try:
        request.app[_STATE_KEY].apply_set_function(key, action, duration, value)
    except KeyError:
        # Don't echo exception details back to the client (CodeQL py/stack-trace-exposure).
        _LOG.warning("setFunctionManually rejected", exc_info=True)
        return web.Response(status=400, text="unknown control key")
    return web.json_response({"ok": True})


async def _handle_set_target(request: web.Request) -> web.Response:
    target = request.query.get("target")
    value_raw = request.query.get("value")
    if not target or value_raw is None:
        return web.Response(status=400, text="missing target or value")
    try:
        value = float(value_raw)
    except ValueError:
        _LOG.debug("setTargetValues got non-numeric value", exc_info=True)
        return web.Response(status=400, text="value must be numeric")
    request.app[_STATE_KEY].apply_set_target(target, value)
    return web.json_response({"ok": True})


async def _handle_set_config(request: web.Request) -> web.Response:
    payload = await _read_json(request)
    if isinstance(payload, web.Response):
        return payload
    request.app[_STATE_KEY].apply_set_config(payload)
    return web.json_response({"ok": True})


async def _handle_set_dosing_parameters(request: web.Request) -> web.Response:
    payload = await _read_json(request)
    if isinstance(payload, web.Response):
        return payload
    request.app[_STATE_KEY].apply_set_dosing_parameters(payload)
    return web.json_response({"ok": True})


async def _read_json(request: web.Request) -> dict[str, Any] | web.Response:
    """Return the request body as a JSON dict, or a 400 response on bad input."""
    try:
        payload = await request.json()
    except (json.JSONDecodeError, UnicodeDecodeError):
        _LOG.debug("invalid JSON body", exc_info=True)
        return web.Response(status=400, text="invalid JSON body")
    if not isinstance(payload, dict):
        return web.Response(status=400, text="JSON body must be an object")
    return payload
