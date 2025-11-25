"""Red Hat Container Catalog provider."""

import re
from typing import Optional

from renovate_datasource.adapters.base_provider import BaseProvider
from renovate_datasource.adapters.http_client import HttpClient
from renovate_datasource.domain.entities import Manifest, Release
from renovate_datasource.domain.exceptions import FetchError


class RedHatCatalogProvider(BaseProvider):
    """Provider for Red Hat container versions from Container Catalog.

    Fetches available container versions from Red Hat's Pyxis API
    (Container Catalog).
    """

    name = "redhat-catalog"

    # Pattern to match versions like: 9.5-1734081738
    VERSION_PATTERN = re.compile(r"^\d+\.\d+-\d+$")

    def __init__(
        self,
        image_path: str = "ubi9/ubi",
        registry: str = "registry.access.redhat.com",
        http_client: Optional[HttpClient] = None,
    ) -> None:
        """Initialize Red Hat Container Catalog provider.

        Args:
            image_path: Full image path (e.g., 'ubi9/ubi', 'ubi9-minimal')
            registry: Container registry URL
            http_client: Optional HTTP client instance
        """
        super().__init__(http_client)
        self.image_path = image_path
        self.registry = registry

    def fetch_versions(self) -> list[str]:
        """Fetch available container versions from Docker Registry V2 API.

        Uses the Docker Registry V2 API to fetch all available tags.
        Filters to only include versions matching the pattern: major.minor-timestamp

        Returns:
            List of filtered version tags

        Raises:
            FetchError: If fetching fails
        """
        try:
            # Use Docker Registry V2 API to get all tags
            url = f"https://catalog.redhat.com/api/containers/v1/repositories/registry/{self.registry}/repository/{self.image_path}/images"

            data = self.http_client.get(url)

            # Extract tags from the response
            all_tags = data.get("tags", [])

            if not all_tags:
                raise FetchError(f"No tags found for {self.image_path}")

            # Filter tags to only include major.minor-timestamp format
            filtered_versions = [tag for tag in all_tags if self.VERSION_PATTERN.match(tag)]

            if not filtered_versions:
                raise FetchError(
                    f"No versions matching pattern found for {self.image_path}. "
                    f"Found {len(all_tags)} tags but none matched major.minor-timestamp format."
                )

            # Sort versions for consistent output
            return sorted(filtered_versions, reverse=True)

        except FetchError:
            # Re-raise FetchError as-is
            raise
        except Exception as e:
            raise FetchError(
                f"Failed to fetch Red Hat container versions for {self.image_path}: {e}"
            ) from e

    def create_manifest(self, versions: list[str]) -> Manifest:
        """Create manifest from container versions.

        Args:
            versions: List of version strings

        Returns:
            Manifest with container releases
        """
        releases = [Release(version=version) for version in versions]

        # Use the Pyxis API URL as the homepage since we can't hardcode IDs
        homepage_url = (
            f"https://catalog.redhat.com/api/containers/v1/repositories/"
            f"registry/{self.registry}/repository/{self.image_path}/images"
        )

        return Manifest(
            releases=releases,
            source_url=f"https://{self.registry}/{self.image_path}",
            homepage=homepage_url,
        )
