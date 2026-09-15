from __future__ import annotations

import asyncio
import unittest

import ucii
from ucii import AsyncUCIIClient, UCIIClient
from ucii.credentials import (
    AsyncCredentialsNamespace,
    CredentialsNamespace,
)
from ucii.identity import (
    AsyncIdentityNamespace,
    IdentityNamespace,
)
from ucii.verification import (
    AsyncVerificationNamespace,
    VerificationNamespace,
)
from ucii.x402 import (
    AsyncX402Namespace,
    X402Namespace,
)


EXPECTED_ROOT_EXPORTS = {
    "AsyncUCIIClient",
    "ENTITLEMENT_PROOF_VERSION",
    "EntitlementProof",
    "EntitlementProofChallenge",
    "ParticipantContext",
    "SigningProvider",
    "UCIIAPIError",
    "UCIIClient",
    "UCIIAuthenticationError",
    "UCIIAuthorizationError",
    "UCIIConfigurationError",
    "UCIIConflictError",
    "UCIIError",
    "UCIIPaymentRequiredError",
    "UCIIResourceNotFoundError",
    "UCIIServiceError",
    "UCIITransportError",
    "UCIIValidationError",
    "create_entitlement_proof",
    "entitlement_proof_header_value",
    "generate_entitlement_nonce",
}

WITHHELD_CLIENT_NAMESPACES = {
    "auth",
    "policy",
    "peer_auth",
    "peer_trust",
    "adoption",
    "provenance",
}


class PublicPackageContractTests(unittest.TestCase):
    def test_package_root_exports_exact_public_contract(self) -> None:
        self.assertEqual(
            set(ucii.__all__),
            EXPECTED_ROOT_EXPORTS,
        )

        for name in EXPECTED_ROOT_EXPORTS:
            self.assertTrue(
                hasattr(ucii, name),
                name,
            )

    def test_x402_implementation_types_are_not_root_exports(self) -> None:
        for name in (
            "X402Operation",
            "X402TrustModel",
            "X402Cryptography",
            "X402Service",
            "X402Info",
            "X402Pricing",
            "X402Namespace",
            "AsyncX402Namespace",
        ):
            self.assertNotIn(name, ucii.__all__)
            self.assertFalse(
                hasattr(ucii, name),
                name,
            )


class PublicSyncClientContractTests(unittest.TestCase):
    def test_sync_client_composition_and_boundaries(self) -> None:
        client = UCIIClient(
            base_url="https://example.invalid/",
        )

        try:
            self.assertEqual(
                client.base_url,
                "https://example.invalid",
            )

            self.assertIsInstance(
                client.identity,
                IdentityNamespace,
            )
            self.assertIsInstance(
                client.credentials,
                CredentialsNamespace,
            )
            self.assertIsInstance(
                client.verification,
                VerificationNamespace,
            )
            self.assertIsInstance(
                client.x402,
                X402Namespace,
            )

            self.assertTrue(
                callable(client.x402.info)
            )
            self.assertTrue(
                callable(client.x402.pricing)
            )
            self.assertFalse(
                hasattr(client.x402, "settlements")
            )

            for name in WITHHELD_CLIENT_NAMESPACES:
                self.assertFalse(
                    hasattr(client, name),
                    name,
                )
        finally:
            client.close()

    def test_sync_context_manager_returns_public_client(self) -> None:
        with UCIIClient(
            base_url="https://example.invalid",
        ) as client:
            self.assertIsInstance(
                client,
                UCIIClient,
            )


class PublicAsyncClientContractTests(unittest.TestCase):
    def test_async_client_composition_and_boundaries(self) -> None:
        async def exercise() -> None:
            client = AsyncUCIIClient(
                base_url="https://example.invalid/",
            )

            try:
                self.assertEqual(
                    client.base_url,
                    "https://example.invalid",
                )

                self.assertIsInstance(
                    client.identity,
                    AsyncIdentityNamespace,
                )
                self.assertIsInstance(
                    client.credentials,
                    AsyncCredentialsNamespace,
                )
                self.assertIsInstance(
                    client.verification,
                    AsyncVerificationNamespace,
                )
                self.assertIsInstance(
                    client.x402,
                    AsyncX402Namespace,
                )

                self.assertTrue(
                    callable(client.x402.info)
                )
                self.assertTrue(
                    callable(client.x402.pricing)
                )
                self.assertFalse(
                    hasattr(client.x402, "settlements")
                )

                for name in WITHHELD_CLIENT_NAMESPACES:
                    self.assertFalse(
                        hasattr(client, name),
                        name,
                    )
            finally:
                await client.close()

        asyncio.run(exercise())

    def test_async_context_manager_returns_public_client(self) -> None:
        async def exercise() -> None:
            async with AsyncUCIIClient(
                base_url="https://example.invalid",
            ) as client:
                self.assertIsInstance(
                    client,
                    AsyncUCIIClient,
                )

        asyncio.run(exercise())


if __name__ == "__main__":
    unittest.main()
