---
allowed-tools: Read, Write, Edit, Bash
argument-hint: [file-path] | [component-name]
description: Generate comprehensive test suite with unit, integration, and edge case coverage
---

# Generate Tests

Generate comprehensive test suite for: $ARGUMENTS

## Current Testing Setup

### Python

- Test framework: @pyproject.toml or @setup.py or @setup.cfg (detect framework)
- Existing tests: !`find . -name "*.test.py" -o -name "*_test.py" | head -5`
- Test coverage: !`pytest --cov 2>/dev/null || python -m pytest --cov 2>/dev/null || echo "No coverage configured"`
- Target file: @$ARGUMENTS (if file path provided)

## Task

I'll analyze the target code and create complete test coverage including:

1. Unit tests for individual functions and methods
2. Integration tests for component interactions
3. Edge case and error handling tests
4. Mock implementations for external dependencies
5. Test utilities and helpers as needed
6. Performance and snapshot tests where appropriate

## Process

I'll follow these steps:

1. Analyze the target file/component structure
2. Identify all testable functions, methods, and behaviors
3. Examine existing test patterns in the project
4. Create test files following project naming conventions
5. Implement comprehensive test cases with proper setup/teardown
6. Add necessary mocks and test utilities
7. Verify test coverage and add missing test cases

## Test Types

### Unit Tests

- Individual function testing with various inputs
- Component rendering and prop handling
- State management and lifecycle methods
- Utility function edge cases and error conditions

### Integration Tests

- Component interaction testing
- API integration with mocked responses
- Service layer integration
- End-to-end user workflows

### Framework-Specific Tests

#### Python

- **Python**: Unit testing with pytest and unittest
- **FastAPI**: API endpoint and middleware testing with TestClient
- **Django**: Model, view, and middleware testing with Django TestCase
- **Flask**: Application and route testing with pytest-flask
- **Click**: Command and callback testing with CliRunner

## Testing Best Practices

### Test Structure

- Use descriptive test names that explain the behavior
- Follow AAA pattern (Arrange, Act, Assert)
- Group related tests with describe blocks
- Use proper setup and teardown for test isolation

### Mock Strategy

- Mock external dependencies and API calls
- Use factories for test data generation
- Implement proper cleanup for async operations
- Mock timers and dates for deterministic tests

### Coverage Goals

- Aim for 80%+ code coverage
- Focus on critical business logic paths
- Test both happy path and error scenarios
- Include boundary value testing

I'll adapt to your project's testing framework (pytest, unittest, etc.) and follow established patterns. For Python projects, I'll use scoped fixtures for test isolation and proper setup/teardown management.
