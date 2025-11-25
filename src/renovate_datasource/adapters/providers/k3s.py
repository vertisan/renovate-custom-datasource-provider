"""K3s Kubernetes distribution provider."""

from typing import Optional

from renovate_datasource.adapters.base_provider import BaseProvider
from renovate_datasource.adapters.http_client import HttpClient
from renovate_datasource.domain.entities import Manifest, Release
from renovate_datasource.domain.exceptions import FetchError


class K3sProvider(BaseProvider):
    """Provider for K3s Kubernetes distribution versions.

    Fetches available K3s versions from GitHub releases.
    """

    name = "k3s"

    def __init__(
        self,
        include_prereleases: bool = False,
        http_client: Optional[HttpClient] = None,
    ) -> None:
        """Initialize K3s provider.

        Args:
            include_prereleases: Whether to include pre-release versions
            http_client: Optional HTTP client instance
        """
        super().__init__(http_client)
        self.include_prereleases = include_prereleases

    def fetch_versions(self) -> list[str]:
        """Fetch available K3s versions from GitHub.

        Returns:
            List of K3s version tags

        Raises:
            FetchError: If fetching fails
        """
        try:
            # Fetch from GitHub API
            url = "https://api.github.com/repos/k3s-io/k3s/releases"
            headers = {"Accept": "application/vnd.github.v3+json"}

            data = self.http_client.get(url, headers=headers)

            versions = []
            for release in data:
                # Skip pre-releases if not requested
                if release.get("prerelease") and not self.include_prereleases:
                    continue

                tag = release.get("tag_name")
                if tag:
                    versions.append(tag)

            return versions

        except Exception as e:
            raise FetchError(f"Failed to fetch K3s versions: {e}") from e

    def create_manifest(self, versions: list[str]) -> Manifest:
        """Create manifest from K3s versions.

        Args:
            versions: List of version strings

        Returns:
            Manifest with K3s releases
        """
        releases = [Release(version=version) for version in versions]

        return Manifest(
            releases=releases,
            source_url="https://github.com/k3s-io/k3s",
            homepage="https://k3s.io",
            changelog_url="https://github.com/k3s-io/k3s/releases",
        )
