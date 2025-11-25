"""Red Hat Container Catalog provider CLI command."""

from typing import Optional

import click

from renovate_datasource.adapters.http_client import HttpClient
from renovate_datasource.adapters.presenters import JsonPresenter
from renovate_datasource.adapters.providers.redhat_catalog import RedHatCatalogProvider
from renovate_datasource.infrastructure.cli.common import (
    handle_error,
    output_option,
    output_result,
    verbose_option,
)
from renovate_datasource.use_cases.generate_manifest import GenerateManifestUseCase


@click.command(name="redhat-catalog")
@click.option(
    "--image-path",
    default="ubi9/ubi",
    show_default=True,
    help="Container image path (e.g., 'ubi9/ubi', 'ubi9-minimal', 'ubi8/ubi')",
)
@click.option(
    "--registry",
    default="registry.access.redhat.com",
    show_default=True,
    help="Container registry URL",
)
@output_option
@verbose_option
def redhat_catalog_command(
    image_path: str,
    registry: str,
    output: Optional[str],
    verbose: bool,
) -> None:
    """Generate Renovate manifest for Red Hat container versions.

    Fetches available container versions from Red Hat's Container Catalog
    (Pyxis API) and outputs a Renovate-compatible JSON manifest.

    Only versions matching the pattern major.minor-timestamp are included.

    Examples:

        \b
        # Generate manifest for UBI 9
        renovate-datasource generate redhat-catalog

        \b
        # Generate manifest for UBI 9 Minimal
        renovate-datasource generate redhat-catalog --image-path ubi9-minimal

        \b
        # Generate manifest for UBI 8
        renovate-datasource generate redhat-catalog --image-path ubi8/ubi

        \b
        # Save to custom location
        renovate-datasource generate redhat-catalog --output custom.json
    """
    try:
        # Initialize dependencies
        http_client = HttpClient()
        provider = RedHatCatalogProvider(
            image_path=image_path,
            registry=registry,
            http_client=http_client,
        )

        # Execute use case
        use_case = GenerateManifestUseCase(provider)
        manifest = use_case.execute()

        # Generate default filename
        default_filename = f"redhat-catalog-{image_path}.json"

        # Present output
        json_output = JsonPresenter.present(manifest)
        output_result(json_output, output, default_filename=default_filename)

    except Exception as e:
        handle_error(e, verbose)
    finally:
        if "http_client" in locals():
            http_client.close()
