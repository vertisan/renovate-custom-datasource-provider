"""HTTP client abstraction for external API calls."""

from typing import Any, Optional

import requests

from renovate_datasource.domain.exceptions import FetchError


class HttpClient:
    """HTTP client wrapper providing a clean interface for providers.

    This adapter abstracts away the HTTP library details and provides
    consistent error handling.
    """

    def __init__(self, timeout: int = 30) -> None:
        """Initialize HTTP client.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str, headers: Optional[dict[str, str]] = None) -> dict[str, Any]:
        """Perform a GET request and return JSON response.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Parsed JSON response

        Raises:
            FetchError: If request fails or response is not valid JSON
        """
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise FetchError(f"Failed to fetch from {url}: {e}") from e
        except ValueError as e:
            raise FetchError(f"Invalid JSON response from {url}: {e}") from e

    def get_text(self, url: str, headers: Optional[dict[str, str]] = None) -> str:
        """Perform a GET request and return text response.

        Args:
            url: URL to fetch
            headers: Optional HTTP headers

        Returns:
            Response text

        Raises:
            FetchError: If request fails
        """
        try:
            response = self.session.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            return response.text
        except requests.exceptions.RequestException as e:
            raise FetchError(f"Failed to fetch from {url}: {e}") from e

    def close(self) -> None:
        """Close the HTTP session."""
        self.session.close()

    def __enter__(self) -> "HttpClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit."""
        self.close()
