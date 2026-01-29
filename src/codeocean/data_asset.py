from __future__ import annotations

from dataclasses import dataclass
from requests_toolbelt.sessions import BaseUrlSession
from time import sleep, time
from typing import Iterator
from warnings import warn

from codeocean.models.components import Permissions
from codeocean.models.data_asset import (
    DataAsset,
    DataAssetState,
    DataAssetUpdateParams,
    DataAssetParams,
    DataAssetSearchParams,
    DataAssetSearchResults,
    TransferDataParams,
)
from codeocean.models.folder import FileURLs, Folder, DownloadFileURL


@dataclass
class DataAssets:
    """Client for interacting with Code Ocean data asset APIs."""

    client: BaseUrlSession

    def get_data_asset(self, data_asset_id: str) -> DataAsset:
        """Retrieve metadata for a specific data asset by its ID."""
        res = self.client.get(f"data_assets/{data_asset_id}")

        return DataAsset.from_dict(res.json())

    def update_metadata(self, data_asset_id: str, update_params: DataAssetUpdateParams) -> DataAsset:
        """
        Update metadata for a data asset including name, description, tags, mount,
        and custom metadata.

        Supports updating various metadata types:
        - Basic metadata: name (display name), description (free text description)
        - Organization: tags (keywords for searching), mount (default mount folder path)
        - Custom metadata: admin-defined custom fields with user-set values according to
            deployment configuration
            (string, number, or date fields in unix epoch format)
        """
        res = self.client.put(
            f"data_assets/{data_asset_id}",
            json=update_params.to_dict(),
        )

        return DataAsset.from_dict(res.json())

    def create_data_asset(self, data_asset_params: DataAssetParams) -> DataAsset:
        """
        Create a new data asset from various sources including S3 buckets,
        computation results, or combined assets.

        Data assets are versioned, immutable collections of files that serve as inputs
        or outputs for computational workflows in Code Ocean. Internal data assets
        store files within Code Ocean's infrastructure, while external data assets
        reference files in external storage (S3/GCP) without copying.

        Supports creating data assets from AWS S3, GCP Cloud Storage, computation
        results, or combining existing data assets. Returns confirmation of creation
        request validity, not success, as creation takes time. Use wait_until_ready()
        to monitor creation progress.

        """
        res = self.client.post("data_assets", json=data_asset_params.to_dict())

        return DataAsset.from_dict(res.json())

    def wait_until_ready(
        self,
        data_asset: DataAsset,
        polling_interval: float = 5,
        timeout: float | None = None,
    ) -> DataAsset:
        """
        Poll a data asset until it reaches 'Ready' or 'Failed' state with configurable
        timing.

        Args:
            data_asset: The data asset object to monitor
            polling_interval: Time between status checks in seconds
                (minimum 5 seconds)
            timeout: Maximum time to wait in seconds, or None for no timeout

        Returns:
            Updated data asset object once ready or failed

        Raises:
            ValueError: If polling_interval < 5 or timeout constraints are violated
            TimeoutError: If data asset doesn't become ready within timeout period
        """
        if polling_interval < 5:
            raise ValueError(
                f"Polling interval {polling_interval} should be greater than or equal to 5"
            )
        if timeout is not None and timeout < polling_interval:
            raise ValueError(
                f"Timeout {timeout} should be greater than or equal to polling interval {polling_interval}"
            )
        if timeout is not None and timeout < 0:
            raise ValueError(
                f"Timeout {timeout} should be greater than or equal to 0 (seconds), or None"
            )
        t0 = time()
        while True:
            da = self.get_data_asset(data_asset.id)

            if da.state in [DataAssetState.Ready, DataAssetState.Failed]:
                return da

            if timeout is not None and (time() - t0) > timeout:
                raise TimeoutError(
                    f"Data asset {data_asset.id} was not ready within {timeout} seconds"
                )

            sleep(polling_interval)

    def delete_data_asset(self, data_asset_id: str):
        """Delete a data asset permanently."""
        self.client.delete(f"data_assets/{data_asset_id}")

    def update_permissions(self, data_asset_id: str, permissions: Permissions):
        """Update permissions for a data asset to control user and group access."""
        self.client.post(
            f"data_assets/{data_asset_id}/permissions",
            json=permissions.to_dict(),
        )

    def archive_data_asset(self, data_asset_id: str, archive: bool):
        """Archive or unarchive a data asset to control its visibility and accessibility."""
        self.client.patch(
            f"data_assets/{data_asset_id}/archive",
            params={"archive": archive},
        )

    def search_data_assets(self, search_params: DataAssetSearchParams) -> DataAssetSearchResults:
        """Search for data assets with filtering, sorting, and pagination options."""
        res = self.client.post("data_assets/search", json=search_params.to_dict())

        return DataAssetSearchResults.from_dict(res.json())

    def search_data_assets_iterator(self, search_params: DataAssetSearchParams) -> Iterator[DataAsset]:
        """
        Iterate through all data assets matching search criteria with
        automatic pagination.
        """
        params = search_params.to_dict()
        while True:
            response = self.search_data_assets(
                search_params=DataAssetSearchParams(**params),
            )

            for result in response.results:
                yield result

            if not response.has_more:
                return

            params["next_token"] = response.next_token

    def list_data_asset_files(self, data_asset_id: str, path: str = "") -> Folder:
        """
        List files and folders within an internal data asset at the specified path.
        Empty path retrieves root level contents.
        """
        data = {
            "path": path,
        }

        res = self.client.post(f"data_assets/{data_asset_id}/files", json=data)

        return Folder.from_dict(res.json())

    def get_data_asset_file_download_url(self, data_asset_id: str, path: str) -> DownloadFileURL:
        """(Deprecated) Generate a download URL for a specific file from an internal data asset.

        Deprecated: Use get_data_asset_file_urls instead.
        """
        warn(
            "get_data_asset_file_download_url is deprecated and will be removed in a future release. "
            "Use get_data_asset_file_urls instead.",
            DeprecationWarning,
            stacklevel=2,
        )
        res = self.client.get(
            f"data_assets/{data_asset_id}/files/download_url",
            params={"path": path},
        )

        return DownloadFileURL.from_dict(res.json())

    def get_data_asset_file_urls(self, data_asset_id: str, path: str) -> FileURLs:
        """Generate view and download URLs for a specific file from an internal data asset."""
        res = self.client.get(
            f"data_assets/{data_asset_id}/files/urls",
            params={"path": path},
        )

        return FileURLs.from_dict(res.json())

    def transfer_data_asset(self, data_asset_id: str, transfer_params: TransferDataParams):
        """
        Transfer a data asset's files to a different S3 storage location (Admin only).

        Can convert internal data assets to external or change storage location of
        external data assets. Maintains provenance for result data assets. Use
        force=True when transferring data assets used by release pipelines.
        """
        self.client.post(
            f"data_assets/{data_asset_id}/transfer",
            json=transfer_params.to_dict(),
        )
