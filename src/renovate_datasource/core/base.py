"""Base classes and interfaces for providers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

from loguru import logger
from pydantic import BaseModel, Field


class VersionInfo(BaseModel):
    """Information about a specific version."""

    version: str = Field(..., description="Version string")
    release_timestamp: str | None = Field(None, description="Release timestamp in ISO format")
    registry_url: str | None = Field(None, description="URL to the registry")
    source_url: str | None = Field(None, description="URL to the source code")
    digest: str | None = Field(None, description="Digest/hash of the artifact")
    homepage: str | None = Field(None, description="Homepage URL")
    changelog_url: str | None = Field(None, description="Changelog URL")


class DatasourceOutput(BaseModel):
    """Output format for Renovate custom datasource."""

    datasource: str = Field(..., description="Datasource type (e.g., 'docker')")
    package_name: str = Field(..., alias="packageName", description="Package name")
    versions: list[VersionInfo] = Field(default_factory=list, description="List of versions")
    homepage: str | None = Field(None, description="Homepage URL")
    source_url: str | None = Field(None, alias="sourceUrl", description="Source code URL")
    registry_url: str | None = Field(None, alias="registryUrl", description="Registry URL")

    model_config = {"populate_by_name": True}


class ProviderConfig(BaseModel):
    """Base configuration for providers."""

    output_dir: Path = Field(
        default=Path("./output"), description="Output directory for JSON files"
    )

    def ensure_output_dir(self) -> None:
        """Ensure output directory exists."""
        self.output_dir.mkdir(parents=True, exist_ok=True)


class BaseProvider(ABC):
    """Base class for all datasource providers."""

    def __init__(self, config: ProviderConfig) -> None:
        """
        Initialize the provider.

        Args:
            config: Provider configuration
        """
        self.config = config
        self.logger = logger.bind(provider=self.__class__.__name__)

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the provider name."""
        pass

    @abstractmethod
    def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
        """
        Fetch versions for the datasource.

        Args:
            **kwargs: Provider-specific arguments

        Returns:
            List of datasource outputs
        """
        pass

    def generate_output(self, **kwargs: Any) -> None:
        """
        Generate JSON output files for the datasource.

        Args:
            **kwargs: Provider-specific arguments
        """
        self.config.ensure_output_dir()

        try:
            self.logger.info(f"Starting version fetch for provider: {self.name}")
            outputs = self.fetch_versions(**kwargs)

            for output in outputs:
                output_file = self.config.output_dir / f"{output.package_name}.json"
                self.logger.info(f"Writing {len(output.versions)} versions to {output_file}")

                # Create parent directories if they don't exist
                output_file.parent.mkdir(parents=True, exist_ok=True)

                with open(output_file, "w") as f:
                    f.write(output.model_dump_json(by_alias=True, indent=2, exclude_none=True))

                self.logger.success(f"Successfully generated output for {output.package_name}")

            self.logger.success(
                f"Provider {self.name} completed successfully. "
                f"Generated {len(outputs)} output files."
            )

        except Exception as e:
            self.logger.error(f"Provider {self.name} failed with error: {e}")
            raise
