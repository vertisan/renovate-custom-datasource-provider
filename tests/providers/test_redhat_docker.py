"""Tests for Red Hat Docker provider."""

from pathlib import Path
from typing import Any
from unittest.mock import Mock

import httpx
import pytest

from renovate_datasource.providers.redhat_docker import (
    RedHatDockerConfig,
    RedHatDockerProvider,
)


class TestRedHatDockerConfig:
    """Tests for RedHatDockerConfig."""

    def test_default_config(self) -> None:
        """Test default configuration."""
        config = RedHatDockerConfig()
        assert config.output_dir == Path("./output")
        assert config.registry_url == "https://catalog.redhat.com/api/containers/v1"
        assert config.timeout == 30

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = RedHatDockerConfig(
            output_dir=Path("/tmp/output"),
            registry_url="https://custom.example.com",
            timeout=60,
        )
        assert config.output_dir == Path("/tmp/output")
        assert config.registry_url == "https://custom.example.com"
        assert config.timeout == 60


class TestRedHatDockerProvider:
    """Tests for RedHatDockerProvider."""

    @pytest.fixture
    def config(self, tmp_path: Path) -> RedHatDockerConfig:
        """Create test configuration."""
        return RedHatDockerConfig(output_dir=tmp_path)

    @pytest.fixture
    def provider(self, config: RedHatDockerConfig) -> RedHatDockerProvider:
        """Create provider instance."""
        return RedHatDockerProvider(config)

    def test_provider_name(self, provider: RedHatDockerProvider) -> None:
        """Test provider name."""
        assert provider.name == "redhat-docker"

    def test_fetch_image_tags_single_page(
        self, provider: RedHatDockerProvider, mocker: Any
    ) -> None:
        """Test fetching image tags with single page."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "data": [
                {
                    "repositories": [{"tags": [{"name": "latest"}]}],
                    "parsed_data": {"created": "2024-01-01T00:00:00Z"},
                },
                {
                    "repositories": [{"tags": [{"name": "9.0"}]}],
                    "parsed_data": {"created": "2024-01-02T00:00:00Z"},
                },
            ],
            "total": 2,
        }
        mock_response.raise_for_status = Mock()

        mocker.patch.object(provider.client, "get", return_value=mock_response)

        result = provider._fetch_image_tags("ubi9/ubi-minimal")

        assert len(result) == 2
        assert result[0]["repositories"][0]["tags"][0]["name"] == "latest"

    def test_fetch_image_tags_multiple_pages(
        self, provider: RedHatDockerProvider, mocker: Any
    ) -> None:
        """Test fetching image tags with multiple pages."""
        mock_responses = [
            Mock(
                json=lambda: {
                    "data": [{"repositories": [{"tags": [{"name": "tag1"}]}]}],
                    "total": 2,
                }
            ),
            Mock(
                json=lambda: {
                    "data": [{"repositories": [{"tags": [{"name": "tag2"}]}]}],
                    "total": 2,
                }
            ),
            Mock(json=lambda: {"data": [], "total": 2}),
        ]

        for mock_response in mock_responses:
            mock_response.raise_for_status = Mock()

        mocker.patch.object(provider.client, "get", side_effect=mock_responses)

        result = provider._fetch_image_tags("ubi9/ubi-minimal")

        assert len(result) == 2

    def test_parse_version_info_success(self, provider: RedHatDockerProvider) -> None:
        """Test parsing version info from image data."""
        image_data = {
            "repositories": [
                {
                    "tags": [{"name": "9.0"}, {"name": "latest"}],
                    "manifest_schema2_digest": "abc123",
                }
            ],
            "parsed_data": {"created": "2024-01-01T00:00:00Z"},
        }

        result = provider._parse_version_info(image_data)

        assert len(result) == 2
        assert result[0].version == "9.0"
        assert result[0].release_timestamp == "2024-01-01T00:00:00+00:00"
        assert result[0].digest == "sha256:abc123"
        assert result[1].version == "latest"

    def test_parse_version_info_no_tags(self, provider: RedHatDockerProvider) -> None:
        """Test parsing version info with no tags."""
        image_data = {"repositories": [{"tags": []}]}

        result = provider._parse_version_info(image_data)
        assert len(result) == 0

    def test_parse_version_info_invalid_timestamp(self, provider: RedHatDockerProvider) -> None:
        """Test parsing version info with invalid timestamp."""
        image_data = {
            "repositories": [{"tags": [{"name": "9.0"}]}],
            "parsed_data": {"created": "invalid"},
        }

        result = provider._parse_version_info(image_data)

        assert len(result) == 1
        assert result[0].version == "9.0"
        assert result[0].release_timestamp is None

    def test_fetch_versions_default_repositories(
        self, provider: RedHatDockerProvider, mocker: Any
    ) -> None:
        """Test fetch_versions with default repositories."""
        # Mock images
        mocker.patch.object(
            provider,
            "_fetch_image_tags",
            return_value=[
                {
                    "repositories": [
                        {
                            "tags": [{"name": "latest"}],
                            "manifest_schema2_digest": "abc123",
                        }
                    ],
                    "parsed_data": {"created": "2024-01-01T00:00:00Z"},
                }
            ],
        )

        results = provider.fetch_versions()

        assert len(results) >= 1
        # Should process default repositories

    def test_fetch_versions_custom_repositories(
        self, provider: RedHatDockerProvider, mocker: Any
    ) -> None:
        """Test fetch_versions with custom repositories."""
        # Mock images
        mocker.patch.object(
            provider,
            "_fetch_image_tags",
            return_value=[
                {
                    "repositories": [
                        {
                            "tags": [{"name": "1.0.0"}],
                            "manifest_schema2_digest": "xyz789",
                        }
                    ],
                    "parsed_data": {"created": "2024-01-01T00:00:00Z"},
                }
            ],
        )

        results = provider.fetch_versions(repositories=["custom-repo"])

        assert len(results) == 1
        assert results[0].package_name == "registry.access.redhat.com/custom-repo"

    def test_fetch_versions_repository_not_found(
        self, provider: RedHatDockerProvider, mocker: Any
    ) -> None:
        """Test fetch_versions when repository is not found."""
        mock_response = Mock()
        mock_response.status_code = 404
        error = httpx.HTTPStatusError("Not found", request=Mock(), response=mock_response)
        mock_response.raise_for_status.side_effect = error
        mocker.patch.object(provider.client, "get", return_value=mock_response)

        # Should not raise, just skip the repository
        results = provider.fetch_versions(repositories=["nonexistent"])
        assert len(results) == 0

    def test_fetch_versions_error_handling(
        self, provider: RedHatDockerProvider, mocker: Any
    ) -> None:
        """Test fetch_versions error handling."""
        mocker.patch.object(
            provider, "_fetch_image_tags", side_effect=Exception("Test error")
        )

        # Should not raise, just skip the repository
        results = provider.fetch_versions(repositories=["error-repo"])
        assert len(results) == 0

    def test_generate_output(
        self, provider: RedHatDockerProvider, mocker: Any, tmp_path: Path
    ) -> None:
        """Test generate_output creates JSON files."""
        # Mock images
        mocker.patch.object(
            provider,
            "_fetch_image_tags",
            return_value=[
                {
                    "repositories": [
                        {
                            "tags": [{"name": "1.0.0"}],
                            "manifest_schema2_digest": "def456",
                        }
                    ],
                    "parsed_data": {"created": "2024-01-01T00:00:00Z"},
                }
            ],
        )

        provider.generate_output(repositories=["test-repo"])

        # Check that output file was created
        output_file = tmp_path / "registry.access.redhat.com/test-repo.json"
        assert output_file.exists()
