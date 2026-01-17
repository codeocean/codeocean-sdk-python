from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from dataclasses_json import dataclass_json
from typing import Iterator, Optional
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.components import (
    Ownership,
    SortOrder,
    SearchFilter,
    Permissions,
    AppPanel,
)
from codeocean.computation import Computation
from codeocean.data_asset import DataAssetAttachParams, DataAssetAttachResults
from codeocean.enum import StrEnum


class PipelineStatus(StrEnum):
    """Status of a pipeline indicating its release state."""

    NonRelease = "non_release"
    Release = "release"


class PipelineSortBy(StrEnum):
    """Fields available for sorting pipeline search results."""

    Created = "created"
    LastAccessed = "last_accessed"
    Name = "name"


@dataclass_json
@dataclass(frozen=True)
class OriginalPipelineInfo:
    """Information about the original pipeline when this pipeline is duplicated from
    another."""

    id: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Original pipeline ID"},
    )
    major_version: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Original pipeline major version"},
    )
    minor_version: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Original pipeline minor version"},
    )
    name: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Original pipeline name"},
    )
    created: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Original pipeline creation time (int64 timestamp)"},
    )
    public: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Indicates whether the original pipeline is public"},
    )


@dataclass_json
@dataclass(frozen=True)
class Pipeline:
    """Represents a Code Ocean pipeline with its metadata and properties."""

    id: str = dataclass_field(
        metadata={"description": "Pipeline ID"},
    )
    created: int = dataclass_field(
        metadata={"description": "Pipeline creation time (int64 timestamp)"},
    )
    name: str = dataclass_field(
        metadata={"description": "Pipeline display name"},
    )
    status: PipelineStatus = dataclass_field(
        metadata={"description": "Status of the pipeline (non_release or release)"},
    )
    owner: str = dataclass_field(
        metadata={"description": "Pipeline owner's ID"},
    )
    slug: str = dataclass_field(
        metadata={"description": "Alternate pipeline ID (URL-friendly identifier)"},
    )
    last_accessed: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Pipeline last accessed time (int64 timestamp)"},
    )
    article: Optional[dict] = dataclass_field(
        default=None,
        metadata={
            "description": "Pipeline article info with URL, ID, DOI, "
            "citation, state, name, journal_name, and "
            "publish_time"
        },
    )
    cloned_from_url: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "URL to external Git repository linked to pipeline"},
    )
    description: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Pipeline description"},
    )
    field: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Pipeline research field"},
    )
    tags: Optional[list[str]] = dataclass_field(
        default=None,
        metadata={"description": "List of tags associated with the pipeline"},
    )
    original_pipeline: Optional[OriginalPipelineInfo] = dataclass_field(
        default=None,
        metadata={
            "description": "Original pipeline info when this pipeline is duplicated from another"
        },
    )
    release_pipeline: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Release pipeline ID"},
    )
    submission: Optional[dict] = dataclass_field(
        default=None,
        metadata={
            "description": "Submission info with timestamp, commit hash, "
            "verification_pipeline, verified status, and "
            "verified_timestamp"
        },
    )
    versions: Optional[list[dict]] = dataclass_field(
        default=None,
        metadata={
            "description": "Pipeline versions with major_version, minor_version, release_time, and DOI"
        },
    )


@dataclass_json
@dataclass(frozen=True)
class PipelineSearchParams:
    """Parameters for searching pipelines with various filters and pagination
    options."""

    query: Optional[str] = dataclass_field(
        default=None,
        metadata={
            "description": """Search expression supporting free text and field:value filters.
            Valid fields:
             - id
             - name
             - doi
             - tag
             - field
             - affiliation
             - journal
             - article
             - author

            Free text:
             - Matches across weighted fields (name, tags, description, authors, etc.)

            Syntax rules:
             - Same field repeated = OR
             - Different fields = AND
             - Quotes = exact phrase
             - No explicit OR operator
             - No wildcards (*)
             - Not case sensitive

            Notes:
             - "description" is not directly searchable; it is covered by free-text matching.

            Examples:
             - name:RNA-seq tag:genomics
             - name:"single cell analysis"
             - Synergy
             - name:Synergy
            """
        },
    )
    next_token: Optional[str] = dataclass_field(
        default=None,
        metadata={
            "description": "Token for next page of results from previous response"
        },
    )
    offset: Optional[int] = dataclass_field(
        default=None,
        metadata={
            "description": "Starting index for search results (ignored if next_token is set)"
        },
    )
    limit: Optional[int] = dataclass_field(
        default=None,
        metadata={
            "description": "Number of items to return (up to 1000, defaults to 100)"
        },
    )
    sort_field: Optional[PipelineSortBy] = dataclass_field(
        default=None,
        metadata={"description": "Field to sort by (created, name, or last_accessed)"},
    )
    sort_order: Optional[SortOrder] = dataclass_field(
        default=None,
        metadata={
            "description": "Sort order ('asc' or 'desc') - must be provided with a sort_field parameter as well!"
        },
    )
    ownership: Optional[Ownership] = dataclass_field(
        default=None,
        metadata={
            "description": "Filter by ownership ('private', 'created' or 'shared') - defaults to all accessible"
        },
    )
    status: Optional[PipelineStatus] = dataclass_field(
        default=None,
        metadata={"description": "Filter by status (release or non_release) - defaults to all"},
    )
    favorite: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Search only favorite pipelines"},
    )
    archived: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Search only archived pipelines"},
    )
    filters: Optional[list[SearchFilter]] = dataclass_field(
        default=None,
        metadata={
            "description": "Additional field-level filters for name, description, tags, or custom fields"
        },
    )


@dataclass_json
@dataclass(frozen=True)
class PipelineSearchResults:
    """Results from a pipeline search operation with pagination support."""

    has_more: bool = dataclass_field(
        metadata={"description": "Indicates if there are more results available"},
    )
    results: list[Pipeline] = dataclass_field(
        metadata={"description": "Array of pipelines found matching the search criteria"},
    )
    next_token: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Token for fetching the next page of results"},
    )


@dataclass
class Pipelines:
    """Client for interacting with Code Ocean pipeline APIs."""

    client: BaseUrlSession

    def get_pipeline(self, pipeline_id: str) -> Pipeline:
        """Retrieve metadata for a specific pipeline by its ID."""
        res = self.client.get(f"pipelines/{pipeline_id}")

        return Pipeline.from_dict(res.json())

    def delete_pipeline(self, pipeline_id: str):
        """Delete a pipeline permanently."""
        self.client.delete(f"pipelines/{pipeline_id}")

    def get_pipeline_app_panel(self, pipeline_id: str, version: int | None = None) -> AppPanel:
        """Retrieve app panel information for a specific pipeline by its ID."""
        res = self.client.get(f"pipelines/{pipeline_id}/app_panel", params={"version": version} if version else None)

        return AppPanel.from_dict(res.json())

    def list_computations(self, pipeline_id: str) -> list[Computation]:
        """Get all computations associated with a specific pipeline."""
        res = self.client.get(f"pipelines/{pipeline_id}/computations")

        return [Computation.from_dict(c) for c in res.json()]

    def update_permissions(self, pipeline_id: str, permissions: Permissions):
        """Update permissions for a pipeline."""
        self.client.post(
            f"pipelines/{pipeline_id}/permissions",
            json=permissions.to_dict(),
        )

    def attach_data_assets(
        self,
        pipeline_id: str,
        attach_params: list[DataAssetAttachParams],
    ) -> list[DataAssetAttachResults]:
        """Attach one or more data assets to a pipeline with optional mount paths."""
        res = self.client.post(
            f"pipelines/{pipeline_id}/data_assets",
            json=[j.to_dict() for j in attach_params],
        )

        return [DataAssetAttachResults.from_dict(c) for c in res.json()]

    def detach_data_assets(self, pipeline_id: str, data_assets: list[str]):
        """Detach one or more data assets from a pipeline by their IDs."""
        self.client.delete(
            f"pipelines/{pipeline_id}/data_assets/",
            json=data_assets,
        )

    def archive_pipeline(self, pipeline_id: str, archive: bool):
        """Archive or unarchive a pipeline to control its visibility and accessibility."""
        self.client.patch(
            f"pipelines/{pipeline_id}/archive",
            params={"archive": archive},
        )

    def search_pipelines(self, search_params: PipelineSearchParams) -> PipelineSearchResults:
        """Search for pipelines with filtering, sorting, and pagination
        options."""
        res = self.client.post("pipelines/search", json=search_params.to_dict())

        return PipelineSearchResults.from_dict(res.json())

    def search_pipelines_iterator(self, search_params: PipelineSearchParams) -> Iterator[Pipeline]:
        """Iterate through all pipelines matching search criteria with automatic pagination."""
        params = search_params.to_dict()
        while True:
            response = self.search_pipelines(search_params=PipelineSearchParams(**params))

            for result in response.results:
                yield result

            if not response.has_more:
                return

            params["next_token"] = response.next_token
