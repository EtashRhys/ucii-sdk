"""Public UCII x402 discovery and pricing contracts.

This module intentionally exposes only the read-only interoperability surface
required for external clients to discover UCII x402 service metadata and
pricing.

Settlement observability, receipt history, settlement verification, replay
protection, adapters, and other economic enforcement machinery remain outside
the public SDK surface.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class X402Operation:
    """Public x402 operation contract."""

    method: str
    endpoint: str
    amount: float
    currency: str | None = None
    network: str | None = None


@dataclass(frozen=True, slots=True)
class X402TrustModel:
    """Public x402 trust-model contract."""

    identity_represents: str
    credential_represents: str
    private_keys_stored: bool


@dataclass(frozen=True, slots=True)
class X402Cryptography:
    """Public x402 cryptography contract."""

    post_quantum_supported: bool
    signature_algorithms: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class X402Service:
    """Public x402 service metadata contract."""

    name: str
    short_name: str
    version: str
    api_version: str
    category: str
    protocol: str
    payment_flow: str
    discovery_endpoint: str
    pricing_endpoint: str
    trust_model: X402TrustModel
    cryptography: X402Cryptography
    capabilities: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class X402Info:
    """Public representation of /v1/x402/info."""

    protocol: str
    service: X402Service
    operations: tuple[X402Operation, ...]


@dataclass(frozen=True, slots=True)
class X402Pricing:
    """Public representation of /v1/x402/pricing."""

    protocol: str
    currency: str
    network: str
    operations: tuple[X402Operation, ...]


def _operation(payload: dict[str, Any]) -> X402Operation:
    return X402Operation(
        method=payload["method"],
        endpoint=payload["endpoint"],
        amount=payload["amount"],
        currency=payload.get("currency"),
        network=payload.get("network"),
    )


def _service(payload: dict[str, Any]) -> X402Service:
    trust = payload["trust_model"]
    crypto = payload["cryptography"]

    return X402Service(
        name=payload["name"],
        short_name=payload["short_name"],
        version=payload["version"],
        api_version=payload["api_version"],
        category=payload["category"],
        protocol=payload["protocol"],
        payment_flow=payload["payment_flow"],
        discovery_endpoint=payload["discovery_endpoint"],
        pricing_endpoint=payload["pricing_endpoint"],
        trust_model=X402TrustModel(
            identity_represents=trust["identity_represents"],
            credential_represents=trust["credential_represents"],
            private_keys_stored=trust["private_keys_stored"],
        ),
        cryptography=X402Cryptography(
            post_quantum_supported=crypto["post_quantum_supported"],
            signature_algorithms=tuple(crypto["signature_algorithms"]),
        ),
        capabilities=tuple(payload["capabilities"]),
    )


def _info(payload: dict[str, Any]) -> X402Info:
    return X402Info(
        protocol=payload["protocol"],
        service=_service(payload["service"]),
        operations=tuple(
            _operation(operation)
            for operation in payload["operations"]
        ),
    )


def _pricing(payload: dict[str, Any]) -> X402Pricing:
    return X402Pricing(
        protocol=payload["protocol"],
        currency=payload["currency"],
        network=payload["network"],
        operations=tuple(
            _operation(operation)
            for operation in payload["operations"]
        ),
    )


class X402Namespace:
    """Thin synchronous x402 discovery and pricing namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    def info(self) -> X402Info:
        """Retrieve UCII x402 service information."""

        response = self._transport.request(
            "GET",
            "/v1/x402/info",
        )
        return _info(response.json())

    def pricing(self) -> X402Pricing:
        """Retrieve UCII x402 pricing information."""

        response = self._transport.request(
            "GET",
            "/v1/x402/pricing",
        )
        return _pricing(response.json())


class AsyncX402Namespace:
    """Thin asynchronous x402 discovery and pricing namespace."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    async def info(self) -> X402Info:
        """Retrieve UCII x402 service information asynchronously."""

        response = await self._transport.request(
            "GET",
            "/v1/x402/info",
        )
        return _info(response.json())

    async def pricing(self) -> X402Pricing:
        """Retrieve UCII x402 pricing information asynchronously."""

        response = await self._transport.request(
            "GET",
            "/v1/x402/pricing",
        )
        return _pricing(response.json())
