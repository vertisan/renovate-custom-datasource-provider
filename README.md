# Renovate Custom Datasource Provider

[![CI](https://github.com/vertisan/renovate-custom-datasource-provider/actions/workflows/ci.yml/badge.svg)](https://github.com/vertisan/renovate-custom-datasource-provider/actions/workflows/ci.yml)
[![Release](https://github.com/vertisan/renovate-custom-datasource-provider/actions/workflows/release.yml/badge.svg)](https://github.com/vertisan/renovate-custom-datasource-provider/actions/workflows/release.yml)
[![codecov](https://codecov.io/gh/vertisan/renovate-custom-datasource-provider/branch/master/graph/badge.svg)](https://codecov.io/gh/vertisan/renovate-custom-datasource-provider)

A Python CLI tool for generating custom datasource JSON files for [Renovate](https://renovatebot.com/). This tool provides a unified interface for managing multiple datasource providers, making it easy to add new providers and handle errors gracefully.

## Features

- 🔌 **Pluggable Architecture**: Easy-to-extend provider system
- 🛡️ **Error Resilience**: One provider failure won't crash the entire process
- 🎯 **Provider-Specific Configuration**: Each provider has its own configuration options
- 📦 **Multiple Output Formats**: Generate JSON files for different package types
- 🧪 **Well Tested**: Comprehensive unit tests for core and providers
- 🐳 **Docker Support**: Ready-to-use Docker image
- 🔄 **CI/CD Ready**: Automated testing, linting, and releases

## Installation

### Using Poetry

```bash
poetry add renovate-custom-datasource-provider
```

### Using pip

```bash
pip install renovate-custom-datasource-provider
```

### Using Docker

```bash
docker pull ghcr.io/vertisan/renovate-custom-datasource-provider:latest
```

## Usage

### Command Line Interface

The CLI provides several commands to work with datasource providers.

#### List Available Providers

```bash
renovate-datasource list-providers
```

#### Run All Providers

Run all registered providers and generate JSON files for all of them:

```bash
renovate-datasource all-providers
```

With custom output directory:

```bash
renovate-datasource -o /path/to/output all-providers
```

#### Run Specific Provider

Each provider has its own command with specific options:

##### Red Hat Docker Provider

Fetch versions for Red Hat UBI (Universal Base Image) containers:

```bash
# Use default repositories (ubi9/ubi-minimal, ubi8, ubi9)
renovate-datasource provider redhat-docker

# Specify custom repositories
renovate-datasource provider redhat-docker \
  -r ubi9/ubi-minimal \
  -r ubi8 \
  -r ubi9/nodejs-20

# With custom output directory
renovate-datasource provider redhat-docker \
  -o /path/to/output \
  -r ubi9/ubi-minimal
```

### Using Docker

```bash
# Run all providers
docker run -v $(pwd)/output:/output \
  ghcr.io/vertisan/renovate-custom-datasource-provider:latest \
  all-providers

# Run specific provider
docker run -v $(pwd)/output:/output \
  ghcr.io/vertisan/renovate-custom-datasource-provider:latest \
  provider redhat-docker -r ubi9/ubi-minimal
```

### Output Format

The tool generates JSON files compatible with Renovate's custom datasource format:

```json
{
  "datasource": "docker",
  "packageName": "registry.access.redhat.com/ubi9/ubi-minimal",
  "versions": [
    {
      "version": "9.4-1194",
      "releaseTimestamp": "2024-09-17T10:30:00+00:00",
      "digest": "sha256:abc123..."
    }
  ],
  "registryUrl": "https://catalog.redhat.com",
  "homepage": "https://catalog.redhat.com/software/containers/ubi9/ubi-minimal"
}
```

## Development

### Prerequisites

- Python 3.11 or higher
- Poetry
- Task (optional, for running tasks)

### Setup

```bash
# Clone the repository
git clone https://github.com/vertisan/renovate-custom-datasource-provider.git
cd renovate-custom-datasource-provider

# Install dependencies
poetry install

# Or using task
task install
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Or using task
task test

# Run tests with coverage
task test

# Run linters
task lint

# Format code
task format
```

### Adding a New Provider

1. Create a new provider class in `src/renovate_datasource/providers/`:

```python
from renovate_datasource.core.base import BaseProvider, ProviderConfig, DatasourceOutput
from renovate_datasource.core.registry import registry

class MyProviderConfig(ProviderConfig):
    # Add provider-specific configuration
    api_url: str = "https://api.example.com"

class MyProvider(BaseProvider):
    config: MyProviderConfig

    @property
    def name(self) -> str:
        return "my-provider"

    def fetch_versions(self, **kwargs) -> list[DatasourceOutput]:
        # Implement version fetching logic
        pass

# Register the provider
registry.register(MyProvider)
```

2. Add a CLI command in the same file:

```python
from renovate_datasource.cli import provider
import click

@provider.command("my-provider")
@click.option("-o", "--option", help="Provider-specific option")
@click.pass_context
def my_provider_command(ctx, option):
    """Fetch versions for my provider."""
    config = MyProviderConfig(output_dir=ctx.obj["output_dir"])
    provider_instance = MyProvider(config)
    provider_instance.generate_output(option=option)
```

3. Add tests in `tests/providers/test_my_provider.py`

4. Update `src/renovate_datasource/providers/__init__.py` to import your provider

## Available Providers

### Red Hat Docker Provider

Fetches version information for Red Hat Universal Base Images (UBI) from the Red Hat Container Catalog.

**Supported Images:**
- `ubi9/ubi-minimal`
- `ubi9` (full image)
- `ubi8`
- `ubi9/nodejs-20`
- And many more from the Red Hat Container Catalog

**Configuration:**
- `registry_url`: Red Hat Container Catalog API URL (default: `https://catalog.redhat.com/api/containers/v1`)
- `timeout`: HTTP request timeout in seconds (default: 30)

## CI/CD

This project uses GitHub Actions for CI/CD:

- **CI Workflow**: Runs on every push and PR, executes linting and testing
- **Release Workflow**: Automatically creates releases using semantic-release and builds Docker images

### Branches

- `master`: Production releases (automatic)
- `next`: Release candidates (manual trigger)

### Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New features (minor version bump)
- `fix:` Bug fixes (patch version bump)
- `docs:` Documentation changes
- `refactor:` Code refactoring
- `test:` Test changes
- `chore:` Maintenance tasks
- `BREAKING CHANGE:` Breaking changes (major version bump)

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feat/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass (`task ci`)
6. Commit your changes using conventional commits
7. Push to your branch
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- [Renovate](https://renovatebot.com/) for the amazing dependency update tool
- [Red Hat](https://www.redhat.com/) for providing the Container Catalog API
