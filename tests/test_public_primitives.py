from __future__ import annotations

import base64
import dataclasses
import hashlib
import json
import re
import unittest
from datetime import datetime, timedelta, timezone

import ucii
from ucii.credentials import generate_fingerprint
from ucii.participant import ParticipantContext
from ucii.service_entitlement import (
    ENTITLEMENT_PROOF_VERSION,
    EntitlementProof,
    EntitlementProofChallenge,
    create_entitlement_proof,
    entitlement_proof_header_value,
    generate_entitlement_nonce,
)
from ucii.signing import SigningProvider


class RecordingSigningProvider:
    algorithm = "TEST-SIGNATURE"
    public_key = b"public-verification-key"

    def __init__(self, signature: bytes = b"signed-result") -> None:
        self.signature = signature
        self.messages: list[bytes] = []

    def sign(self, message: bytes) -> bytes:
        self.messages.append(message)
        return self.signature


def make_challenge(
    *,
    issued_at: str = "2030-01-01T12:00:00+00:00",
    expires_at: str = "2030-01-01T12:05:00+00:00",
) -> EntitlementProofChallenge:
    return EntitlementProofChallenge(
        nonce="nonce-123",
        subject_identity_id="identity-123",
        credential_fingerprint="fingerprint-123",
        method="POST",
        path="/v1/credentials/verify",
        issued_at=issued_at,
        expires_at=expires_at,
    )


class PublicServiceEntitlementContractTests(unittest.TestCase):
    def test_root_exports_exact_entitlement_and_signing_primitives(self) -> None:
        expected = (
            "ENTITLEMENT_PROOF_VERSION",
            "EntitlementProof",
            "EntitlementProofChallenge",
            "ParticipantContext",
            "SigningProvider",
            "create_entitlement_proof",
            "entitlement_proof_header_value",
            "generate_entitlement_nonce",
        )

        for name in expected:
            with self.subTest(name=name):
                self.assertTrue(hasattr(ucii, name))

        self.assertFalse(hasattr(ucii, "generate_fingerprint"))

    def test_challenge_validation_canonical_message_and_freshness(self) -> None:
        challenge = make_challenge()

        expected_payload = {
            "credential_fingerprint": "fingerprint-123",
            "expires_at": "2030-01-01T12:05:00+00:00",
            "issued_at": "2030-01-01T12:00:00+00:00",
            "method": "POST",
            "nonce": "nonce-123",
            "path": "/v1/credentials/verify",
            "subject_identity_id": "identity-123",
            "version": ENTITLEMENT_PROOF_VERSION,
        }

        self.assertEqual(
            challenge.canonical_message(),
            json.dumps(
                expected_payload,
                separators=(",", ":"),
                sort_keys=True,
            ),
        )

        self.assertTrue(
            challenge.is_fresh(
                now=datetime(
                    2030, 1, 1, 12, 2, tzinfo=timezone.utc
                )
            )
        )
        self.assertTrue(
            challenge.is_fresh(
                now=datetime(2030, 1, 1, 12, 0)
            )
        )
        self.assertFalse(
            challenge.is_fresh(
                now=datetime(
                    2030, 1, 1, 11, 59, 59,
                    tzinfo=timezone.utc,
                )
            )
        )
        self.assertFalse(
            challenge.is_fresh(
                now=datetime(
                    2030, 1, 1, 12, 5, 1,
                    tzinfo=timezone.utc,
                )
            )
        )

        invalid_cases = (
            {"nonce": ""},
            {"method": "post"},
            {"method": " POST"},
            {"path": "v1/credentials/verify"},
            {"path": "/v1/credentials/verify "},
            {"issued_at": "not-a-timestamp"},
            {"issued_at": "2030-01-01T12:00:00"},
            {
                "expires_at":
                    "2030-01-01T12:00:00+00:00"
            },
        )

        base = {
            "nonce": "nonce-123",
            "subject_identity_id": "identity-123",
            "credential_fingerprint": "fingerprint-123",
            "method": "POST",
            "path": "/v1/credentials/verify",
            "issued_at": "2030-01-01T12:00:00+00:00",
            "expires_at": "2030-01-01T12:05:00+00:00",
        }

        for replacement in invalid_cases:
            with self.subTest(replacement=replacement):
                values = dict(base)
                values.update(replacement)
                with self.assertRaises(ValueError):
                    EntitlementProofChallenge(**values)

    def test_create_proof_signs_only_canonical_message(self) -> None:
        now = datetime.now(timezone.utc)
        challenge = make_challenge(
            issued_at=(now - timedelta(seconds=5)).isoformat(),
            expires_at=(now + timedelta(minutes=5)).isoformat(),
        )
        provider = RecordingSigningProvider(
            signature=b"\x00\x01signature\xff"
        )

        self.assertIsInstance(provider, SigningProvider)

        proof = create_entitlement_proof(
            challenge,
            signing_provider=provider,
        )

        self.assertEqual(
            provider.messages,
            [challenge.canonical_message().encode("utf-8")],
        )
        self.assertEqual(
            proof,
            EntitlementProof(
                challenge=challenge,
                signature=base64.b64encode(
                    b"\x00\x01signature\xff"
                ).decode("ascii"),
            ),
        )

    def test_create_proof_rejects_invalid_provider_and_stale_challenge(
        self,
    ) -> None:
        now = datetime.now(timezone.utc)

        stale = make_challenge(
            issued_at=(now - timedelta(minutes=10)).isoformat(),
            expires_at=(now - timedelta(minutes=5)).isoformat(),
        )

        with self.assertRaises(ValueError):
            create_entitlement_proof(
                stale,
                signing_provider=RecordingSigningProvider(),
            )

        fresh = make_challenge(
            issued_at=(now - timedelta(seconds=5)).isoformat(),
            expires_at=(now + timedelta(minutes=5)).isoformat(),
        )

        with self.assertRaises(TypeError):
            create_entitlement_proof(
                fresh,
                signing_provider=object(),
            )

        class TextSigner:
            def sign(self, message: bytes) -> str:
                return "not-bytes"

        with self.assertRaises(ValueError):
            create_entitlement_proof(
                fresh,
                signing_provider=TextSigner(),
            )

        class EmptySigner:
            def sign(self, message: bytes) -> bytes:
                return b""

        with self.assertRaises(ValueError):
            create_entitlement_proof(
                fresh,
                signing_provider=EmptySigner(),
            )

        with self.assertRaises(TypeError):
            create_entitlement_proof(
                object(),
                signing_provider=RecordingSigningProvider(),
            )

    def test_entitlement_header_is_deterministic_compact_payload(self) -> None:
        challenge = make_challenge()
        proof = EntitlementProof(
            challenge=challenge,
            signature="c2lnbmF0dXJl",
        )

        value = entitlement_proof_header_value(proof)

        decoded = json.loads(
            base64.urlsafe_b64decode(value.encode("ascii")).decode(
                "utf-8"
            )
        )

        self.assertEqual(
            decoded,
            {
                "challenge": {
                    "credential_fingerprint": "fingerprint-123",
                    "expires_at":
                        "2030-01-01T12:05:00+00:00",
                    "issued_at":
                        "2030-01-01T12:00:00+00:00",
                    "method": "POST",
                    "nonce": "nonce-123",
                    "path": "/v1/credentials/verify",
                    "subject_identity_id": "identity-123",
                },
                "signature": "c2lnbmF0dXJl",
            },
        )

        expected_json = json.dumps(
            decoded,
            separators=(",", ":"),
            sort_keys=True,
        ).encode("utf-8")

        self.assertEqual(
            value,
            base64.urlsafe_b64encode(expected_json).decode(
                "ascii"
            ),
        )

        with self.assertRaises(TypeError):
            entitlement_proof_header_value(object())

        with self.assertRaises(ValueError):
            EntitlementProof(
                challenge=challenge,
                signature="",
            )

    def test_nonce_is_nonempty_urlsafe_and_not_reused(self) -> None:
        first = generate_entitlement_nonce()
        second = generate_entitlement_nonce()

        self.assertIsInstance(first, str)
        self.assertIsInstance(second, str)
        self.assertTrue(first)
        self.assertTrue(second)
        self.assertNotEqual(first, second)

        self.assertRegex(first, r"^[A-Za-z0-9_-]+$")
        self.assertRegex(second, r"^[A-Za-z0-9_-]+$")


class PublicSigningAndParticipantContractTests(unittest.TestCase):
    def test_signing_provider_is_runtime_provider_neutral_contract(
        self,
    ) -> None:
        provider = RecordingSigningProvider()

        self.assertIsInstance(provider, SigningProvider)
        self.assertEqual(provider.algorithm, "TEST-SIGNATURE")
        self.assertEqual(
            provider.public_key,
            b"public-verification-key",
        )
        self.assertEqual(
            provider.sign(b"message"),
            b"signed-result",
        )
        self.assertEqual(provider.messages, [b"message"])

        class MissingSign:
            algorithm = "TEST"
            public_key = b"public"

        self.assertNotIsInstance(MissingSign(), SigningProvider)

    def test_participant_context_is_frozen_public_data_only(self) -> None:
        context = ParticipantContext(
            identity_id="identity-123",
            credential_id="credential-123",
            public_key=b"public-key",
        )

        self.assertEqual(context.identity_id, "identity-123")
        self.assertEqual(context.credential_id, "credential-123")
        self.assertEqual(context.public_key, b"public-key")

        self.assertTrue(dataclasses.is_dataclass(context))
        self.assertTrue(
            type(context).__dataclass_params__.frozen
        )

        with self.assertRaises(dataclasses.FrozenInstanceError):
            context.identity_id = "other"


class PublicCredentialFingerprintContractTests(unittest.TestCase):
    def test_fingerprint_is_lowercase_sha256_of_raw_public_key_bytes(
        self,
    ) -> None:
        samples = (
            b"",
            b"ucii",
            bytes(range(32)),
            b"\x00public\x00key\xff",
        )

        for public_key in samples:
            with self.subTest(public_key=public_key):
                expected = hashlib.sha256(
                    public_key
                ).hexdigest()

                actual = generate_fingerprint(public_key)

                self.assertEqual(actual, expected)
                self.assertRegex(actual, r"^[0-9a-f]{64}$")

        self.assertEqual(
            generate_fingerprint(b"ucii"),
            "8e30ce8fe0d63b47b8f80d0a0c61322"
            "b3cce2ca7f5881515608f5a2a2bf61882",
        )


if __name__ == "__main__":
    unittest.main()
