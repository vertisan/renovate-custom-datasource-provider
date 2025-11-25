"""Common CLI utilities shared across commands."""

import sys
from pathlib import Path
from typing import Optional

import click

from renovate_datasource.domain.exceptions import DomainError

# Default output directory
OUTPUT_DIR = "output"


def handle_error(error: Exception, verbose: bool = False) -> None:
    """Handle and display errors consistently.

    Args:
        error: Exception to handle
        verbose: Whether to show full traceback
    """
    if isinstance(error, DomainError):
        click.echo(f"Error: {error}", err=True)
    else:
        click.echo(f"Unexpected error: {error}", err=True)

    if verbose:
        import traceback

        click.echo("\nTraceback:", err=True)
        click.echo(traceback.format_exc(), err=True)

    sys.exit(1)


def sanitize_filename(filename: str) -> str:
    """Sanitize filename by replacing path separators and invalid characters.

    Args:
        filename: The filename to sanitize

    Returns:
        Sanitized filename safe for use in filesystems
    """
    # Replace path separators with dashes
    sanitized = filename.replace("/", "-").replace("\\", "-")
    # Remove or replace other potentially problematic characters
    sanitized = sanitized.replace(":", "-").replace(" ", "_")
    return sanitized


def ensure_output_dir() -> Path:
    """Ensure the output directory exists.

    Returns:
        Path object for the output directory
    """
    output_path = Path(OUTPUT_DIR)
    output_path.mkdir(exist_ok=True)
    return output_path


def output_result(
    content: str, output_file: Optional[str] = None, default_filename: Optional[str] = None
) -> None:
    """Output result to file in output directory or custom path.

    If output_file is provided, writes to that path.
    If default_filename is provided, writes to output/{default_filename}.
    If neither is provided, prints to stdout (for backward compatibility).

    Args:
        content: Content to output
        output_file: Optional custom file path (overrides default)
        default_filename: Optional default filename to use in output directory
    """
    # Determine the output path
    if output_file:
        # User specified a custom output path
        final_path = output_file
    elif default_filename:
        # Use default filename in output directory
        output_dir = ensure_output_dir()
        sanitized_name = sanitize_filename(default_filename)
        final_path = str(output_dir / sanitized_name)
    else:
        # No file specified, output to stdout
        click.echo(content)
        return

    # Write to file
    try:
        with open(final_path, "w") as f:
            f.write(content)
        click.echo(f"Manifest written to {final_path}")
    except OSError as e:
        click.echo(f"Error writing to file: {e}", err=True)
        sys.exit(1)


# Common CLI options
output_option = click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="Custom output file path (if not specified, saves to output/ directory)",
)

verbose_option = click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output",
)
