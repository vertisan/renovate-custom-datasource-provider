"""Tests for core base classes."""

import json
from pathlib import Path
from typing import Any

import pytest

from renovate_datasource.core.base import (
    BaseProvider,
    DatasourceOutput,
    ProviderConfig,
    VersionInfo,
)


class TestVersionInfo:
    """Tests for VersionInfo model."""

    def test_version_info_minimal(self) -> None:
        """Test VersionInfo with minimal required fields."""
        version_info = VersionInfo(version="1.0.0")
        assert version_info.version == "1.0.0"
        assert version_info.release_timestamp is None
        assert version_info.digest is None

    def test_version_info_full(self) -> None:
        """Test VersionInfo with all fields."""
        version_info = VersionInfo(
            version="1.0.0",
            release_timestamp="2024-01-01T00:00:00Z",
            registry_url="https://registry.example.com",
            source_url="https://github.com/example/repo",
            digest="sha256:abc123",
            homepage="https://example.com",
            changelog_url="https://example.com/changelog",
        )
        assert version_info.version == "1.0.0"
        assert version_info.release_timestamp == "2024-01-01T00:00:00Z"
        assert version_info.digest == "sha256:abc123"


class TestDatasourceOutput:
    """Tests for DatasourceOutput model."""

    def test_datasource_output_minimal(self) -> None:
        """Test DatasourceOutput with minimal required fields."""
        output = DatasourceOutput(
            datasource="docker",
            package_name="test/package",
        )
        assert output.datasource == "docker"
        assert output.package_name == "test/package"
        assert output.versions == []

    def test_datasource_output_with_versions(self) -> None:
        """Test DatasourceOutput with versions."""
        versions = [
            VersionInfo(version="1.0.0"),
            VersionInfo(version="1.1.0"),
        ]
        output = DatasourceOutput(
            datasource="docker",
            package_name="test/package",
            versions=versions,
        )
        assert len(output.versions) == 2
        assert output.versions[0].version == "1.0.0"

    def test_datasource_output_json_serialization(self) -> None:
        """Test JSON serialization with proper aliases."""
        versions = [VersionInfo(version="1.0.0")]
        output = DatasourceOutput(
            datasource="docker",
            package_name="test/package",
            versions=versions,
            source_url="https://github.com/example/repo",
            registry_url="https://registry.example.com",
        )

        json_data = json.loads(output.model_dump_json(by_alias=True, exclude_none=True))

        assert json_data["packageName"] == "test/package"
        assert json_data["datasource"] == "docker"
        assert json_data["sourceUrl"] == "https://github.com/example/repo"
        assert json_data["registryUrl"] == "https://registry.example.com"
        assert len(json_data["versions"]) == 1


class TestProviderConfig:
    """Tests for ProviderConfig."""

    def test_provider_config_default(self) -> None:
        """Test ProviderConfig with default values."""
        config = ProviderConfig()
        assert config.output_dir == Path("./output")

    def test_provider_config_custom(self) -> None:
        """Test ProviderConfig with custom output directory."""
        config = ProviderConfig(output_dir=Path("/tmp/test"))
        assert config.output_dir == Path("/tmp/test")

    def test_ensure_output_dir(self, tmp_path: Path) -> None:
        """Test ensure_output_dir creates directory."""
        output_dir = tmp_path / "output"
        config = ProviderConfig(output_dir=output_dir)

        assert not output_dir.exists()
        config.ensure_output_dir()
        assert output_dir.exists()
        assert output_dir.is_dir()


class TestBaseProvider:
    """Tests for BaseProvider."""

    class TestProvider(BaseProvider):
        """Test provider implementation."""

        @property
        def name(self) -> str:
            return "test-provider"

        def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
            return [
                DatasourceOutput(
                    datasource="test",
                    package_name="test/package",
                    versions=[VersionInfo(version="1.0.0")],
                )
            ]

    def test_provider_initialization(self) -> None:
        """Test provider initialization."""
        config = ProviderConfig()
        provider = self.TestProvider(config)

        assert provider.config == config
        assert provider.name == "test-provider"

    def test_generate_output(self, tmp_path: Path) -> None:
        """Test generate_output creates JSON files."""
        config = ProviderConfig(output_dir=tmp_path)
        provider = self.TestProvider(config)

        provider.generate_output()

        output_file = tmp_path / "test/package.json"
        assert output_file.exists()

        with open(output_file) as f:
            data = json.load(f)

        assert data["packageName"] == "test/package"
        assert data["datasource"] == "test"
        assert len(data["versions"]) == 1
        assert data["versions"][0]["version"] == "1.0.0"

    def test_generate_output_multiple_packages(self, tmp_path: Path) -> None:
        """Test generate_output with multiple packages."""

        class MultiPackageProvider(BaseProvider):
            @property
            def name(self) -> str:
                return "multi-provider"

            def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
                return [
                    DatasourceOutput(
                        datasource="test",
                        package_name="package1",
                        versions=[VersionInfo(version="1.0.0")],
                    ),
                    DatasourceOutput(
                        datasource="test",
                        package_name="package2",
                        versions=[VersionInfo(version="2.0.0")],
                    ),
                ]

        config = ProviderConfig(output_dir=tmp_path)
        provider = MultiPackageProvider(config)

        provider.generate_output()

        assert (tmp_path / "package1.json").exists()
        assert (tmp_path / "package2.json").exists()

    def test_generate_output_error_handling(self, tmp_path: Path) -> None:
        """Test generate_output error handling."""

        class ErrorProvider(BaseProvider):
            @property
            def name(self) -> str:
                return "error-provider"

            def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
                raise ValueError("Test error")

        config = ProviderConfig(output_dir=tmp_path)
        provider = ErrorProvider(config)

        with pytest.raises(ValueError, match="Test error"):
            provider.generate_output()
