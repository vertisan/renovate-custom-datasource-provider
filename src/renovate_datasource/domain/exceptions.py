"""Domain-specific exceptions."""


class DomainError(Exception):
    """Base exception for all domain errors."""

    pass


class ProviderError(DomainError):
    """Raised when a provider encounters an error."""

    pass


class FetchError(ProviderError):
    """Raised when fetching data from a source fails."""

    pass


class ValidationError(DomainError):
    """Raised when data validation fails."""

    pass
