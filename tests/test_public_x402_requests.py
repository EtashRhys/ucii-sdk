from __future__ import annotations

import asyncio
import dataclasses
import unittest
from typing import Any

import httpx

from ucii.x402 import (
    AsyncX402Namespace,
    X402Cryptography,
    X402Info,
    X402Namespace,
    X402Operation,
    X402Pricing,
    X402Service,
    X402TrustModel,
)


INFO_PAYLOAD = {
    "protocol": "x402",
    "service": {
        "name": "UCII Public Service",
        "short_name": "ucii",
        "version": "1.0.0",
        "api_version": "v1",
        "category": "identity",
        "protocol": "x402",
        "payment_flow": "pay-per-use",
        "discovery_endpoint": "/v1/x402/info",
        "pricing_endpoint": "/v1/x402/pricing",
        "trust_model": {
            "identity_represents": "cryptographic-subject",
            "credential_represents": "subject-credential",
            "private_keys_stored": False,
        },
        "cryptography": {
            "post_quantum_supported": True,
            "signature_algorithms": [
                "Ed25519",
                "ML-DSA-65",
            ],
        },
        "capabilities": [
            "identity",
            "credentials",
            "verification",
        ],
    },
    "operations": [
        {
            "method": "POST",
            "endpoint": "/v1/example/paid",
            "amount": 0.25,
            "currency": "USDC",
            "network": "base",
        },
        {
            "method": "GET",
            "endpoint": "/v1/example/discovery",
            "amount": 0.0,
        },
    ],
}


PRICING_PAYLOAD = {
    "protocol": "x402",
    "currency": "USDC",
    "network": "base",
    "operations": [
        {
            "method": "POST",
            "endpoint": "/v1/example/paid",
            "amount": 0.25,
            "currency": "USDC",
            "network": "base",
        },
        {
            "method": "GET",
            "endpoint": "/v1/example/discovery",
            "amount": 0.0,
        },
    ],
}


class RecordingTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "kwargs": kwargs,
            }
        )

        if path == "/v1/x402/info":
            payload = INFO_PAYLOAD
        elif path == "/v1/x402/pricing":
            payload = PRICING_PAYLOAD
        else:
            raise AssertionError(
                f"unexpected synthetic path: {path}"
            )

        request = httpx.Request(
            method,
            f"https://example.invalid{path}",
        )

        return httpx.Response(
            200,
            request=request,
            json=payload,
        )


class AsyncRecordingTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []

    async def request(
        self,
        method: str,
        path: str,
        **kwargs: Any,
    ) -> httpx.Response:
        self.calls.append(
            {
                "method": method,
                "path": path,
                "kwargs": kwargs,
            }
        )

        if path == "/v1/x402/info":
            payload = INFO_PAYLOAD
        elif path == "/v1/x402/pricing":
            payload = PRICING_PAYLOAD
        else:
            raise AssertionError(
                f"unexpected synthetic path: {path}"
            )

        request = httpx.Request(
            method,
            f"https://example.invalid{path}",
        )

        return httpx.Response(
            200,
            request=request,
            json=payload,
        )


class PublicX402RequestTests(unittest.TestCase):
    def test_sync_info_request_and_model_contract(
        self,
    ) -> None:
        transport = RecordingTransport()
        x402 = X402Namespace(transport)

        result = x402.info()

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "GET",
                    "path": "/v1/x402/info",
                    "kwargs": {},
                }
            ],
        )

        self.assertIsInstance(result, X402Info)
        self.assertEqual(result.protocol, "x402")

        self.assertEqual(
            result.service,
            X402Service(
                name="UCII Public Service",
                short_name="ucii",
                version="1.0.0",
                api_version="v1",
                category="identity",
                protocol="x402",
                payment_flow="pay-per-use",
                discovery_endpoint="/v1/x402/info",
                pricing_endpoint="/v1/x402/pricing",
                trust_model=X402TrustModel(
                    identity_represents=(
                        "cryptographic-subject"
                    ),
                    credential_represents=(
                        "subject-credential"
                    ),
                    private_keys_stored=False,
                ),
                cryptography=X402Cryptography(
                    post_quantum_supported=True,
                    signature_algorithms=(
                        "Ed25519",
                        "ML-DSA-65",
                    ),
                ),
                capabilities=(
                    "identity",
                    "credentials",
                    "verification",
                ),
            ),
        )

        self.assertEqual(
            result.operations,
            (
                X402Operation(
                    method="POST",
                    endpoint="/v1/example/paid",
                    amount=0.25,
                    currency="USDC",
                    network="base",
                ),
                X402Operation(
                    method="GET",
                    endpoint="/v1/example/discovery",
                    amount=0.0,
                    currency=None,
                    network=None,
                ),
            ),
        )

        self.assertIsInstance(
            result.service.capabilities,
            tuple,
        )
        self.assertIsInstance(
            result.service.cryptography.signature_algorithms,
            tuple,
        )
        self.assertIsInstance(
            result.operations,
            tuple,
        )

    def test_sync_pricing_request_and_model_contract(
        self,
    ) -> None:
        transport = RecordingTransport()
        x402 = X402Namespace(transport)

        result = x402.pricing()

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "GET",
                    "path": "/v1/x402/pricing",
                    "kwargs": {},
                }
            ],
        )

        self.assertEqual(
            result,
            X402Pricing(
                protocol="x402",
                currency="USDC",
                network="base",
                operations=(
                    X402Operation(
                        method="POST",
                        endpoint="/v1/example/paid",
                        amount=0.25,
                        currency="USDC",
                        network="base",
                    ),
                    X402Operation(
                        method="GET",
                        endpoint="/v1/example/discovery",
                        amount=0.0,
                        currency=None,
                        network=None,
                    ),
                ),
            ),
        )

        self.assertIsInstance(
            result.operations,
            tuple,
        )

    def test_public_x402_models_are_frozen(
        self,
    ) -> None:
        operation = X402Operation(
            method="GET",
            endpoint="/v1/example",
            amount=1.0,
        )

        with self.assertRaises(
            dataclasses.FrozenInstanceError
        ):
            operation.amount = 2.0  # type: ignore[misc]

    def test_async_x402_requests_match_sync_contract(
        self,
    ) -> None:
        async def exercise() -> None:
            transport = AsyncRecordingTransport()
            x402 = AsyncX402Namespace(transport)

            info = await x402.info()
            pricing = await x402.pricing()

            self.assertEqual(
                transport.calls,
                [
                    {
                        "method": "GET",
                        "path": "/v1/x402/info",
                        "kwargs": {},
                    },
                    {
                        "method": "GET",
                        "path": "/v1/x402/pricing",
                        "kwargs": {},
                    },
                ],
            )

            self.assertEqual(
                info,
                X402Namespace(
                    RecordingTransport()
                ).info(),
            )

            self.assertEqual(
                pricing,
                X402Namespace(
                    RecordingTransport()
                ).pricing(),
            )

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
