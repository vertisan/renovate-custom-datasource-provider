"""Configuration management."""

from dataclasses import dataclass


@dataclass
class Config:
    """Application configuration."""

    timeout: int = 30
    """HTTP request timeout in seconds."""

    indent: int = 2
    """JSON output indentation."""

    verbose: bool = False
    """Enable verbose output."""
