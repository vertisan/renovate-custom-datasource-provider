"""Red Hat Docker provider for UBI images."""

from datetime import datetime
from typing import Any

import click
import httpx
from pydantic import Field

from renovate_datasource.cli import provider
from renovate_datasource.core.base import (
    BaseProvider,
    DatasourceOutput,
    ProviderConfig,
    VersionInfo,
)
from renovate_datasource.core.registry import registry


class RedHatDockerConfig(ProviderConfig):
    """Configuration for Red Hat Docker provider."""

    registry_url: str = Field(
        default="https://catalog.redhat.com/api/containers/v1",
        description="Red Hat Container Catalog API URL",
    )
    timeout: int = Field(default=30, description="HTTP request timeout in seconds")


class RedHatDockerProvider(BaseProvider):
    """Provider for Red Hat Docker images (UBI)."""

    config: RedHatDockerConfig

    def __init__(self, config: RedHatDockerConfig) -> None:
        """
        Initialize the Red Hat Docker provider.

        Args:
            config: Provider configuration
        """
        super().__init__(config)
        self.client = httpx.Client(timeout=config.timeout)

    @property
    def name(self) -> str:
        """Return the provider name."""
        return "redhat-docker"

    def _fetch_repository_data(self, repository: str) -> dict[str, Any] | None:
        """
        Fetch repository data from Red Hat Container Catalog.

        Args:
            repository: Repository name (e.g., 'ubi9/ubi-minimal')

        Returns:
            Repository data or None if not found
        """
        try:
            # Search for the repository
            search_url = (
                f"{self.config.registry_url}/repositories/registry/"
                f"registry.access.redhat.com/repository/{repository}"
            )
            self.logger.debug(f"Fetching repository data from: {search_url}")

            response = self.client.get(search_url)
            response.raise_for_status()

            data: dict[str, Any] = response.json()
            return data

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                self.logger.warning(f"Repository not found: {repository}")
                return None
            self.logger.error(f"HTTP error fetching repository {repository}: {e}")
            raise
        except Exception as e:
            self.logger.error(f"Error fetching repository {repository}: {e}")
            raise

    def _fetch_image_tags(self, repository_id: str) -> list[dict[str, Any]]:
        """
        Fetch image tags for a repository.

        Args:
            repository_id: Repository ID from the catalog

        Returns:
            List of tag data
        """
        try:
            tags_url = f"{self.config.registry_url}/repositories/id/{repository_id}/images"
            self.logger.debug(f"Fetching tags from: {tags_url}")

            all_tags = []
            page = 0
            page_size = 100

            while True:
                response = self.client.get(tags_url, params={"page_size": page_size, "page": page})
                response.raise_for_status()

                data = response.json()
                tags = data.get("data", [])

                if not tags:
                    break

                all_tags.extend(tags)

                # Check if there are more pages
                total = data.get("total", 0)
                if len(all_tags) >= total:
                    break

                page += 1

            self.logger.info(f"Found {len(all_tags)} tags for repository {repository_id}")
            return all_tags

        except Exception as e:
            self.logger.error(f"Error fetching tags for repository {repository_id}: {e}")
            raise

    def _parse_version_info(self, tag_data: dict[str, Any]) -> VersionInfo | None:
        """
        Parse version information from tag data.

        Args:
            tag_data: Tag data from API

        Returns:
            VersionInfo or None if tag should be skipped
        """
        try:
            # Get the first tag name (images can have multiple tags)
            tags = tag_data.get("repositories", [{}])[0].get("tags", [])
            if not tags:
                return None

            version = tags[0].get("name")
            if not version:
                return None

            # Parse timestamp
            parsed_date = tag_data.get("parsed_data", {}).get("created")
            release_timestamp = None
            if parsed_date:
                try:
                    dt = datetime.fromisoformat(parsed_date.replace("Z", "+00:00"))
                    release_timestamp = dt.isoformat()
                except Exception:
                    pass

            # Get digest
            digest = None
            manifest_schema2_digest = tag_data.get("manifest_schema2_digest")
            if manifest_schema2_digest:
                digest = f"sha256:{manifest_schema2_digest}"

            return VersionInfo(
                version=version,
                release_timestamp=release_timestamp,
                digest=digest,
            )

        except Exception as e:
            self.logger.warning(f"Error parsing tag data: {e}")
            return None

    def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
        """
        Fetch versions for Red Hat Docker images.

        Args:
            **kwargs: Keyword arguments
                repositories: List of repository names to fetch
                             (e.g., ['ubi9/ubi-minimal', 'ubi8'])

        Returns:
            List of datasource outputs
        """
        repositories: list[str] | None = kwargs.get("repositories")
        if not repositories:
            repositories = ["ubi9/ubi-minimal", "ubi8", "ubi9"]

        outputs = []

        for repo in repositories:
            try:
                self.logger.info(f"Processing repository: {repo}")

                # Fetch repository data
                repo_data = self._fetch_repository_data(repo)
                if not repo_data:
                    self.logger.warning(f"Skipping repository {repo}: not found")
                    continue

                repository_id = repo_data.get("_id")
                if not repository_id:
                    self.logger.warning(f"Skipping repository {repo}: no ID found")
                    continue

                # Fetch tags
                tags = self._fetch_image_tags(repository_id)

                # Parse versions
                versions = []
                for tag_data in tags:
                    version_info = self._parse_version_info(tag_data)
                    if version_info:
                        versions.append(version_info)

                # Sort versions by release timestamp (newest first)
                versions.sort(key=lambda v: v.release_timestamp or "", reverse=True)

                # Create output
                repo_encoded = repo.replace("/", "%2F")
                homepage_url = f"https://catalog.redhat.com/software/containers/{repo_encoded}"
                output = DatasourceOutput(
                    datasource="docker",
                    package_name=f"registry.access.redhat.com/{repo}",
                    versions=versions,
                    registry_url="https://catalog.redhat.com",
                    homepage=homepage_url,
                )

                outputs.append(output)
                self.logger.success(f"Processed {repo}: {len(versions)} versions found")

            except Exception as e:
                self.logger.error(f"Failed to process repository {repo}: {e}")
                # Continue with next repository
                continue

        return outputs


# Register the provider
registry.register(RedHatDockerProvider)


# Add CLI command for this provider
@provider.command("redhat-docker")
@click.option(
    "-r",
    "--repository",
    "repositories",
    multiple=True,
    help="Repository to fetch (can be specified multiple times). "
    "Examples: ubi9/ubi-minimal, ubi8, ubi9",
)
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(exists=False, path_type=str),
    help="Output directory for JSON files (overrides global option)",
)
@click.pass_context
def redhat_docker_command(
    ctx: click.Context,
    repositories: tuple[str, ...],
    output_dir: str | None,
) -> None:
    """Fetch versions for Red Hat Docker images (UBI)."""
    from pathlib import Path

    output_path = Path(output_dir) if output_dir else Path(ctx.obj["output_dir"])

    config = RedHatDockerConfig(output_dir=output_path)
    provider_instance = RedHatDockerProvider(config)

    # Convert tuple to list, use default if empty
    repo_list = list(repositories) if repositories else None

    provider_instance.generate_output(repositories=repo_list)
