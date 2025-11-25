"""Pytest configuration and shared fixtures."""

import pytest
from renovate_datasource.adapters.http_client import HttpClient


@pytest.fixture
def mock_http_client(mocker):
    """Provide a mocked HTTP client."""
    return mocker.Mock(spec=HttpClient)


@pytest.fixture
def sample_versions():
    """Provide sample version data for testing."""
    return ["v1.0.0", "v1.1.0", "v1.2.0", "v2.0.0"]
