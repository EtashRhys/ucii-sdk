"""Minimal public UCII SDK client.

This client intentionally exposes only publication-approved interoperability
namespaces. Private UCII trust, authority, enforcement, economic, fleet,
adoption, and provenance machinery is not part of this client surface.
"""

from __future__ import annotations

from .authorization import (
    AsyncAuthorizationNamespace,
    AuthorizationNamespace,
)
from ._transport import AsyncHTTPTransport, HTTPTransport
from .credentials import AsyncCredentialsNamespace, CredentialsNamespace
from .identity import AsyncIdentityNamespace, IdentityNamespace
from .verification import AsyncVerificationNamespace, VerificationNamespace
from .x402 import AsyncX402Namespace, X402Namespace


class UCIIClient:
    """Synchronous client for publication-approved UCII namespaces."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        self._transport = HTTPTransport(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
        )

        self.identity = IdentityNamespace(self._transport)
        self.authorization = AuthorizationNamespace(self._transport)
        self.credentials = CredentialsNamespace(self._transport)
        self.verification = VerificationNamespace(self._transport)
        self.x402 = X402Namespace(self._transport)

    def close(self) -> None:
        """Close the underlying HTTP transport."""
        self._transport.close()

    def __enter__(self) -> "UCIIClient":
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.close()


class AsyncUCIIClient:
    """Asynchronous client for publication-approved UCII namespaces."""

    def __init__(
        self,
        *,
        base_url: str,
        api_key: str | None = None,
        timeout: float = 30.0,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        self._transport = AsyncHTTPTransport(
            base_url=self.base_url,
            api_key=self.api_key,
            timeout=self.timeout,
        )

        self.identity = AsyncIdentityNamespace(self._transport)
        self.authorization = AsyncAuthorizationNamespace(self._transport)
        self.credentials = AsyncCredentialsNamespace(self._transport)
        self.verification = AsyncVerificationNamespace(self._transport)
        self.x402 = AsyncX402Namespace(self._transport)

    async def close(self) -> None:
        """Close the underlying HTTP transport."""
        await self._transport.close()

    async def __aenter__(self) -> "AsyncUCIIClient":
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()
