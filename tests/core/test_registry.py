"""Tests for provider registry."""

from typing import Any

from renovate_datasource.core.base import BaseProvider, DatasourceOutput, ProviderConfig
from renovate_datasource.core.registry import ProviderRegistry


class TestProviderRegistry:
    """Tests for ProviderRegistry."""

    class TestProvider1(BaseProvider):
        """Test provider 1."""

        config: ProviderConfig

        @property
        def name(self) -> str:
            return "test-provider-1"

        def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
            return []

    class TestProvider2(BaseProvider):
        """Test provider 2."""

        config: ProviderConfig

        @property
        def name(self) -> str:
            return "test-provider-2"

        def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
            return []

    def test_register_provider(self) -> None:
        """Test registering a provider."""
        registry = ProviderRegistry()
        registry.register(self.TestProvider1)

        assert "test-provider-1" in registry.list_provider_names()

    def test_register_multiple_providers(self) -> None:
        """Test registering multiple providers."""
        registry = ProviderRegistry()
        registry.register(self.TestProvider1)
        registry.register(self.TestProvider2)

        provider_names = registry.list_provider_names()
        assert "test-provider-1" in provider_names
        assert "test-provider-2" in provider_names
        assert len(provider_names) == 2

    def test_get_provider(self) -> None:
        """Test getting a provider by name."""
        registry = ProviderRegistry()
        registry.register(self.TestProvider1)

        provider_class = registry.get_provider("test-provider-1")
        assert provider_class == self.TestProvider1

    def test_get_nonexistent_provider(self) -> None:
        """Test getting a non-existent provider."""
        registry = ProviderRegistry()
        provider_class = registry.get_provider("nonexistent")
        assert provider_class is None

    def test_get_all_providers(self) -> None:
        """Test getting all providers."""
        registry = ProviderRegistry()
        registry.register(self.TestProvider1)
        registry.register(self.TestProvider2)

        providers = registry.get_all_providers()
        assert len(providers) == 2
        assert "test-provider-1" in providers
        assert "test-provider-2" in providers
        assert providers["test-provider-1"] == self.TestProvider1
        assert providers["test-provider-2"] == self.TestProvider2

    def test_list_provider_names(self) -> None:
        """Test listing provider names."""
        registry = ProviderRegistry()
        registry.register(self.TestProvider1)
        registry.register(self.TestProvider2)

        names = registry.list_provider_names()
        assert len(names) == 2
        assert "test-provider-1" in names
        assert "test-provider-2" in names
