"""Public UCII authorization-check boundary."""

from __future__ import annotations

from typing import Any


def _payload(
    *,
    token: str,
    identity_id: str,
    credential_fingerprint: str,
    operation: str,
    message: str,
    signature: str,
) -> dict[str, Any]:
    """Construct an authorization-check request payload."""

    return {
        "token": token,
        "identity_id": identity_id,
        "credential_fingerprint": credential_fingerprint,
        "operation": operation,
        "message": message,
        "signature": signature,
    }


class AuthorizationNamespace:
    """Thin synchronous non-executing authorization boundary."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    def check(
        self,
        *,
        token: str,
        identity_id: str,
        credential_fingerprint: str,
        operation: str,
        message: str,
        signature: str,
    ) -> dict[str, Any]:
        """Evaluate authorization without executing the operation."""

        response = self._transport.request(
            "POST",
            "/v1/authorization/check",
            json=_payload(
                token=token,
                identity_id=identity_id,
                credential_fingerprint=credential_fingerprint,
                operation=operation,
                message=message,
                signature=signature,
            ),
        )

        return response.json()


class AsyncAuthorizationNamespace:
    """Thin asynchronous non-executing authorization boundary."""

    def __init__(self, transport: Any) -> None:
        self._transport = transport

    async def check(
        self,
        *,
        token: str,
        identity_id: str,
        credential_fingerprint: str,
        operation: str,
        message: str,
        signature: str,
    ) -> dict[str, Any]:
        """Evaluate authorization without executing the operation."""

        response = await self._transport.request(
            "POST",
            "/v1/authorization/check",
            json=_payload(
                token=token,
                identity_id=identity_id,
                credential_fingerprint=credential_fingerprint,
                operation=operation,
                message=message,
                signature=signature,
            ),
        )

        return response.json()
