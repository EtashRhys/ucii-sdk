"""Public UCII participant-context contract.

A participant context identifies the durable UCII identity and credential
state used by one independently governed participant.

It does not grant authority, contain private signing material, define
authentication secrets, or establish fleet membership.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ParticipantContext:
    """Identity-bound public context for one UCII participant.

    The context describes which UCII identity and credential an application
    intends to use.

    Cryptographic signing authority remains supplied separately through a
    SigningProvider.

    Operating policy, authentication secrets, payment authority, lifecycle
authority, and fleet membership are intentionally outside this object.
    """

    identity_id: str
    credential_id: str
    public_key: bytes
