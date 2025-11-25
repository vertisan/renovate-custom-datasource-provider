"""K3s provider CLI command."""

from typing import Optional

import click

from renovate_datasource.adapters.http_client import HttpClient
from renovate_datasource.adapters.presenters import JsonPresenter
from renovate_datasource.adapters.providers.k3s import K3sProvider
from renovate_datasource.infrastructure.cli.common import (
    handle_error,
    output_option,
    output_result,
    verbose_option,
)
from renovate_datasource.use_cases.generate_manifest import GenerateManifestUseCase


@click.command(name="k3s")
@click.option(
    "--include-prereleases",
    is_flag=True,
    help="Include pre-release versions",
)
@output_option
@verbose_option
def k3s_command(
    include_prereleases: bool,
    output: Optional[str],
    verbose: bool,
) -> None:
    """Generate Renovate manifest for K3s versions.

    Fetches available K3s Kubernetes distribution versions from GitHub
    releases and outputs a Renovate-compatible JSON manifest.

    Examples:

        \b
        # Generate manifest for stable K3s versions
        renovate-datasource k3s

        \b
        # Include pre-release versions
        renovate-datasource k3s --include-prereleases

        \b
        # Save to file
        renovate-datasource k3s --output k3s.json
    """
    try:
        # Initialize dependencies
        http_client = HttpClient()
        provider = K3sProvider(
            include_prereleases=include_prereleases,
            http_client=http_client,
        )

        # Execute use case
        use_case = GenerateManifestUseCase(provider)
        manifest = use_case.execute()

        # Generate default filename
        if include_prereleases:
            default_filename = "k3s-with-prereleases.json"
        else:
            default_filename = "k3s.json"

        # Present output
        json_output = JsonPresenter.present(manifest)
        output_result(json_output, output, default_filename=default_filename)

    except Exception as e:
        handle_error(e, verbose)
    finally:
        if "http_client" in locals():
            http_client.close()
