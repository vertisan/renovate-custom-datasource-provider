"""Provider registry for managing all available providers."""

from loguru import logger

from renovate_datasource.core.base import BaseProvider


class ProviderRegistry:
    """Registry for managing datasource providers."""

    def __init__(self) -> None:
        """Initialize the provider registry."""
        self._providers: dict[str, type[BaseProvider]] = {}
        self.logger = logger.bind(component="ProviderRegistry")

    def register(self, provider_class: type[BaseProvider]) -> None:
        """
        Register a provider class.

        Args:
            provider_class: Provider class to register
        """
        # We need to instantiate temporarily to get the name
        default_config_class = type("ProviderConfig", (), {"output_dir": "."})
        config = provider_class.__annotations__.get("config", default_config_class)()
        temp_instance = provider_class(config)
        name = temp_instance.name
        self._providers[name] = provider_class
        self.logger.debug(f"Registered provider: {name}")

    def get_provider(self, name: str) -> type[BaseProvider] | None:
        """
        Get a provider class by name.

        Args:
            name: Provider name

        Returns:
            Provider class or None if not found
        """
        return self._providers.get(name)

    def get_all_providers(self) -> dict[str, type[BaseProvider]]:
        """
        Get all registered providers.

        Returns:
            Dictionary of provider name to provider class
        """
        return self._providers.copy()

    def list_provider_names(self) -> list[str]:
        """
        List all registered provider names.

        Returns:
            List of provider names
        """
        return list(self._providers.keys())


# Global registry instance
registry = ProviderRegistry()
