"""CLI interface for renovate datasource providers."""

import sys
from pathlib import Path

import click
from loguru import logger

# Import all providers to ensure they are registered
from renovate_datasource import providers as _  # noqa: F401
from renovate_datasource.core.registry import registry


def setup_logging(verbose: bool = False) -> None:
    """
    Set up logging configuration.

    Args:
        verbose: Enable verbose logging
    """
    logger.remove()
    log_level = "DEBUG" if verbose else "INFO"
    log_format = (
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level: <8}</level> | "
        "<cyan>{extra[provider]}</cyan> | "
        "<level>{message}</level>"
    )
    logger.add(
        sys.stderr,
        format=log_format,
        level=log_level,
        colorize=True,
    )


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose logging")
@click.option(
    "-o",
    "--output-dir",
    type=click.Path(path_type=Path),
    default=Path("./output"),
    help="Output directory for JSON files",
)
@click.pass_context
def cli(ctx: click.Context, verbose: bool, output_dir: Path) -> None:
    """Renovate Custom Datasource Provider - Generate JSON datasources for Renovate."""
    setup_logging(verbose)
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["output_dir"] = output_dir


@cli.command()
@click.pass_context
def all_providers(ctx: click.Context) -> None:
    """Run all registered providers."""
    output_dir = ctx.obj["output_dir"]
    logger_main = logger.bind(provider="CLI")

    providers = registry.get_all_providers()
    if not providers:
        logger_main.warning("No providers registered")
        return

    logger_main.info(f"Running all {len(providers)} providers")

    success_count = 0
    failure_count = 0
    failed_providers = []

    for provider_name, provider_class in providers.items():
        try:
            logger_main.info(f"Processing provider: {provider_name}")

            # Get the provider's config class from annotations
            config_annotation = provider_class.__annotations__.get("config")
            if config_annotation is None:
                logger_main.error(f"Provider {provider_name} has no config annotation")
                continue
            config_class = config_annotation.__args__[0]
            config = config_class(output_dir=output_dir)
            provider_instance = provider_class(config)

            # Call generate_output with default arguments (provider-specific defaults)
            provider_instance.generate_output()

            success_count += 1
            logger_main.success(f"Provider {provider_name} completed successfully")

        except Exception as e:
            failure_count += 1
            failed_providers.append(provider_name)
            logger_main.error(
                f"Provider {provider_name} failed with error: {e}. "
                "Continuing with next provider..."
            )

    # Summary
    logger_main.info("-" * 60)
    logger_main.info(f"Summary: {success_count} succeeded, {failure_count} failed")
    if failed_providers:
        logger_main.warning(f"Failed providers: {', '.join(failed_providers)}")

    # Exit with error code if any provider failed
    if failure_count > 0:
        sys.exit(1)


@cli.command()
@click.pass_context
def list_providers(ctx: click.Context) -> None:
    """List all registered providers."""
    logger_main = logger.bind(provider="CLI")
    providers = registry.list_provider_names()

    if not providers:
        logger_main.warning("No providers registered")
        return

    logger_main.info("Registered providers:")
    for provider_name in providers:
        click.echo(f"  - {provider_name}")


# This will be populated by providers when they register
@cli.group()
def provider() -> None:
    """Run specific provider commands."""
    pass


if __name__ == "__main__":
    cli()
