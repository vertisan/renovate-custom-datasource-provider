# Renovate Datasource Provider

A flexible and extensible Python CLI tool for generating Renovate-compatible custom datasource manifests from various version sources. Built with Clean Architecture principles for maintainability and easy extensibility.

## Features

- **Multiple Providers**: Built-in support for Red Hat containers and K3s versions
- **Clean Architecture**: Separation of concerns with clear layer boundaries
- **Extensible**: Easy to add new providers following established patterns
- **Type-Safe**: Full type hints and Pydantic models for data validation
- **Well-Tested**: Comprehensive test suite with unit and integration tests
- **CLI-Friendly**: Simple command-line interface with provider-specific options

## Installation

### Using Poetry (Recommended)

```bash
# Clone the repository
git clone <repository-url>
cd renovate-datasource-provider

# Install dependencies
poetry install

# Run the CLI
poetry run renovate-datasource --help
```

### Using pip

```bash
# Install in development mode
pip install -e .

# Run the CLI
renovate-datasource --help
```

## Usage

### Red Hat Container Catalog Provider

Generate a manifest for Red Hat container versions from the Red Hat Container Catalog (Pyxis API):

```bash
# Default UBI 9 (saves to output/redhat-catalog-ubi9-ubi.json)
renovate-datasource generate redhat-catalog

# UBI 9 Minimal (saves to output/redhat-catalog-ubi9-minimal.json)
renovate-datasource generate redhat-catalog --image-path ubi9-minimal

# UBI 8 (saves to output/redhat-catalog-ubi8-ubi.json)
renovate-datasource generate redhat-catalog --image-path ubi8/ubi

# Save to custom location
renovate-datasource generate redhat-catalog --output /path/to/custom.json

# With verbose output
renovate-datasource generate redhat-catalog --verbose
```

**Note**:

- By default, manifests are saved to the `output/` directory with auto-generated filenames
- Only versions matching the pattern `major.minor-timestamp` are included (e.g., `9.5-1734081738`)
- Uses the Docker Registry V2 API to fetch all available container tags

### K3s Provider

Generate a manifest for K3s Kubernetes distribution versions from GitHub:

```bash
# Stable versions only (saves to output/k3s.json)
renovate-datasource generate k3s

# Include pre-releases (saves to output/k3s-with-prereleases.json)
renovate-datasource generate k3s --include-prereleases

# Save to custom location
renovate-datasource generate k3s --output /path/to/custom-k3s.json
```

**Note**: By default, manifests are saved to the `output/` directory. The `output/` directory is created automatically if it doesn't exist.

## Output Format

The tool generates JSON manifests compatible with Renovate's custom datasource format:

```json
{
  "releases": [
    {
      "version": "v1.27.0+k3s1",
      "releaseTimestamp": "2023-04-12T10:30:00Z"
    }
  ],
  "sourceUrl": "https://github.com/k3s-io/k3s",
  "homepage": "https://k3s.io",
  "changelogUrl": "https://github.com/k3s-io/k3s/releases"
}
```

## Architecture

This project follows Clean Architecture principles with clear separation of concerns:

```
src/renovate_datasource/
├── domain/              # Core business logic (entities, protocols)
├── use_cases/           # Application business rules
├── adapters/            # Interface adapters (providers, HTTP client)
└── infrastructure/      # Frameworks & external dependencies (CLI)
```

### Layers

1. **Domain Layer**: Core entities (Release, Manifest) and provider protocol
2. **Use Cases Layer**: Application-specific business rules (GenerateManifestUseCase)
3. **Adapters Layer**: Provider implementations and external service wrappers
4. **Infrastructure Layer**: CLI commands, configuration, and framework code

## Adding a New Provider

To add a new provider, follow these steps:

### 1. Create Provider Implementation

Create a new file in `src/renovate_datasource/adapters/providers/`:

```python
# src/renovate_datasource/adapters/providers/my_provider.py

from renovate_datasource.adapters.base_provider import BaseProvider
from renovate_datasource.adapters.http_client import HttpClient
from renovate_datasource.domain.entities import Manifest, Release

class MyProvider(BaseProvider):
    name = "my-provider"

    def __init__(self, http_client=None):
        self.http_client = http_client or HttpClient()

    def fetch_versions(self) -> list[str]:
        # Implement version fetching logic
        pass

    def create_manifest(self, versions: list[str]) -> Manifest:
        # Create manifest from versions
        releases = [Release(version=v) for v in versions]
        return Manifest(releases=releases)
```

### 2. Create CLI Command

Create a new file in `src/renovate_datasource/infrastructure/cli/commands/`:

```python
# src/renovate_datasource/infrastructure/cli/commands/my_provider.py

import click
from renovate_datasource.adapters.providers.my_provider import MyProvider
from renovate_datasource.use_cases.generate_manifest import GenerateManifestUseCase
from renovate_datasource.infrastructure.cli.common import handle_error, output_result

@click.command(name="my-provider")
@click.option("--my-option", help="Provider-specific option")
def my_provider_command(my_option):
    """Generate manifest for My Provider."""
    try:
        provider = MyProvider()
        use_case = GenerateManifestUseCase(provider)
        manifest = use_case.execute()
        output_result(JsonPresenter.present(manifest))
    except Exception as e:
        handle_error(e)
```

### 3. Register Command

Update `src/renovate_datasource/main.py` to register your command:

```python
from renovate_datasource.infrastructure.cli.commands.my_provider import my_provider_command

cli.add_command(my_provider_command)
```

### 4. Write Tests

Add tests in `tests/adapters/` for your provider implementation.

## Development

### Setup

```bash
# Install dependencies including dev dependencies
poetry install

# Activate virtual environment
poetry shell
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov

# Run specific test file
poetry run pytest tests/domain/test_entities.py

# Run integration tests only
poetry run pytest -m integration
```

### Code Quality

```bash
# Format code
poetry run black src tests

# Lint code
poetry run ruff check src tests

# Type checking
poetry run mypy src
```

### Running the CLI Locally

```bash
# Using poetry
poetry run renovate-datasource --help

# Or after activating the virtual environment
renovate-datasource --help
```

## Testing

The project includes comprehensive tests organized by layer:

- `tests/domain/`: Tests for core entities and domain logic
- `tests/use_cases/`: Tests for use case implementations
- `tests/adapters/`: Tests for provider implementations
- `tests/infrastructure/`: Tests for CLI commands

Run the full test suite with:

```bash
poetry run pytest
```

## Contributing

1. Follow Clean Architecture principles
2. Add tests for new functionality
3. Use conventional commit messages
4. Format code with Black
5. Ensure type hints are present
6. Update documentation as needed

## License

[Your License Here]

## Acknowledgments

Built with Clean Architecture principles for maintainability and extensibility.
