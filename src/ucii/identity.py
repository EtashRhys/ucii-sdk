"""Public UCII identity domain."""

from __future__ import annotations

from typing import Any

from .service_entitlement import (
    EntitlementProof,
    _economic_access_headers,
)

class IdentityNamespace:
    """Thin synchronous identity namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    def create(
        self,
        *,
        identity_type: str,
        name: str,
        description: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Create a UCII identity."""

        payload: dict[str, Any] = {
            "identity_type": identity_type,
            "name": name,
        }

        if description is not None:
            payload["description"] = description

        response = self._transport.request(
            "POST",
            "/v1/identity",
            json=payload,
            **_economic_access_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
            ),
        )

        return response.json()

    def get(
        self,
        *,
        identity_id: str,
    ) -> dict[str, Any]:
        """Retrieve a UCII identity by identifier."""

        response = self._transport.request(
            "GET",
            f"/v1/identity/{identity_id}",
        )

        return response.json()

    def list(self) -> list[dict[str, Any]]:
        """List available UCII identities."""

        response = self._transport.request(
            "GET",
            "/v1/identity",
        )

        return response.json()


class AsyncIdentityNamespace:
    """Thin asynchronous identity namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    async def create(
        self,
        *,
        identity_type: str,
        name: str,
        description: str | None = None,
        payment_proof: dict[str, Any] | None = None,
        service_entitlement_proof: EntitlementProof | None = None,
    ) -> dict[str, Any]:
        """Create a UCII identity asynchronously."""

        payload: dict[str, Any] = {
            "identity_type": identity_type,
            "name": name,
        }

        if description is not None:
            payload["description"] = description

        response = await self._transport.request(
            "POST",
            "/v1/identity",
            json=payload,
            **_economic_access_headers(
                payment_proof=payment_proof,
                service_entitlement_proof=service_entitlement_proof,
            ),
        )

        return response.json()

    async def get(
        self,
        *,
        identity_id: str,
    ) -> dict[str, Any]:
        """Retrieve a UCII identity by identifier asynchronously."""

        response = await self._transport.request(
            "GET",
            f"/v1/identity/{identity_id}",
        )

        return response.json()

    async def list(self) -> list[dict[str, Any]]:
        """List available UCII identities asynchronously."""

        response = await self._transport.request(
            "GET",
            "/v1/identity",
        )

        return response.json()
