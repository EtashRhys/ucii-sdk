"""Public UCII service-entitlement proof contract.

A service-entitlement proof demonstrates that the holder of a specific UCII
credential signed a fresh presentation bound to one exact HTTP request.

The proof can satisfy only an applicable UCII economic-access policy. It does
not establish identity authority, controller authority, action authorization,
revocation authority, or execution authority.
"""

from __future__ import annotations

import base64
import json
import secrets
from dataclasses import dataclass
from datetime import datetime, timezone


ENTITLEMENT_PROOF_VERSION = "ucii-service-entitlement-proof-v1"


@dataclass(frozen=True, slots=True)
class EntitlementProofChallenge:
    """Fresh request-bound challenge for one entitlement presentation."""

    nonce: str
    subject_identity_id: str
    credential_fingerprint: str
    method: str
    path: str
    issued_at: str
    expires_at: str

    def __post_init__(self) -> None:
        required = {
            "nonce": self.nonce,
            "subject_identity_id": self.subject_identity_id,
            "credential_fingerprint": self.credential_fingerprint,
            "method": self.method,
            "path": self.path,
            "issued_at": self.issued_at,
            "expires_at": self.expires_at,
        }

        for name, value in required.items():
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"{name} must be a non-empty string")

        normalized_method = self.method.strip().upper()
        normalized_path = self.path.strip()

        if self.method != normalized_method:
            raise ValueError(
                "method must be canonical uppercase HTTP method"
            )

        if self.path != normalized_path:
            raise ValueError(
                "path must not contain surrounding whitespace"
            )

        if not self.path.startswith("/"):
            raise ValueError("path must be absolute")

        issued = _parse_timestamp(self.issued_at)
        expires = _parse_timestamp(self.expires_at)

        if expires <= issued:
            raise ValueError(
                "expires_at must be later than issued_at"
            )

    def canonical_message(self) -> str:
        """Return the deterministic signed representation."""

        payload = {
            "credential_fingerprint": self.credential_fingerprint,
            "expires_at": self.expires_at,
            "issued_at": self.issued_at,
            "method": self.method,
            "nonce": self.nonce,
            "path": self.path,
            "subject_identity_id": self.subject_identity_id,
            "version": ENTITLEMENT_PROOF_VERSION,
        }

        return json.dumps(
            payload,
            separators=(",", ":"),
            sort_keys=True,
        )

    def is_fresh(
        self,
        *,
        now: datetime | None = None,
    ) -> bool:
        """Return whether the challenge remains inside its validity window."""

        current = now or datetime.now(timezone.utc)

        if current.tzinfo is None:
            current = current.replace(tzinfo=timezone.utc)

        current = current.astimezone(timezone.utc)

        issued = _parse_timestamp(self.issued_at)
        expires = _parse_timestamp(self.expires_at)

        return issued <= current <= expires


@dataclass(frozen=True, slots=True)
class EntitlementProof:
    """Signed response to one EntitlementProofChallenge."""

    challenge: EntitlementProofChallenge
    signature: str

    def __post_init__(self) -> None:
        if not isinstance(self.signature, str) or not self.signature.strip():
            raise ValueError("signature must be a non-empty string")


def create_entitlement_proof(
    challenge: EntitlementProofChallenge,
    *,
    signing_provider: object,
) -> EntitlementProof:
    """Sign one fresh request-bound entitlement challenge."""

    if not isinstance(challenge, EntitlementProofChallenge):
        raise TypeError(
            "challenge must be an EntitlementProofChallenge"
        )

    if not challenge.is_fresh():
        raise ValueError(
            "entitlement proof challenge is not fresh"
        )

    sign = getattr(signing_provider, "sign", None)

    if not callable(sign):
        raise TypeError(
            "signing_provider must provide a callable sign method"
        )

    signature = sign(
        challenge.canonical_message().encode("utf-8")
    )

    if not isinstance(signature, bytes) or not signature:
        raise ValueError(
            "signing_provider must return non-empty signature bytes"
        )

    return EntitlementProof(
        challenge=challenge,
        signature=base64.b64encode(signature).decode("ascii"),
    )


def entitlement_proof_header_value(
    proof: EntitlementProof,
) -> str:
    """Serialize a proof for X-UCII-Service-Entitlement."""

    if not isinstance(proof, EntitlementProof):
        raise TypeError("proof must be an EntitlementProof")

    challenge = proof.challenge

    payload = {
        "challenge": {
            "nonce": challenge.nonce,
            "subject_identity_id": challenge.subject_identity_id,
            "credential_fingerprint": challenge.credential_fingerprint,
            "method": challenge.method,
            "path": challenge.path,
            "issued_at": challenge.issued_at,
            "expires_at": challenge.expires_at,
        },
        "signature": proof.signature,
    }

    encoded = json.dumps(
        payload,
        separators=(",", ":"),
        sort_keys=True,
    ).encode("utf-8")

    return base64.urlsafe_b64encode(encoded).decode("ascii")


def _economic_access_headers(
    *,
    payment_proof: dict | None = None,
    service_entitlement_proof: EntitlementProof | None = None,
) -> dict[str, dict[str, str]]:
    """Construct exactly one UCII economic-access presentation.

    Ordinary x402 payment and service entitlement are independent ways to
    satisfy the economic gate. A request must not present both mechanisms
    simultaneously.
    """

    if (
        payment_proof is not None
        and service_entitlement_proof is not None
    ):
        raise ValueError(
            "payment_proof and service_entitlement_proof "
            "are mutually exclusive"
        )

    if payment_proof is not None:
        return {
            "headers": {
                "x-payment-proof": json.dumps(
                    payment_proof,
                    separators=(",", ":"),
                    sort_keys=True,
                ),
            },
        }

    if service_entitlement_proof is not None:
        return {
            "headers": {
                "X-UCII-Service-Entitlement": (
                    entitlement_proof_header_value(
                        service_entitlement_proof
                    )
                ),
            },
        }

    return {}


def generate_entitlement_nonce() -> str:
    """Generate a cryptographically strong one-time entitlement nonce."""

    return secrets.token_urlsafe(32)


def _parse_timestamp(value: str) -> datetime:
    """Parse a timezone-aware ISO-8601 timestamp into UTC."""

    try:
        parsed = datetime.fromisoformat(
            value.replace("Z", "+00:00")
        )
    except ValueError as exc:
        raise ValueError(
            "entitlement proof timestamps must be valid ISO-8601"
        ) from exc

    if parsed.tzinfo is None:
        raise ValueError(
            "entitlement proof timestamps must include timezone information"
        )

    return parsed.astimezone(timezone.utc)
