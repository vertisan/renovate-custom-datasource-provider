"""Output presenters for formatting manifests."""

from renovate_datasource.domain.entities import Manifest


class JsonPresenter:
    """Presents manifests as formatted JSON."""

    @staticmethod
    def present(manifest: Manifest, indent: int = 2) -> str:
        """Format manifest as pretty-printed JSON.

        Args:
            manifest: Manifest to format
            indent: Number of spaces for indentation

        Returns:
            Formatted JSON string
        """
        return manifest.to_json(indent=indent)
