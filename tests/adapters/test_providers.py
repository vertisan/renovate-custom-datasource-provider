"""Tests for provider implementations."""

import pytest
from renovate_datasource.adapters.providers.k3s import K3sProvider
from renovate_datasource.adapters.providers.redhat_catalog import RedHatCatalogProvider
from renovate_datasource.domain.entities import Manifest


class TestRedHatCatalogProvider:
    """Tests for RedHatCatalogProvider."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = RedHatCatalogProvider(image_path="ubi9/ubi")

        assert provider.name == "redhat-catalog"
        assert provider.image_path == "ubi9/ubi"

    @pytest.mark.integration
    def test_fetch_versions_integration(self):
        """Integration test for fetching real versions from Pyxis API."""
        provider = RedHatCatalogProvider(image_path="ubi9-minimal")
        versions = provider.fetch_versions()

        assert isinstance(versions, list)
        assert len(versions) > 0
        # All versions should match major.minor-timestamp pattern
        import re

        pattern = re.compile(r"^\d+\.\d+-\d+$")
        assert all(pattern.match(v) for v in versions)

    def test_create_manifest(self):
        """Test manifest creation."""
        provider = RedHatCatalogProvider(image_path="ubi9/ubi")
        versions = ["9.5-1734081738", "9.4-1234567890"]
        manifest = provider.create_manifest(versions)

        assert isinstance(manifest, Manifest)
        assert len(manifest.releases) == 2
        assert manifest.source_url is not None
        assert manifest.homepage is not None
        assert "pyxis" in manifest.homepage.lower() or "catalog.redhat.com" in manifest.homepage


class TestK3sProvider:
    """Tests for K3sProvider."""

    def test_initialization(self):
        """Test provider initialization."""
        provider = K3sProvider(include_prereleases=True)

        assert provider.name == "k3s"
        assert provider.include_prereleases is True

    def test_create_manifest(self):
        """Test manifest creation."""
        provider = K3sProvider()
        versions = ["v1.27.0+k3s1", "v1.26.5+k3s1"]
        manifest = provider.create_manifest(versions)

        assert isinstance(manifest, Manifest)
        assert len(manifest.releases) == 2
        assert manifest.source_url == "https://github.com/k3s-io/k3s"
        assert manifest.homepage == "https://k3s.io"

    @pytest.mark.integration
    def test_fetch_versions_integration(self):
        """Integration test for fetching real K3s versions."""
        provider = K3sProvider(include_prereleases=False)
        versions = provider.fetch_versions()

        assert isinstance(versions, list)
        assert len(versions) > 0
        # K3s versions typically contain '+k3s'
        assert any("+k3s" in v for v in versions)
