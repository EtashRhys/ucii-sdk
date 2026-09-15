"""Public UCII credentials domain."""

from __future__ import annotations

import hashlib

from typing import Any

from .service_entitlement import (
    EntitlementProof,
    _economic_access_headers,
)


def generate_fingerprint(public_key: bytes) -> str:
    """Generate the UCII credential fingerprint for raw public-key bytes.

    UCII credential fingerprints are the lowercase hexadecimal SHA-256
    digest of the raw public verification-key bytes. Private-key material
    is never used.
    """

    return hashlib.sha256(public_key).hexdigest()


def _request_headers(
    *,
    payment_proof: dict[str, Any] | None = None,
    service_entitlement_proof: EntitlementProof | None = None,
    controller_authority: str | None = None,
) -> dict[str, dict[str, str]]:
    """
    Construct independent credential-lifecycle request headers.

    Controller authority governs identity-scoped lifecycle mutation.

    Ordinary x402 payment or service entitlement may independently satisfy
    the economic gate.

    Economic access never substitutes for controller authority.
    """

    economic = _economic_access_headers(
        payment_proof=payment_proof,
        service_entitlement_proof=service_entitlement_proof,
    )

    headers: dict[str, str] = dict(
        economic.get("headers", {})
    )

    if controller_authority is not None:
        headers["X-UCII-Controller-Authority"] = (
            controller_authority
        )

    if not headers:
        return {}

    return {
        "headers": headers,
    }



class CredentialsNamespace:
    """Thin synchronous credentials namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    def register(
        self,
        *,
        identity_id: str,
        credential_type: str,
        algorithm: str,
        public_key: str,
        fingerprint: str,
        key_version: str = "1",
        controller_authority: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Register a cryptographic credential."""

        payload: dict[str, Any] = {
            "identity_id": identity_id,
            "credential_type": credential_type,
            "algorithm": algorithm,
            "public_key": public_key,
            "fingerprint": fingerprint,
            "key_version": key_version,
        }

        response = self._transport.request(
            "POST",
            "/v1/credentials/register",
            json=payload,
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
                controller_authority=controller_authority,
            ),
        )

        return response.json()

    def get(
        self,
        *,
        fingerprint: str,
    ) -> dict[str, Any]:
        """Retrieve a cryptographic credential by fingerprint."""

        response = self._transport.request(
            "GET",
            f"/v1/credentials/{fingerprint}",
        )

        return response.json()

    def revoke(
        self,
        *,
        credential_id: str,
        controller_authority: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Revoke a cryptographic credential."""

        response = self._transport.request(
            "POST",
            f"/v1/credentials/{credential_id}/revoke",
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
                controller_authority=controller_authority,
            ),
        )

        return response.json()


    def recover(
        self,
        *,
        credential_id: str,
        identity_id: str,
        credential_type: str,
        algorithm: str,
        public_key: str,
        fingerprint: str,
        key_version: str = "1",
        controller_authority: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Recover a credential with replacement public credential material."""

        payload: dict[str, Any] = {
            "identity_id": identity_id,
            "credential_type": credential_type,
            "algorithm": algorithm,
            "public_key": public_key,
            "fingerprint": fingerprint,
            "key_version": key_version,
        }

        response = self._transport.request(
            "POST",
            f"/v1/credentials/{credential_id}/recover",
            json=payload,
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
                controller_authority=controller_authority,
            ),
        )

        return response.json()


    def verify(
        self,
        *,
        fingerprint: str,
        message: str,
        signature: str,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Verify cryptographic credential ownership."""

        payload: dict[str, Any] = {
            "fingerprint": fingerprint,
            "message": message,
            "signature": signature,
        }

        response = self._transport.request(
            "POST",
            "/v1/credentials/verify",
            json=payload,
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
            ),
        )

        return response.json()


class AsyncCredentialsNamespace:
    """Thin asynchronous credentials namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    async def register(
        self,
        *,
        identity_id: str,
        credential_type: str,
        algorithm: str,
        public_key: str,
        fingerprint: str,
        key_version: str = "1",
        controller_authority: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Register a cryptographic credential asynchronously."""

        payload: dict[str, Any] = {
            "identity_id": identity_id,
            "credential_type": credential_type,
            "algorithm": algorithm,
            "public_key": public_key,
            "fingerprint": fingerprint,
            "key_version": key_version,
        }

        response = await self._transport.request(
            "POST",
            "/v1/credentials/register",
            json=payload,
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
                controller_authority=controller_authority,
            ),
        )

        return response.json()

    async def get(
        self,
        *,
        fingerprint: str,
    ) -> dict[str, Any]:
        """Retrieve a cryptographic credential asynchronously."""

        response = await self._transport.request(
            "GET",
            f"/v1/credentials/{fingerprint}",
        )

        return response.json()

    async def revoke(
        self,
        *,
        credential_id: str,
        controller_authority: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Revoke a cryptographic credential asynchronously."""

        response = await self._transport.request(
            "POST",
            f"/v1/credentials/{credential_id}/revoke",
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
                controller_authority=controller_authority,
            ),
        )

        return response.json()

    async def recover(
        self,
        *,
        credential_id: str,
        identity_id: str,
        credential_type: str,
        algorithm: str,
        public_key: str,
        fingerprint: str,
        key_version: str = "1",
        controller_authority: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Recover a credential asynchronously with replacement public material."""

        payload: dict[str, Any] = {
            "identity_id": identity_id,
            "credential_type": credential_type,
            "algorithm": algorithm,
            "public_key": public_key,
            "fingerprint": fingerprint,
            "key_version": key_version,
        }

        response = await self._transport.request(
            "POST",
            f"/v1/credentials/{credential_id}/recover",
            json=payload,
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
                controller_authority=controller_authority,
            ),
        )

        return response.json()


    async def verify(
        self,
        *,
        fingerprint: str,
        message: str,
        signature: str,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Verify cryptographic credential ownership asynchronously."""

        payload: dict[str, Any] = {
            "fingerprint": fingerprint,
            "message": message,
            "signature": signature,
        }

        response = await self._transport.request(
            "POST",
            "/v1/credentials/verify",
            json=payload,
            **_request_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
            ),
        )

        return response.json()
