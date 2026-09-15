from __future__ import annotations

import asyncio
import unittest
from typing import Any

import httpx

from ucii.verification import (
    AsyncVerificationNamespace,
    VerificationNamespace,
)


class RecordingTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "json": json,
                "params": params,
                "headers": headers,
            }
        )

        request = httpx.Request(
            method,
            f"https://example.invalid{path}",
        )

        return httpx.Response(
            200,
            request=request,
            json={
                "status": "synthetic-public-status",
                "verified": True,
            },
        )


class AsyncRecordingTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def request(
        self,
        method: str,
        path: str,
        *,
        json: Any | None = None,
        params: Any | None = None,
        headers: dict[str, str] | None = None,
    ) -> httpx.Response:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "json": json,
                "params": params,
                "headers": headers,
            }
        )

        request = httpx.Request(
            method,
            f"https://example.invalid{path}",
        )

        return httpx.Response(
            200,
            request=request,
            json={
                "status": "synthetic-public-status",
                "verified": True,
            },
        )


class PublicVerificationRequestTests(unittest.TestCase):
    def test_sync_verification_status_request_contract(
        self,
    ) -> None:
        transport = RecordingTransport()
        verification = VerificationNamespace(transport)

        result = verification.status()

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "GET",
                    "path": "/v1/verification/status",
                    "json": None,
                    "params": None,
                    "headers": None,
                }
            ],
        )

        self.assertEqual(
            result,
            {
                "status": "synthetic-public-status",
                "verified": True,
            },
        )

    def test_async_verification_status_matches_sync_contract(
        self,
    ) -> None:
        async def exercise() -> None:
            transport = AsyncRecordingTransport()
            verification = AsyncVerificationNamespace(
                transport
            )

            result = await verification.status()

            self.assertEqual(
                transport.calls,
                [
                    {
                        "method": "GET",
                        "path": "/v1/verification/status",
                        "json": None,
                        "params": None,
                        "headers": None,
                    }
                ],
            )

            self.assertEqual(
                result,
                {
                    "status": "synthetic-public-status",
                    "verified": True,
                },
            )

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
