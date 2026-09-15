"""Public UCII SDK exception hierarchy."""

from __future__ import annotations

from typing import Any


class UCIIError(Exception):
    """Base exception for all public UCII SDK errors."""

    def __init__(
        self,
        message: str,
        *,
        error_code: str | None = None,
        request_id: str | None = None,
        status_code: int | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.request_id = request_id
        self.status_code = status_code
        self.details = dict(details) if details is not None else None

    def __str__(self) -> str:
        return self.message


class UCIIConfigurationError(UCIIError):
    """Raised when SDK configuration is invalid."""


class UCIITransportError(UCIIError):
    """Raised when an SDK transport operation fails."""


class UCIIAPIError(UCIIError):
    """Base class for errors returned by the UCII API."""


class UCIIAuthenticationError(UCIIAPIError):
    """Raised when API authentication fails."""


class UCIIAuthorizationError(UCIIAPIError):
    """Raised when API authorization fails."""


class UCIIPaymentRequiredError(UCIIAPIError):
    """Raised when an API operation requires x402 payment."""


class UCIIValidationError(UCIIAPIError):
    """Raised when API request validation fails."""


class UCIIResourceNotFoundError(UCIIAPIError):
    """Raised when an API resource cannot be found."""


class UCIIConflictError(UCIIAPIError):
    """Raised when an API operation conflicts with current state."""


class UCIIServiceError(UCIIAPIError):
    """Raised when the UCII service reports an internal failure."""
