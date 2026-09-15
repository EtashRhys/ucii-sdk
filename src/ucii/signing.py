"""Public UCII signing-provider contract.

The UCII SDK does not own or persist private signing keys.

Applications supply a signing provider representing their authorized
custody boundary. That provider may be backed by software custody,
protected local signing, KMS, HSM, secure enclave, threshold signing,
remote signing infrastructure, or another compatible implementation.

The SDK consumes only the public verification key, algorithm identity,
and bounded signing operation exposed by the provider.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable


@runtime_checkable
class SigningProvider(Protocol):
    """Provider-neutral cryptographic signing boundary.

    Implementations retain responsibility for private-key custody and
    authorization of signing operations.

    UCII consumers MUST NOT assume that raw private-key export is
    available merely because a provider can produce signatures.
    """

    @property
    def algorithm(self) -> str:
        """Return the public algorithm identifier used by this signer."""
        ...

    @property
    def public_key(self) -> bytes:
        """Return the public verification-key material."""
        ...

    def sign(self, message: bytes) -> bytes:
        """Produce a signature for an authorized message."""
        ...
