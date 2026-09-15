"""Public UCII verification domain."""

from __future__ import annotations

from typing import Any


class VerificationNamespace:
    """Thin synchronous verification namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport


    def status(self) -> dict[str, Any]:
        """Retrieve the current UCII verification status."""

        response = self._transport.request(
            "GET",
            "/v1/verification/status",
        )

        return response.json()


class AsyncVerificationNamespace:
    """Thin asynchronous verification namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    async def status(self) -> dict[str, Any]:
        """Retrieve the current UCII verification status asynchronously."""

        response = await self._transport.request(
            "GET",
            "/v1/verification/status",
        )

        return response.json()
