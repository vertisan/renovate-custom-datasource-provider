"""Red Hat Docker provider for UBI images."""

from datetime import datetime
import sys
from typing import Any

import click
import httpx
from pydantic import Field

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

    def _fetch_image_tags(self, repository: str) -> list[dict[str, Any]]:
        """
        Fetch image tags for a repository.

        Args:
            repository: Repository name (e.g., 'ubi9/ubi-minimal')

        Returns:
            List of image data
        """
        try:
            images_url = (
                f"{self.config.registry_url}/repositories/registry/"
                f"registry.access.redhat.com/repository/{repository}/images"
            )
            self.logger.debug(f"Fetching images from: {images_url}")

            all_images = []
            page = 0
            page_size = 100

            while True:
                response = self.client.get(
                    images_url, params={"page_size": page_size, "page": page}
                )
                response.raise_for_status()

                data = response.json()
                images = data.get("data", [])

                if not images:
                    break

                all_images.extend(images)

                # Check if there are more pages
                total = data.get("total", 0)
                if len(all_images) >= total:
                    break

                page += 1

            self.logger.info(f"Found {len(all_images)} images for repository {repository}")
            return all_images

        except Exception as e:
            self.logger.error(f"Error fetching images for repository {repository}: {e}")
            raise

    def _parse_version_info(self, image_data: dict[str, Any]) -> list[VersionInfo]:
        """
        Parse version information from image data.

        Args:
            image_data: Image data from API

        Returns:
            List of VersionInfo objects (one per tag)
        """
        versions: list[VersionInfo] = []
        try:
            # Get repository info
            repo_info = image_data.get("repositories", [{}])[0]
            tags = repo_info.get("tags", [])

            if not tags:
                return versions

            # Parse timestamp from image creation date
            parsed_date = image_data.get("parsed_data", {}).get("created")
            release_timestamp = None
            if parsed_date:
                try:
                    dt = datetime.fromisoformat(parsed_date.replace("Z", "+00:00"))
                    release_timestamp = dt.isoformat()
                except Exception:
                    pass

            # Get digest
            digest = None
            manifest_schema2_digest = repo_info.get("manifest_schema2_digest")
            if manifest_schema2_digest:
                digest = manifest_schema2_digest
                if not digest.startswith("sha256:"):
                    digest = f"sha256:{digest}"

            # Create a VersionInfo for each tag
            for tag in tags:
                tag_name = tag.get("name")
                if not tag_name:
                    continue

                versions.append(
                    VersionInfo(
                        version=tag_name,
                        release_timestamp=release_timestamp,
                        digest=digest,
                    )
                )

        except Exception as e:
            self.logger.warning(f"Error parsing image data: {e}")

        return versions

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
            self.logger.warning("No repositories has been provided!")
            sys.exit(0)

        outputs = []

        for repo in repositories:
            try:
                self.logger.info(f"Processing repository: {repo}")

                # Fetch images
                images = self._fetch_image_tags(repo)

                # Parse versions from images
                versions = []
                for image_data in images:
                    version_infos = self._parse_version_info(image_data)
                    versions.extend(version_infos)

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


def register_cli_command() -> None:
    """Register the CLI command for this provider."""
    from renovate_datasource.cli import provider

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
