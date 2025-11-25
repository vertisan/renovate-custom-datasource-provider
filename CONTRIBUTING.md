# Contributing to Renovate Datasource Provider

Thank you for your interest in contributing! This document provides guidelines for contributing to this project.

## Code of Conduct

Please be respectful and constructive in all interactions with the project and its community.

## Development Setup

### Prerequisites

- Python 3.12+
- Poetry 1.7+
- Docker (for container testing)

### Setup

```bash
# Clone the repository
git clone https://github.com/vertisan/renovate-datasource-provider.git
cd renovate-datasource-provider

# Install dependencies
poetry install

# Activate virtual environment
poetry shell

# Run tests
poetry run pytest
```

## Development Workflow

### 1. Create a Branch

```bash
# For features
git checkout -b feat/your-feature-name

# For bug fixes
git checkout -b fix/your-bug-fix

# For documentation
git checkout -b docs/your-documentation-update
```

### 2. Make Changes

Follow these principles:

- **Clean Architecture**: Respect the layer boundaries (domain → use cases → adapters → infrastructure)
- **Type Safety**: Add type hints to all functions and methods
- **Testing**: Write tests for new functionality
- **Documentation**: Update relevant documentation

### 3. Code Quality

Before committing, ensure your code passes all quality checks:

```bash
# Format code
poetry run black src tests

# Lint code
poetry run ruff check src tests

# Type checking
poetry run mypy src

# Run tests
poetry run pytest

# Run tests with coverage
poetry run pytest --cov
```

### 4. Commit Changes

Use [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>
```

**Types:**

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `ci`: CI/CD changes
- `perf`: Performance improvements

**Examples:**

```bash
feat: add support for Debian container versions
fix: correct version sorting for RedHat catalog
docs: update installation instructions
test: add integration tests for K3s provider
refactor: simplify HTTP client error handling
```

**Breaking Changes:**

```bash
feat!: change provider interface
```

### 5. Submit a Pull Request

1. Push your branch to GitHub
2. Create a Pull Request against the `master` branch
3. Fill out the PR template
4. Wait for CI checks to pass
5. Request review from maintainers

## Project Structure

```
src/renovate_datasource/
├── domain/              # Core business logic
│   ├── entities.py     # Domain entities (Release, Manifest)
│   ├── exceptions.py   # Domain exceptions
│   └── provider_protocol.py  # Provider interface
├── use_cases/          # Application business rules
│   └── generate_manifest.py
├── adapters/           # Interface adapters
│   ├── providers/     # Provider implementations
│   ├── base_provider.py
│   ├── http_client.py
│   └── presenters.py
└── infrastructure/     # External frameworks & tools
    ├── cli/           # CLI commands
    └── config.py
```

## Adding a New Provider

See [README.md](README.md#adding-a-new-provider) for detailed instructions on adding new providers.

### Checklist

- [ ] Create provider class extending `BaseProvider`
- [ ] Implement `fetch_versions()` method
- [ ] Implement `create_manifest()` method
- [ ] Add CLI command in `infrastructure/cli/commands/`
- [ ] Register command in `main.py`
- [ ] Add tests in `tests/adapters/`
- [ ] Update documentation in README.md
- [ ] Update CLAUDE.md with implementation details

## Testing

### Running Tests

```bash
# All tests
poetry run pytest

# Exclude integration tests (faster)
poetry run pytest -m "not integration"

# Specific test file
poetry run pytest tests/domain/test_entities.py

# With coverage report
poetry run pytest --cov --cov-report=html
```

### Writing Tests

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Mark with `@pytest.mark.integration` for tests that call external APIs
- Use fixtures for common test data
- Mock external dependencies when appropriate

## Documentation

- Update README.md for user-facing changes
- Update CLAUDE.md with technical implementation details
- Add docstrings to all public functions and classes
- Include examples in docstrings where helpful

## Release Process

Releases are automated using semantic-release:

1. Merge changes to `master` branch with conventional commits
2. CI/CD automatically creates releases based on commit messages
3. For pre-releases, push to `next` branch and trigger manual release

## Questions?

If you have questions, please:

1. Check existing documentation
2. Search existing issues
3. Open a new issue with your question

Thank you for contributing!
