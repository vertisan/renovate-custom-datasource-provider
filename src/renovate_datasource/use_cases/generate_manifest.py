"""Use case for generating Renovate datasource manifests."""

from renovate_datasource.domain.entities import Manifest
from renovate_datasource.domain.exceptions import FetchError, ProviderError
from renovate_datasource.domain.provider_protocol import ProviderProtocol


class GenerateManifestUseCase:
    """Orchestrates the process of generating a Renovate manifest.

    This use case encapsulates the business logic of:
    1. Fetching versions from a provider
    2. Creating a manifest from those versions
    3. Handling errors appropriately
    """

    def __init__(self, provider: ProviderProtocol) -> None:
        """Initialize the use case with a provider.

        Args:
            provider: Provider implementation following ProviderProtocol
        """
        self.provider = provider

    def execute(self) -> Manifest:
        """Execute the manifest generation process.

        Returns:
            Generated Manifest object

        Raises:
            FetchError: If version fetching fails
            ProviderError: If manifest creation fails
        """
        try:
            # Fetch versions from the provider
            versions = self.provider.fetch_versions()

            if not versions:
                raise ProviderError(f"Provider '{self.provider.name}' returned no versions")

            # Create manifest from versions
            manifest = self.provider.create_manifest(versions)

            return manifest

        except FetchError:
            # Re-raise fetch errors as-is
            raise
        except ProviderError:
            # Re-raise provider errors as-is
            raise
        except Exception as e:
            # Wrap unexpected errors
            raise ProviderError(
                f"Unexpected error generating manifest for '{self.provider.name}': {e}"
            ) from e
