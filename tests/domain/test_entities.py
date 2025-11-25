"""Tests for domain entities."""

import json
from datetime import datetime

from renovate_datasource.domain.entities import Manifest, Release


class TestRelease:
    """Tests for Release entity."""

    def test_create_minimal_release(self):
        """Test creating a release with only required fields."""
        release = Release(version="1.0.0")

        assert release.version == "1.0.0"
        assert release.is_deprecated is None
        assert release.release_timestamp is None

    def test_create_full_release(self):
        """Test creating a release with all fields."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0)
        release = Release(
            version="1.0.0",
            is_deprecated=False,
            release_timestamp=timestamp,
            changelog_url="https://example.com/changelog",
            source_url="https://github.com/example/repo",
            digest="sha256:abc123",
            is_stable=True,
        )

        assert release.version == "1.0.0"
        assert release.is_deprecated is False
        assert release.release_timestamp == timestamp
        assert release.changelog_url == "https://example.com/changelog"

    def test_alias_fields(self):
        """Test that camelCase aliases work correctly."""
        release = Release(
            version="1.0.0",
            isDeprecated=True,
            changelogUrl="https://example.com",
        )

        assert release.is_deprecated is True
        assert release.changelog_url == "https://example.com"


class TestManifest:
    """Tests for Manifest entity."""

    def test_create_minimal_manifest(self):
        """Test creating a manifest with only required fields."""
        releases = [Release(version="1.0.0"), Release(version="2.0.0")]
        manifest = Manifest(releases=releases)

        assert len(manifest.releases) == 2
        assert manifest.source_url is None

    def test_create_full_manifest(self):
        """Test creating a manifest with all fields."""
        releases = [Release(version="1.0.0")]
        manifest = Manifest(
            releases=releases,
            source_url="https://github.com/example/repo",
            homepage="https://example.com",
            changelog_url="https://example.com/changelog",
        )

        assert len(manifest.releases) == 1
        assert manifest.source_url == "https://github.com/example/repo"
        assert manifest.homepage == "https://example.com"

    def test_to_json(self):
        """Test JSON serialization."""
        releases = [Release(version="1.0.0", is_deprecated=False)]
        manifest = Manifest(
            releases=releases,
            source_url="https://github.com/example/repo",
        )

        json_str = manifest.to_json()
        data = json.loads(json_str)

        assert "releases" in data
        assert len(data["releases"]) == 1
        assert data["releases"][0]["version"] == "1.0.0"
        assert data["releases"][0]["isDeprecated"] is False
        assert data["sourceUrl"] == "https://github.com/example/repo"

    def test_to_json_excludes_none(self):
        """Test that None values are excluded from JSON."""
        releases = [Release(version="1.0.0")]
        manifest = Manifest(releases=releases)

        json_str = manifest.to_json()
        data = json.loads(json_str)

        assert "sourceUrl" not in data
        assert "homepage" not in data
        assert "isDeprecated" not in data["releases"][0]
