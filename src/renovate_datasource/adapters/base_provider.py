"""Base provider class with common functionality."""

from abc import ABC, abstractmethod
from typing import Optional

from renovate_datasource.adapters.http_client import HttpClient
from renovate_datasource.domain.entities import Manifest


class BaseProvider(ABC):
    """Abstract base class for datasource providers.

    Provides common functionality like HTTP client management,
    while requiring subclasses to implement provider-specific logic.
    """

    name: str
    """Unique name identifying the provider. Must be set by subclasses."""

    def __init__(self, http_client: Optional[HttpClient] = None) -> None:
        """Initialize the provider with an HTTP client.

        Args:
            http_client: Optional HTTP client instance. If not provided,
                        a new client will be created and owned by this instance.
        """
        self.http_client = http_client or HttpClient()
        self._owns_client = http_client is None

    @abstractmethod
    def fetch_versions(self) -> list[str]:
        """Fetch available versions from the datasource.

        This method must be implemented by subclasses to fetch versions
        from their specific data source.

        Returns:
            List of version strings

        Raises:
            FetchError: If fetching fails
        """
        pass

    @abstractmethod
    def create_manifest(self, versions: list[str]) -> Manifest:
        """Create a Renovate-compatible manifest from versions.

        This method must be implemented by subclasses to create
        a manifest with provider-specific metadata.

        Args:
            versions: List of version strings

        Returns:
            Manifest object ready for serialization

        Raises:
            ValidationError: If manifest creation fails
        """
        pass

    def close(self) -> None:
        """Close the HTTP client if owned by this instance."""
        if self._owns_client and hasattr(self, "http_client"):
            self.http_client.close()

    def __del__(self) -> None:
        """Cleanup HTTP client on instance destruction."""
        self.close()

    def __enter__(self) -> "BaseProvider":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:  # type: ignore
        """Context manager exit."""
        self.close()
