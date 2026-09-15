from __future__ import annotations

import asyncio
import unittest
from typing import Any

import httpx

from ucii.identity import (
    AsyncIdentityNamespace,
    IdentityNamespace,
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
                "ok": True,
                "method": method,
                "path": path,
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
                "ok": True,
                "method": method,
                "path": path,
            },
        )


class PublicIdentityRequestTests(unittest.TestCase):
    def test_sync_identity_create_request_and_response(self) -> None:
        transport = RecordingTransport()
        identity = IdentityNamespace(transport)

        result = identity.create(
            identity_type="AI_AGENT",
            name="Public Test Agent",
            description="Synthetic public SDK test",
        )

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "POST",
                    "path": "/v1/identity",
                    "json": {
                        "identity_type": "AI_AGENT",
                        "name": "Public Test Agent",
                        "description": "Synthetic public SDK test",
                    },
                    "params": None,
                    "headers": None,
                }
            ],
        )

        self.assertEqual(
            result,
            {
                "ok": True,
                "method": "POST",
                "path": "/v1/identity",
            },
        )

    def test_sync_identity_create_omits_optional_description(self) -> None:
        transport = RecordingTransport()
        identity = IdentityNamespace(transport)

        identity.create(
            identity_type="DEVICE",
            name="Public Test Device",
        )

        self.assertEqual(
            transport.calls[0]["json"],
            {
                "identity_type": "DEVICE",
                "name": "Public Test Device",
            },
        )

    def test_sync_identity_get_and_list_requests(self) -> None:
        transport = RecordingTransport()
        identity = IdentityNamespace(transport)

        get_result = identity.get(
            identity_id="identity-public-123",
        )
        list_result = identity.list()

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "GET",
                    "path": "/v1/identity/identity-public-123",
                    "json": None,
                    "params": None,
                    "headers": None,
                },
                {
                    "method": "GET",
                    "path": "/v1/identity",
                    "json": None,
                    "params": None,
                    "headers": None,
                },
            ],
        )

        self.assertEqual(
            get_result["path"],
            "/v1/identity/identity-public-123",
        )
        self.assertEqual(
            list_result["path"],
            "/v1/identity",
        )

    def test_async_identity_requests_match_sync_contract(self) -> None:
        async def exercise() -> None:
            transport = AsyncRecordingTransport()
            identity = AsyncIdentityNamespace(transport)

            create_result = await identity.create(
                identity_type="AI_AGENT",
                name="Async Public Test Agent",
                description="Synthetic async test",
            )

            get_result = await identity.get(
                identity_id="identity-public-456",
            )

            list_result = await identity.list()

            self.assertEqual(
                transport.calls,
                [
                    {
                        "method": "POST",
                        "path": "/v1/identity",
                        "json": {
                            "identity_type": "AI_AGENT",
                            "name": "Async Public Test Agent",
                            "description": "Synthetic async test",
                        },
                        "params": None,
                        "headers": None,
                    },
                    {
                        "method": "GET",
                        "path": "/v1/identity/identity-public-456",
                        "json": None,
                        "params": None,
                        "headers": None,
                    },
                    {
                        "method": "GET",
                        "path": "/v1/identity",
                        "json": None,
                        "params": None,
                        "headers": None,
                    },
                ],
            )

            self.assertEqual(
                create_result["path"],
                "/v1/identity",
            )
            self.assertEqual(
                get_result["path"],
                "/v1/identity/identity-public-456",
            )
            self.assertEqual(
                list_result["path"],
                "/v1/identity",
            )

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
