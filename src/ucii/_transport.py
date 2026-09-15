"""Internal UCII SDK HTTP transport implementation."""

from __future__ import annotations

from typing import Any

import httpx

from .errors import (
    UCIIAPIError,
    UCIIAuthenticationError,
    UCIIAuthorizationError,
    UCIIPaymentRequiredError,
    UCIIConflictError,
    UCIIResourceNotFoundError,
    UCIIServiceError,
    UCIITransportError,
    UCIIValidationError,
)


def _error_from_response(response: httpx.Response) -> UCIIAPIError:
    """Convert an HTTP error response into the public SDK error model."""

    status_code = response.status_code
    request_id = response.headers.get("x-request-id")
    details: dict[str, Any] | None = None
    message = f"UCII API request failed with status {status_code}"
    error_code: str | None = None

    try:
        payload = response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict):
        detail = payload.get("detail")

        if isinstance(detail, str):
            message = detail
        elif isinstance(detail, dict):
            details = dict(detail)
            message = str(
                detail.get("message")
                or detail.get("detail")
                or message
            )
            error_code = detail.get("code") or detail.get("error_code")
        elif detail is not None:
            details = {"detail": detail}

        error_code = error_code or payload.get("code") or payload.get("error_code")

        if details is None:
            extra = payload.get("details")
            if isinstance(extra, dict):
                details = dict(extra)

        request_id = request_id or payload.get("request_id")

    error_kwargs = {
        "message": message,
        "error_code": error_code,
        "request_id": request_id,
        "status_code": status_code,
        "details": details,
    }

    if status_code == 402:
        return UCIIPaymentRequiredError(**error_kwargs)
    if status_code == 401:
        return UCIIAuthenticationError(**error_kwargs)
    if status_code == 403:
        return UCIIAuthorizationError(**error_kwargs)
    if status_code == 404:
        return UCIIResourceNotFoundError(**error_kwargs)
    if status_code == 409:
        return UCIIConflictError(**error_kwargs)
    if status_code == 422:
        return UCIIValidationError(**error_kwargs)
    if status_code >= 500:
        return UCIIServiceError(**error_kwargs)

    return UCIIAPIError(**error_kwargs)


class HTTPTransport:
    """Internal synchronous HTTP transport."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        request_headers = self._headers()
        if headers:
            request_headers.update(headers)

        try:
            response = self._client.request(
                method,
                path,
                json=json,
                params=params,
                headers=request_headers,
            )
        except httpx.HTTPError as exc:
            raise UCIITransportError(str(exc)) from exc

        if response.is_error:
            raise _error_from_response(response)

        return response

    def close(self) -> None:
        self._client.close()

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers


class AsyncHTTPTransport:
    """Internal asynchronous HTTP transport."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        )

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        request_headers = self._headers()
        if headers:
            request_headers.update(headers)

        try:
            response = await self._client.request(
                method,
                path,
                json=json,
                params=params,
                headers=request_headers,
            )
        except httpx.HTTPError as exc:
            raise UCIITransportError(str(exc)) from exc

        if response.is_error:
            raise _error_from_response(response)

        return response

    async def close(self) -> None:
        await self._client.aclose()

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        return headers
