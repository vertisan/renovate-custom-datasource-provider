"""Provider protocol defining the contract for all datasource providers."""

from typing import Protocol, runtime_checkable

from renovate_datasource.domain.entities import Manifest


@runtime_checkable
class ProviderProtocol(Protocol):
    """Protocol that all providers must implement.

    This defines the contract for provider implementations without
    requiring inheritance, following Clean Architecture principles.
    """

    name: str
    """Unique name identifying the provider."""

    def fetch_versions(self) -> list[str]:
        """Fetch available versions from the datasource.

        Returns:
            List of version strings

        Raises:
            FetchError: If fetching fails
        """
        ...

    def create_manifest(self, versions: list[str]) -> Manifest:
        """Create a Renovate-compatible manifest from versions.

        Args:
            versions: List of version strings

        Returns:
            Manifest object ready for serialization

        Raises:
            ValidationError: If manifest creation fails
        """
        ...
