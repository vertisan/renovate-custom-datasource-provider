"""Main CLI entry point with command auto-discovery."""

import click

from renovate_datasource.infrastructure.cli.commands.k3s import k3s_command
from renovate_datasource.infrastructure.cli.commands.redhat_catalog import (
    redhat_catalog_command,
)


@click.group()
@click.version_option(version="0.1.0", prog_name="renovate-datasource")
def cli() -> None:
    """Renovate Custom Datasource Provider.

    Generate Renovate-compatible custom datasource manifests from
    various version sources.
    """
    pass


@cli.group()
def generate() -> None:
    """Generate Renovate datasource manifests.

    Commands in this group fetch version data from various sources
    and generate Renovate-compatible JSON manifests.
    """
    pass


# Register provider commands under the generate group
generate.add_command(redhat_catalog_command)
generate.add_command(k3s_command)


if __name__ == "__main__":
    cli()
