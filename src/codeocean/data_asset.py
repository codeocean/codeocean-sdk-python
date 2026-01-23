from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from requests_toolbelt.sessions import BaseUrlSession
from time import sleep, time
from typing import Optional, Iterator
from warnings import warn

from codeocean.components import Ownership, SortOrder, SearchFilter, Permissions
from codeocean.computation import PipelineProcess, Param
from codeocean.enum import StrEnum
from codeocean.folder import FileURLs, Folder, DownloadFileURL


class DataAssetType(StrEnum):
    """Type of data asset indicating its content and purpose."""

    Dataset = "dataset"
    Result = "result"
    Combined = "combined"
    Model = "model"


class DataAssetState(StrEnum):
    """Current state of a data asset during its creation and lifecycle."""

    Draft = "draft"
    Ready = "ready"
    Failed = "failed"


@dataclass_json
@dataclass(frozen=True)
class Provenance:
    """Shows the data asset provenance information when type is result."""

    commit: Optional[str] = field(
        default=None,
        metadata={"description": "Commit hash of capsule/pipeline code at time of execution"},
    )
    run_script: Optional[str] = field(
        default=None,
        metadata={"description": "Script path the data asset was created by"},
    )
    docker_image: Optional[str] = field(
        default=None,
        metadata={"description": "Docker image used to create the data asset"},
    )
    capsule: Optional[str] = field(
        default=None,
        metadata={"description": "ID of the capsule used to create the data asset"},
    )
    data_assets: Optional[list[str]] = field(
        default=None,
        metadata={
            "description": "Data assets that were used as input to create this data asset",
        },
    )
    computation: Optional[str] = field(
        default=None,
        metadata={"description": "ID of the computation from which this data asset was created"},
    )


class DataAssetOrigin(StrEnum):
    """Origin type of the data asset indicating where it was created from."""

    Local = "local"
    AWS = "aws"
    GCP = "gcp"


@dataclass_json
@dataclass(frozen=True)
class SourceBucket:
    """Information about the bucket from which the data asset was created."""

    origin: DataAssetOrigin = field(
        metadata={"description": "Origin type (aws, local, gcp)"},
    )
    bucket: Optional[str] = field(
        default=None,
        metadata={"description": "The S3 bucket from which the data asset was created"},
    )
    prefix: Optional[str] = field(
        default=None,
        metadata={
            "description": "The folder in the S3 bucket from which the data asset was created",
        },
    )
    external: Optional[bool] = field(
        default=None,
        metadata={"description": "Indicates if the data asset is stored external to Code Ocean"},
    )


@dataclass_json
@dataclass(frozen=True)
class AppParameter:
    """Name and value of app panel parameters used to generate result data assets."""

    name: Optional[str] = field(
        default=None,
        metadata={"description": "Parameter name"},
    )
    value: Optional[str] = field(
        default=None,
        metadata={"description": "Parameter value"},
    )


@dataclass_json
@dataclass(frozen=True)
class ResultsInfo:
    """
    Additional information for data assets created from exported capsule/pipeline
    results.
    """

    capsule_id: Optional[str] = field(
        default=None,
        metadata={"description": "ID of the capsule that was executed"},
    )
    pipeline_id: Optional[str] = field(
        default=None,
        metadata={"description": "ID of the pipeline that was executed"},
    )
    version: Optional[int] = field(
        default=None,
        metadata={"description": "Capsule or pipeline release version"},
    )
    commit: Optional[str] = field(
        default=None,
        metadata={
            "description": "Commit hash of capsule/pipeline code at time of execution",
        },
    )
    run_script: Optional[str] = field(
        default=None,
        metadata={
            "description": "Path to the script that was executed relative to /capsule folder",
        },
    )
    data_assets: Optional[list[str]] = field(
        default=None,
        metadata={"description": "IDs of data assets used during the run"},
    )
    parameters: Optional[list[Param]] = field(
        default=None,
        metadata={"description": "Run parameters used for execution"},
    )
    nextflow_profile: Optional[str] = field(
        default=None,
        metadata={"description": "Pipeline Nextflow profile"},
    )
    processes: Optional[list[PipelineProcess]] = field(
        default=None,
        metadata={"description": "Pipeline processes information"},
    )


@dataclass_json
@dataclass(frozen=True)
class DataAsset:
    """Represents a Code Ocean data asset with its metadata and properties."""

    id: str = field(
        metadata={"description": "Unique data asset ID (UUID string)"},
    )
    created: int = field(
        metadata={"description": "Data asset creation time in seconds from epoch"},
    )
    name: str = field(
        metadata={"description": "Name of the data asset"},
    )
    mount: str = field(
        metadata={"description": "The default mount folder of the data asset"},
    )
    state: DataAssetState = field(
        metadata={"description": "Data asset creation state (draft, ready, failed)"},
    )
    type: DataAssetType = field(
        metadata={
            "description": "Type of the data asset (dataset, result, combined, model)",
        },
    )
    last_used: int = field(
        metadata={
            "description": "Time data asset was last used in seconds from unix epoch",
        },
    )
    files: Optional[int] = field(
        default=None,
        metadata={"description": "Number of files in the data asset"},
    )
    size: Optional[int] = field(
        default=None,
        metadata={"description": "Size in bytes of the data asset (parsed to int)"},
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Data asset description"},
    )
    tags: Optional[list[str]] = field(
        default=None,
        metadata={"description": "Keywords for searching the data asset"},
    )
    provenance: Optional[Provenance] = field(
        default=None,
        metadata={
            "description": "Shows the data asset provenance if type is result; only "
            "'capsule' or 'computation' field will be populated depending on source",
        },
    )
    source_bucket: Optional[SourceBucket] = field(
        default=None,
        metadata={
            "description": "Information on bucket from which data asset was created",
        },
    )
    custom_metadata: Optional[dict] = field(
        default=None,
        metadata={
            "description": "Custom metadata fields defined by deployment admin with "
            "user-set values",
        },
    )
    app_parameters: Optional[list[AppParameter]] = field(
        default=None,
        metadata={
            "description": "Name and value of app panel parameters used to generate "
            "result data asset",
        },
    )
    nextflow_profile: Optional[str] = field(
        default=None,
        metadata={"description": "Pipeline Nextflow profile"},
    )
    contained_data_assets: Optional[list[ContainedDataAsset]] = field(
        default=None,
        metadata={"description": "List of contained data assets if type is combined"},
    )
    last_transferred: Optional[int] = field(
        default=None,
        metadata={
            "description": "Time data asset's files were last transferred to a "
            "different S3 storage location",
        },
    )
    transfer_error: Optional[str] = field(
        default=None,
        metadata={
            "description": "The error that occurred during the last transfer attempt "
            "if it failed",
        },
    )
    failure_reason: Optional[str] = field(
        default=None,
        metadata={
            "description": "Reason for data asset creation failure if state is failed",
        },
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetUpdateParams:
    """Parameters for updating data asset metadata."""

    name: Optional[str] = field(
        default=None,
        metadata={"description": "Data asset name"},
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Data asset description"},
    )
    tags: Optional[list[str]] = field(
        default=None,
        metadata={"description": "Keywords for searching the data asset"},
    )
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Default mount folder of the data asset"},
    )
    custom_metadata: Optional[dict] = field(
        default=None,
        metadata={"description": "Custom metadata fields with user-set values"},
    )


@dataclass_json
@dataclass(frozen=True)
class AWSS3Source:
    """AWS S3 source configuration for creating data assets."""

    bucket: str = field(
        metadata={
            "description": "The S3 bucket from which the data asset will be created",
        },
    )
    endpoint_name: Optional[str] = field(
        default=None,
        metadata={
            "description": "The name of the custom S3 endpoint where the bucket is stored",
        },
    )
    prefix: Optional[str] = field(
        default=None,
        metadata={
            "description": "The folder in the S3 bucket from which the data asset will be created",
        },
    )
    keep_on_external_storage: Optional[bool] = field(
        default=None,
        metadata={
            "description": "When true, data asset files will not be copied to Code Ocean",
        },
    )
    public: Optional[bool] = field(
        default=None,
        metadata={
            "description": "When true, Code Ocean will access the source bucket without credentials",
        },
    )
    use_input_bucket: Optional[bool] = field(
        default=None,
        metadata={
            "description": "When true, Code Ocean will try to create the dataset from an internal "
            "input bucket. All properties are ignored except for prefix. Only allowed to Admin users.",
        },
    )


@dataclass_json
@dataclass(frozen=True)
class GCPCloudStorageSource:
    """
    Google Cloud Platform Cloud Storage source configuration for creating
    data assets.
    """

    bucket: str = field(
        metadata={
            "description": "The GCP Cloud Storage bucket from which the data asset will be created",
        },
    )
    client_id: Optional[str] = field(
        default=None,
        metadata={"description": "GCP client ID for authentication"},
    )
    client_secret: Optional[str] = field(
        default=None,
        metadata={"description": "GCP client secret for authentication"},
    )
    prefix: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "The folder in the GCP bucket from which the data asset will be created"
            ),
        },
    )


@dataclass_json
@dataclass(frozen=True)
class ComputationSource:
    """Computation source configuration for creating result data assets."""

    id: str = field(
        metadata={"description": "Computation ID from which to create the data asset"},
    )
    path: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "Results path within computation (empty captures all result files)"
            ),
        },
    )


@dataclass_json
@dataclass(frozen=True)
class Source:
    """Source configuration for data asset creation from various origins."""

    aws: Optional[AWSS3Source] = field(
        default=None,
        metadata={"description": "AWS S3 source configuration"},
    )
    gcp: Optional[GCPCloudStorageSource] = field(
        default=None,
        metadata={"description": "GCP Cloud Storage source configuration"},
    )
    computation: Optional[ComputationSource] = field(
        default=None,
        metadata={"description": "Computation source configuration"},
    )


@dataclass_json
@dataclass(frozen=True)
class AWSS3Target:
    """AWS S3 target configuration for external data asset storage."""

    bucket: str = field(
        metadata={"description": "The S3 bucket where the data asset will be stored"},
    )
    endpoint_name: Optional[str] = field(
        default=None,
        metadata={"description": "The name of the custom S3 endpoint where the bucket is stored"},
    )
    prefix: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "The folder in the S3 bucket where the data asset will be placed"
            ),
        },
    )


@dataclass_json
@dataclass(frozen=True)
class Target:
    """Target configuration for external data asset storage."""

    aws: Optional[AWSS3Target] = field(
        default=None,
        metadata={"description": "AWS S3 target configuration"},
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetParams:
    """
    Complete parameter set for creating data assets with various source types
    and configurations.
    """

    name: str = field(
        metadata={"description": "Data asset name"},
    )
    tags: list[str] = field(
        metadata={
            "description": "Keywords applied to the data asset to aid in searching",
        },
    )
    mount: str = field(
        metadata={"description": "Data asset default mount folder"},
    )
    description: Optional[str] = field(
        default=None,
        metadata={"description": "Data asset description"},
    )
    source: Optional[Source] = field(
        default=None,
        metadata={"description": "Source configuration (AWS S3, GCP, or computation)"},
    )
    target: Optional[Target] = field(
        default=None,
        metadata={"description": "Target configuration for external storage"},
    )
    custom_metadata: Optional[dict] = field(
        default=None,
        metadata={
            "description": "Custom metadata fields according to admin-defined fields",
        },
    )
    data_asset_ids: Optional[list[str]] = field(
        default=None,
        metadata={
            "description": "List of data asset IDs for creating combined data assets",
        },
    )
    results_info: Optional[ResultsInfo] = field(
        default=None,
        metadata={
            "description": "Additional information for data assets from external results",
        },
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetAttachParams:
    """Parameters for attaching data assets to capsules."""

    id: str = field(
        metadata={"description": "Data asset ID to attach"},
    )
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Mount path for the attached data asset"},
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetAttachResults:
    """Results from attaching data assets to capsules."""

    id: str = field(
        metadata={"description": "Data asset ID that was attached"},
    )
    mount_state: Optional[str] = field(
        default=None,
        metadata={"description": "Current state of the data asset mount"},
    )
    job_id: Optional[str] = field(
        default=None,
        metadata={"description": "Job ID for the attachment operation"},
    )
    external: Optional[bool] = field(
        default=None,
        metadata={"description": "Indicates if the data asset is external"},
    )
    ready: Optional[bool] = field(
        default=None,
        metadata={"description": "Indicates if the data asset is ready for use"},
    )
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Path at which the data asset is mounted"},
    )


class DataAssetSortBy(StrEnum):
    """Fields available for sorting data asset search results."""

    Created = "created"
    Type = "type"
    Name = "name"
    Size = "size"


class DataAssetSearchOrigin(StrEnum):
    """Origin filter for data asset searches."""

    Internal = "internal"
    External = "external"


@dataclass_json
@dataclass(frozen=True)
class DataAssetSearchParams:
    """
    Parameters for searching data assets with filtering, sorting,
    and pagination options.
    """

    query: Optional[str] = field(
        default=None,
        metadata={
            "description": """Search expression supporting free text and field:value filters.
            Valid fields:
             - name
             - tag
             - run_script
             - commit_id
             - contained_data_id

            Free text:
             - Matches across weighted fields (name, tags, description, custom metadata)

            Syntax rules:
             - Same field repeated = OR
             - Different fields = AND
             - Quotes = exact phrase
             - No explicit OR operator
             - No wildcards (*)
             - Not case sensitive

            Examples:
             - name:RNA-seq tag:genomics
             - name:"analysis pipeline"
             - name:Synergy
            """
        },
    )
    next_token: Optional[str] = field(
        default=None,
        metadata={
            "description": "Token for next page of results from previous response",
        },
    )
    offset: Optional[int] = field(
        default=None,
        metadata={
            "description": (
                "Starting index for search results (ignored if next_token is set)"
            ),
        },
    )
    limit: Optional[int] = field(
        default=None,
        metadata={
            "description": "Number of items to return (up to 1000, defaults to 100)",
        },
    )
    sort_field: Optional[DataAssetSortBy] = field(
        default=None,
        metadata={"description": "Field to sort by (created, type, name, size)"},
    )
    sort_order: Optional[SortOrder] = field(
        default=None,
        metadata={
            "description": "Sort order (asc or desc) - must be provided with sort_field",
        },
    )
    type: Optional[DataAssetType] = field(
        default=None,
        metadata={
            "description": "Filter by data asset type "
            "(dataset, result, combined, model)",
        },
    )
    ownership: Optional[Ownership] = field(
        default=None,
        metadata={
            "description": (
                "Filter by ownership (created or shared) - defaults to all accessible"
            ),
        },
    )
    origin: Optional[DataAssetSearchOrigin] = field(
        default=None,
        metadata={"description": "Filter by origin (internal or external)"},
    )
    favorite: Optional[bool] = field(
        default=None,
        metadata={"description": "Search only favorite data assets"},
    )
    archived: Optional[bool] = field(
        default=None,
        metadata={"description": "Search only archived data assets"},
    )
    filters: Optional[list[SearchFilter]] = field(
        default=None,
        metadata={
            "description": "Additional field-level filters for name, description, tags, or custom fields",
        },
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetSearchResults:
    """Results from a data asset search operation with pagination support."""

    has_more: bool = field(
        metadata={
            "description": "Indicates if there are more results available",
        },
    )
    results: list[DataAsset] = field(
        metadata={
            "description": (
                "Array of data assets found matching the search criteria"
            ),
        },
    )
    next_token: Optional[str] = field(
        default=None,
        metadata={"description": "Token for fetching the next page of results"},
    )


@dataclass_json
@dataclass(frozen=True)
class ContainedDataAsset:
    """Information about data assets contained within a combined data asset."""

    id: Optional[str] = field(
        default=None,
        metadata={"description": "ID of the contained data asset"},
    )
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Mount path of the contained data asset"},
    )
    size: Optional[int] = field(
        default=None,
        metadata={"description": "Size in bytes of the contained data asset"},
    )


@dataclass_json
@dataclass(frozen=True)
class TransferDataParams:
    """Parameters for transferring data asset files
    to different S3 storage locations."""

    target: Target = field(
        metadata={
            "description": "Target storage location configuration",
        },
    )
    force: Optional[bool] = field(
        default=None,
        metadata={
            "description": (
                "Perform transfer even if there are release pipelines using the data asset"
            ),
        },
    )


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
