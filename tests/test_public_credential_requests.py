from __future__ import annotations

import asyncio
import base64
import json
import unittest
from typing import Any

import httpx

from ucii.credentials import (
    AsyncCredentialsNamespace,
    CredentialsNamespace,
)
from ucii.service_entitlement import (
    EntitlementProof,
    EntitlementProofChallenge,
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


def synthetic_entitlement_proof(
    *,
    method: str,
    path: str,
) -> EntitlementProof:
    challenge = EntitlementProofChallenge(
        nonce="synthetic-public-nonce",
        subject_identity_id="identity-public-123",
        credential_fingerprint="fingerprint-public-123",
        method=method,
        path=path,
        issued_at="2099-01-01T00:00:00+00:00",
        expires_at="2099-01-01T00:05:00+00:00",
    )

    return EntitlementProof(
        challenge=challenge,
        signature="synthetic-public-signature",
    )


class PublicCredentialRequestTests(unittest.TestCase):
    def test_sync_register_request_contract(self) -> None:
        transport = RecordingTransport()
        credentials = CredentialsNamespace(transport)

        result = credentials.register(
            identity_id="identity-public-123",
            credential_type="ML_DSA_SIGNING_KEY",
            algorithm="ML-DSA-65",
            public_key="public-key-material",
            fingerprint="fingerprint-public-123",
        )

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "POST",
                    "path": "/v1/credentials/register",
                    "json": {
                        "identity_id": "identity-public-123",
                        "credential_type": "ML_DSA_SIGNING_KEY",
                        "algorithm": "ML-DSA-65",
                        "public_key": "public-key-material",
                        "fingerprint": "fingerprint-public-123",
                        "key_version": "1",
                    },
                    "params": None,
                    "headers": None,
                }
            ],
        )

        self.assertEqual(
            result["path"],
            "/v1/credentials/register",
        )

    def test_sync_get_revoke_and_recover_request_contract(self) -> None:
        transport = RecordingTransport()
        credentials = CredentialsNamespace(transport)

        get_result = credentials.get(
            fingerprint="fingerprint-public-123",
        )

        revoke_result = credentials.revoke(
            credential_id="credential-public-123",
            controller_authority="controller-public-test",
        )

        recover_result = credentials.recover(
            credential_id="credential-public-123",
            identity_id="identity-public-123",
            credential_type="ML_DSA_SIGNING_KEY",
            algorithm="ML-DSA-65",
            public_key="replacement-public-key",
            fingerprint="replacement-fingerprint",
            key_version="2",
            controller_authority="controller-public-test",
        )

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "GET",
                    "path": (
                        "/v1/credentials/"
                        "fingerprint-public-123"
                    ),
                    "json": None,
                    "params": None,
                    "headers": None,
                },
                {
                    "method": "POST",
                    "path": (
                        "/v1/credentials/"
                        "credential-public-123/revoke"
                    ),
                    "json": None,
                    "params": None,
                    "headers": {
                        "X-UCII-Controller-Authority":
                            "controller-public-test",
                    },
                },
                {
                    "method": "POST",
                    "path": (
                        "/v1/credentials/"
                        "credential-public-123/recover"
                    ),
                    "json": {
                        "identity_id": "identity-public-123",
                        "credential_type": "ML_DSA_SIGNING_KEY",
                        "algorithm": "ML-DSA-65",
                        "public_key": "replacement-public-key",
                        "fingerprint": "replacement-fingerprint",
                        "key_version": "2",
                    },
                    "params": None,
                    "headers": {
                        "X-UCII-Controller-Authority":
                            "controller-public-test",
                    },
                },
            ],
        )

        self.assertEqual(
            get_result["path"],
            "/v1/credentials/fingerprint-public-123",
        )
        self.assertEqual(
            revoke_result["path"],
            "/v1/credentials/credential-public-123/revoke",
        )
        self.assertEqual(
            recover_result["path"],
            "/v1/credentials/credential-public-123/recover",
        )

    def test_sync_verify_request_contract(self) -> None:
        transport = RecordingTransport()
        credentials = CredentialsNamespace(transport)

        result = credentials.verify(
            fingerprint="fingerprint-public-123",
            message="synthetic-message",
            signature="synthetic-signature",
        )

        self.assertEqual(
            transport.calls,
            [
                {
                    "method": "POST",
                    "path": "/v1/credentials/verify",
                    "json": {
                        "fingerprint": "fingerprint-public-123",
                        "message": "synthetic-message",
                        "signature": "synthetic-signature",
                    },
                    "params": None,
                    "headers": None,
                }
            ],
        )

        self.assertEqual(
            result["path"],
            "/v1/credentials/verify",
        )

    def test_sync_controller_and_payment_headers_remain_independent(
        self,
    ) -> None:
        transport = RecordingTransport()
        credentials = CredentialsNamespace(transport)

        credentials.register(
            identity_id="identity-public-123",
            credential_type="ML_DSA_SIGNING_KEY",
            algorithm="ML-DSA-65",
            public_key="public-key-material",
            fingerprint="fingerprint-public-123",
            controller_authority="controller-public-test",
            payment_proof={
                "proof": "synthetic-public-payment",
                "amount": "1",
            },
        )

        self.assertEqual(
            transport.calls[0]["headers"],
            {
                "x-payment-proof": (
                    '{"amount":"1",'
                    '"proof":"synthetic-public-payment"}'
                ),
                "X-UCII-Controller-Authority":
                    "controller-public-test",
            },
        )

    def test_sync_service_entitlement_header_contract(self) -> None:
        transport = RecordingTransport()
        credentials = CredentialsNamespace(transport)

        proof = synthetic_entitlement_proof(
            method="POST",
            path="/v1/credentials/verify",
        )

        credentials.verify(
            fingerprint="fingerprint-public-123",
            message="synthetic-message",
            signature="synthetic-signature",
            service_entitlement_proof=proof,
        )

        headers = transport.calls[0]["headers"]

        self.assertIsNotNone(headers)
        assert headers is not None

        self.assertEqual(
            set(headers),
            {"X-UCII-Service-Entitlement"},
        )

        encoded = headers[
            "X-UCII-Service-Entitlement"
        ]

        decoded = json.loads(
            base64.urlsafe_b64decode(
                encoded.encode("ascii")
            ).decode("utf-8")
        )

        self.assertEqual(
            decoded,
            {
                "challenge": {
                    "nonce": "synthetic-public-nonce",
                    "subject_identity_id":
                        "identity-public-123",
                    "credential_fingerprint":
                        "fingerprint-public-123",
                    "method": "POST",
                    "path": "/v1/credentials/verify",
                    "issued_at":
                        "2099-01-01T00:00:00+00:00",
                    "expires_at":
                        "2099-01-01T00:05:00+00:00",
                },
                "signature":
                    "synthetic-public-signature",
            },
        )

    def test_sync_economic_presentations_are_mutually_exclusive(
        self,
    ) -> None:
        transport = RecordingTransport()
        credentials = CredentialsNamespace(transport)

        proof = synthetic_entitlement_proof(
            method="POST",
            path="/v1/credentials/verify",
        )

        with self.assertRaisesRegex(
            ValueError,
            "mutually exclusive",
        ):
            credentials.verify(
                fingerprint="fingerprint-public-123",
                message="synthetic-message",
                signature="synthetic-signature",
                payment_proof={
                    "proof": "synthetic-public-payment",
                },
                service_entitlement_proof=proof,
            )

        self.assertEqual(transport.calls, [])

    def test_async_credential_requests_match_sync_contract(
        self,
    ) -> None:
        async def exercise() -> None:
            transport = AsyncRecordingTransport()
            credentials = AsyncCredentialsNamespace(
                transport
            )

            await credentials.register(
                identity_id="identity-public-456",
                credential_type="DEVICE_KEY",
                algorithm="ML-DSA-65",
                public_key="async-public-key",
                fingerprint="async-fingerprint",
                controller_authority="async-controller",
            )

            await credentials.get(
                fingerprint="async-fingerprint",
            )

            await credentials.revoke(
                credential_id="async-credential",
                controller_authority="async-controller",
            )

            await credentials.recover(
                credential_id="async-credential",
                identity_id="identity-public-456",
                credential_type="DEVICE_KEY",
                algorithm="ML-DSA-65",
                public_key="async-replacement-key",
                fingerprint="async-replacement-fingerprint",
                controller_authority="async-controller",
            )

            await credentials.verify(
                fingerprint="async-replacement-fingerprint",
                message="async-message",
                signature="async-signature",
            )

            self.assertEqual(
                [
                    (call["method"], call["path"])
                    for call in transport.calls
                ],
                [
                    (
                        "POST",
                        "/v1/credentials/register",
                    ),
                    (
                        "GET",
                        "/v1/credentials/async-fingerprint",
                    ),
                    (
                        "POST",
                        (
                            "/v1/credentials/"
                            "async-credential/revoke"
                        ),
                    ),
                    (
                        "POST",
                        (
                            "/v1/credentials/"
                            "async-credential/recover"
                        ),
                    ),
                    (
                        "POST",
                        "/v1/credentials/verify",
                    ),
                ],
            )

            self.assertEqual(
                transport.calls[0]["headers"],
                {
                    "X-UCII-Controller-Authority":
                        "async-controller",
                },
            )

            self.assertEqual(
                transport.calls[3]["json"],
                {
                    "identity_id": "identity-public-456",
                    "credential_type": "DEVICE_KEY",
                    "algorithm": "ML-DSA-65",
                    "public_key": "async-replacement-key",
                    "fingerprint":
                        "async-replacement-fingerprint",
                    "key_version": "1",
                },
            )

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
