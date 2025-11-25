"""Core domain entities representing Renovate datasource format."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class Release(BaseModel):
    """Represents a single version release in Renovate format.

    This is the core domain entity that maps to Renovate's expected
    release object structure.
    """

    version: str = Field(..., description="The version string (required)")
    is_deprecated: Optional[bool] = Field(
        None, alias="isDeprecated", description="Whether this version is deprecated"
    )
    release_timestamp: Optional[datetime] = Field(
        None, alias="releaseTimestamp", description="When the version was released"
    )
    changelog_url: Optional[str] = Field(
        None, alias="changelogUrl", description="URL to the changelog for this version"
    )
    source_url: Optional[str] = Field(None, alias="sourceUrl", description="Source repository URL")
    source_directory: Optional[str] = Field(
        None, alias="sourceDirectory", description="Directory within source repository"
    )
    digest: Optional[str] = Field(None, description="Hash/digest of the release")
    is_stable: Optional[bool] = Field(
        None, alias="isStable", description="Whether this is a stable release"
    )

    model_config = ConfigDict(populate_by_name=True)


class Manifest(BaseModel):
    """Represents the complete Renovate custom datasource manifest.

    This is the root entity that contains all releases and optional
    top-level metadata.
    """

    releases: list[Release] = Field(..., description="List of available releases")
    source_url: Optional[str] = Field(
        None, alias="sourceUrl", description="Default source repository URL"
    )
    source_directory: Optional[str] = Field(
        None, alias="sourceDirectory", description="Default source directory"
    )
    changelog_url: Optional[str] = Field(
        None, alias="changelogUrl", description="Default changelog URL"
    )
    homepage: Optional[str] = Field(None, description="Project homepage URL")

    model_config = ConfigDict(populate_by_name=True)

    def to_json(self, **kwargs: dict) -> str:
        """Export manifest as JSON string compatible with Renovate.

        Args:
            **kwargs: Additional arguments passed to model_dump_json

        Returns:
            JSON string representation
        """
        return self.model_dump_json(by_alias=True, exclude_none=True, **kwargs)
