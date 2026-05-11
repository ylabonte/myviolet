"""HTTP transport for the Violet controller.

A thin wrapper around `aiohttp.ClientSession` that handles HTTP Basic auth,
per-request timeouts, and uniform error mapping to the `myviolet.exceptions`
hierarchy. Every namespace on `VioletClient` funnels through this single
layer so retry/observability hooks can be added in one place.
"""

from __future__ import annotations

import asyncio
import json
from typing import Any

import aiohttp
from yarl import URL

from .exceptions import (
    BadCredentialsException,
    BadStatusCodeException,
    InvalidPayloadException,
    TimeoutException,
    VioletApiException,
)


class VioletTransport:
    """HTTP layer that all `VioletClient` namespaces share."""

    def __init__(
        self,
        session: aiohttp.ClientSession,
        base_url: URL,
        auth: aiohttp.BasicAuth | None,
        default_timeout: float = 10.0,
    ) -> None:
        self._session = session
        self._base_url = base_url
        self._auth = auth
        self._default_timeout = default_timeout

    async def get(
        self,
        path: str,
        *,
        query: str | None = None,
        timeout: float | None = None,
    ) -> Any:
        """GET `<base_url><path>?<query>` and return parsed JSON.

        The Violet API uses raw comma-separated query strings (e.g.
        ``?ALL,DOSAGE,RUNTIMES``) rather than ``key=value`` pairs, so this
        method accepts the query as a single raw string.
        """
        url = self._base_url.join(URL(path))
        if query is not None:
            url = url.with_query(query)
        return await self._request("GET", url, timeout=timeout)

    async def post(
        self,
        path: str,
        *,
        json: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> Any:
        """POST `<base_url><path>` with a JSON body and return parsed JSON."""
        url = self._base_url.join(URL(path))
        return await self._request("POST", url, json_body=json, timeout=timeout)

    async def _request(
        self,
        method: str,
        url: URL,
        *,
        json_body: dict[str, Any] | None = None,
        timeout: float | None,
    ) -> Any:
        effective_timeout = timeout if timeout is not None else self._default_timeout
        try:
            async with asyncio.timeout(effective_timeout):
                async with self._session.request(
                    method,
                    url,
                    auth=self._auth,
                    json=json_body,
                ) as response:
                    return await _parse_response(response)
        except TimeoutError as exc:
            raise TimeoutException(f"request to {url} timed out") from exc
        except aiohttp.ClientError as exc:
            raise VioletApiException(f"HTTP client error for {url}: {exc}") from exc


async def _parse_response(response: aiohttp.ClientResponse) -> Any:
    status = response.status
    if status in (401, 403):
        raise BadCredentialsException(status)
    if status >= 400:
        body_preview = (await response.text())[:200]
        raise BadStatusCodeException(status, body_preview)
    try:
        return await response.json(content_type=None)
    except (json.JSONDecodeError, aiohttp.ContentTypeError) as exc:
        raise InvalidPayloadException(f"response was not valid JSON: {exc}") from exc
