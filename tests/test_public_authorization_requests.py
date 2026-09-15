"""Public request-contract tests for the UCII authorization doorbell."""

from __future__ import annotations

import asyncio
from types import SimpleNamespace
import unittest

from ucii.authorization import (
    AsyncAuthorizationNamespace,
    AuthorizationNamespace,
)
from ucii.client import AsyncUCIIClient, UCIIClient


REQUEST = {
    "token": "token-123",
    "identity_id": "identity-123",
    "credential_fingerprint": "fp-123",
    "operation": "c55.protected.execute",
    "message": "signed-message",
    "signature": "signature-123",
}

RESPONSE = {
    "authorized": True,
    "executed": False,
    "operation": "c55.protected.execute",
    "identity_id": "identity-123",
    "user_id": "user-123",
    "credential_fingerprint": "fp-123",
    "status": "ACTIVE",
}


class FakeTransport:
    def __init__(self) -> None:
        self.calls = []

    def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        return SimpleNamespace(json=lambda: dict(RESPONSE))


class AsyncFakeTransport:
    def __init__(self) -> None:
        self.calls = []

    async def request(self, method, path, **kwargs):
        self.calls.append((method, path, kwargs))
        return SimpleNamespace(json=lambda: dict(RESPONSE))


class PublicAuthorizationRequestTests(unittest.TestCase):
    def test_sync_authorization_check_exact_request_contract(self) -> None:
        transport = FakeTransport()
        namespace = AuthorizationNamespace(transport)

        result = namespace.check(**REQUEST)

        self.assertEqual(
            transport.calls,
            [
                (
                    "POST",
                    "/v1/authorization/check",
                    {"json": REQUEST},
                )
            ],
        )
        self.assertTrue(result["authorized"])
        self.assertFalse(result["executed"])
        self.assertEqual(result["operation"], REQUEST["operation"])
        self.assertEqual(result["identity_id"], REQUEST["identity_id"])

    def test_async_authorization_check_exact_request_contract(self) -> None:
        async def exercise() -> None:
            transport = AsyncFakeTransport()
            namespace = AsyncAuthorizationNamespace(transport)

            result = await namespace.check(**REQUEST)

            self.assertEqual(
                transport.calls,
                [
                    (
                        "POST",
                        "/v1/authorization/check",
                        {"json": REQUEST},
                    )
                ],
            )
            self.assertTrue(result["authorized"])
            self.assertFalse(result["executed"])
            self.assertEqual(result["operation"], REQUEST["operation"])
            self.assertEqual(
                result["identity_id"],
                REQUEST["identity_id"],
            )

        asyncio.run(exercise())

    def test_public_authorization_surface_is_check_only(self) -> None:
        for namespace in (
            AuthorizationNamespace,
            AsyncAuthorizationNamespace,
        ):
            public_methods = {
                name
                for name in dir(namespace)
                if not name.startswith("_")
            }

            self.assertEqual(public_methods, {"check"})

            for forbidden in (
                "execute",
                "check_delegated",
                "grant_delegated",
                "revoke_delegated",
                "policy",
                "permissions",
            ):
                self.assertFalse(hasattr(namespace, forbidden))

    def test_clients_compose_check_only_authorization_namespace(self) -> None:
        sync_client = UCIIClient(
            base_url="https://example.invalid",
        )
        async_client = AsyncUCIIClient(
            base_url="https://example.invalid",
        )

        try:
            self.assertIsInstance(
                sync_client.authorization,
                AuthorizationNamespace,
            )
            self.assertIsInstance(
                async_client.authorization,
                AsyncAuthorizationNamespace,
            )

            self.assertFalse(
                hasattr(sync_client.authorization, "execute")
            )
            self.assertFalse(
                hasattr(async_client.authorization, "execute")
            )
        finally:
            sync_client.close()
            asyncio.run(async_client.close())


if __name__ == "__main__":
    unittest.main()
