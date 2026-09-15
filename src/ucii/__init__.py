"""Public UCII Python SDK.

Only publication-approved interoperability contracts are exported here.
Private UCII trust, authority, enforcement, fleet, adoption, and provenance
implementation details are intentionally outside this package surface.
"""

from .errors import (
    UCIIAPIError,
    UCIIAuthenticationError,
    UCIIAuthorizationError,
    UCIIConfigurationError,
    UCIIConflictError,
    UCIIError,
    UCIIPaymentRequiredError,
    UCIIResourceNotFoundError,
    UCIIServiceError,
    UCIITransportError,
    UCIIValidationError,
)
from .participant import ParticipantContext
from .service_entitlement import (
    ENTITLEMENT_PROOF_VERSION,
    EntitlementProof,
    EntitlementProofChallenge,
    create_entitlement_proof,
    entitlement_proof_header_value,
    generate_entitlement_nonce,
)
from .signing import SigningProvider

__all__ = [
    "ENTITLEMENT_PROOF_VERSION",
    "EntitlementProof",
    "EntitlementProofChallenge",
    "ParticipantContext",
    "SigningProvider",
    "UCIIAPIError",
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
]
