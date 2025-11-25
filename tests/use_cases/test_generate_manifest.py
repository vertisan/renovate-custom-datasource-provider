"""Tests for GenerateManifestUseCase."""

import pytest
from renovate_datasource.domain.entities import Manifest, Release
from renovate_datasource.domain.exceptions import FetchError, ProviderError
from renovate_datasource.use_cases.generate_manifest import GenerateManifestUseCase


class MockProvider:
    """Mock provider for testing."""

    name = "test-provider"

    def __init__(self, versions=None, should_fail=False):
        self._versions = versions if versions is not None else ["1.0.0", "2.0.0"]
        self._should_fail = should_fail

    def fetch_versions(self):
        if self._should_fail:
            raise FetchError("Failed to fetch")
        return self._versions

    def create_manifest(self, versions):
        releases = [Release(version=v) for v in versions]
        return Manifest(releases=releases)


class TestGenerateManifestUseCase:
    """Tests for GenerateManifestUseCase."""

    def test_execute_success(self):
        """Test successful manifest generation."""
        provider = MockProvider(versions=["1.0.0", "2.0.0"])
        use_case = GenerateManifestUseCase(provider)

        manifest = use_case.execute()

        assert isinstance(manifest, Manifest)
        assert len(manifest.releases) == 2
        assert manifest.releases[0].version == "1.0.0"

    def test_execute_with_fetch_error(self):
        """Test handling of fetch errors."""
        provider = MockProvider(should_fail=True)
        use_case = GenerateManifestUseCase(provider)

        with pytest.raises(FetchError):
            use_case.execute()

    def test_execute_with_no_versions(self):
        """Test that empty versions result in a manifest with no releases."""
        provider = MockProvider(versions=[])
        use_case = GenerateManifestUseCase(provider)

        # Empty versions list should raise an error
        with pytest.raises(ProviderError, match="returned no versions"):
            use_case.execute()

    def test_execute_with_unexpected_error(self):
        """Test handling of unexpected errors."""

        class BrokenProvider:
            name = "broken"

            def fetch_versions(self):
                raise RuntimeError("Unexpected error")

            def create_manifest(self, versions):
                pass

        provider = BrokenProvider()
        use_case = GenerateManifestUseCase(provider)

        with pytest.raises(ProviderError, match="Unexpected error"):
            use_case.execute()
