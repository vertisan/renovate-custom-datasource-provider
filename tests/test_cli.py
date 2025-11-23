"""Tests for CLI functionality."""

from pathlib import Path
from typing import Any

import pytest
from click.testing import CliRunner

from renovate_datasource.cli import cli
from renovate_datasource.core.base import (
    BaseProvider,
    DatasourceOutput,
    ProviderConfig,
    VersionInfo,
)
from renovate_datasource.core.registry import ProviderRegistry


class TestCLI:
    """Tests for CLI commands."""

    @pytest.fixture
    def runner(self) -> CliRunner:
        """Create a CLI runner."""
        return CliRunner()

    @pytest.fixture
    def test_registry(self) -> ProviderRegistry:
        """Create a test registry with test providers."""
        registry = ProviderRegistry()

        class TestProvider(BaseProvider):
            config: ProviderConfig

            @property
            def name(self) -> str:
                return "test-provider"

            def fetch_versions(self, **kwargs: Any) -> list[DatasourceOutput]:
                return [
                    DatasourceOutput(
                        datasource="test",
                        package_name="test-package",
                        versions=[VersionInfo(version="1.0.0")],
                    )
                ]

        registry.register(TestProvider)
        return registry

    def test_cli_help(self, runner: CliRunner) -> None:
        """Test CLI help output."""
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Renovate Custom Datasource Provider" in result.output

    def test_cli_verbose_flag(self, runner: CliRunner) -> None:
        """Test CLI verbose flag."""
        result = runner.invoke(cli, ["-v", "list-providers"])
        assert result.exit_code == 0

    def test_cli_output_dir_option(self, runner: CliRunner, tmp_path: Path) -> None:
        """Test CLI output directory option."""
        result = runner.invoke(cli, ["-o", str(tmp_path), "list-providers"])
        assert result.exit_code == 0

    def test_list_providers_command(self, runner: CliRunner) -> None:
        """Test list-providers command."""
        result = runner.invoke(cli, ["list-providers"])
        assert result.exit_code == 0

    def test_list_providers_with_registered(
        self, runner: CliRunner, test_registry: ProviderRegistry
    ) -> None:
        """Test list-providers with registered providers."""
        # The test_registry fixture registers providers, but we need to import
        # the providers module to ensure they are registered in the global registry
        from renovate_datasource.core.registry import registry

        # Clear and use test registry
        original_providers = registry._providers.copy()
        registry._providers = test_registry._providers

        try:
            result = runner.invoke(cli, ["list-providers"])
            assert result.exit_code == 0
            assert "test-provider" in result.output or "redhat-docker" in result.output
        finally:
            registry._providers = original_providers
