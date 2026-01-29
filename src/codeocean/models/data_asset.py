from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass, field
from typing import Optional

from codeocean.enum import StrEnum
from codeocean.models.components import Ownership, SortOrder, SearchFilter
from codeocean.models.computation import PipelineProcess, Param


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
class CloudWorkstationSource:
    """Cloud Workstation session source configuration for creating data assets."""

    id: str = field(
        metadata={"description": "Computation ID of the Cloud Workstation session"},
    )
    path: str = field(
        metadata={
            "description": (
                "Path within the Cloud Workstation to create the data asset from"
            ),
        },
    )
    run_script: Optional[str] = field(
        default=None,
        metadata={
            "description": (
                "Path to the script that was executed, relative to the capsule folder."
                "Existence determines if the data would be of type result"
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
    cloud_workstation: Optional[CloudWorkstationSource] = field(
        default=None,
        metadata={"description": "Cloud Workstation source configuration"},
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
