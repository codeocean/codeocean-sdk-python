from __future__ import annotations

from dataclasses import dataclass, field as dataclass_field
from dataclasses_json import dataclass_json
from typing import Optional, Iterator
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.components import Ownership, SortOrder, SearchFilter, Permissions
from codeocean.computation import Computation
from codeocean.data_asset import DataAssetAttachParams, DataAssetAttachResults
from codeocean.enum import StrEnum


class CapsuleStatus(StrEnum):
    """Status of a capsule indicating its release state."""

    NonRelease = "non_release"
    Release = "release"


class CapsuleSortBy(StrEnum):
    """Fields available for sorting capsule search results."""

    Created = "created"
    LastAccessed = "last_accessed"
    Name = "name"


@dataclass_json
@dataclass(frozen=True)
class OriginalCapsuleInfo:
    """Information about the original capsule when this capsule is duplicated from
    another."""

    id: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Original capsule ID"},
    )
    major_version: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Original capsule major version"},
    )
    minor_version: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Original capsule minor version"},
    )
    name: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Original capsule name"},
    )
    created: Optional[int] = dataclass_field(
        default=None,
        metadata={"description": "Original capsule creation time (int64 timestamp)"},
    )
    public: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Indicates whether the original capsule is public"},
    )


@dataclass_json
@dataclass(frozen=True)
class Capsule:
    """Represents a Code Ocean capsule with its metadata and properties."""

    id: str = dataclass_field(
        metadata={"description": "Capsule ID"},
    )
    created: int = dataclass_field(
        metadata={"description": "Capsule creation time (int64 timestamp)"},
    )
    name: str = dataclass_field(
        metadata={"description": "Capsule display name"},
    )
    status: CapsuleStatus = dataclass_field(
        metadata={"description": "Status of the capsule (non_release or release)"},
    )
    owner: str = dataclass_field(
        metadata={"description": "Capsule owner's ID"},
    )
    slug: str = dataclass_field(
        metadata={"description": "Alternate capsule ID (URL-friendly identifier)"},
    )
    article: Optional[dict] = dataclass_field(
        default=None,
        metadata={
            "description": "Capsule article info with URL, ID, DOI, "
            "citation, state, name, journal_name, and "
            "publish_time"
        },
    )
    cloned_from_url: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "URL to external Git repository linked to capsule"},
    )
    description: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Capsule description"},
    )
    field: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Capsule research field"},
    )
    tags: Optional[list[str]] = dataclass_field(
        default=None,
        metadata={"description": "List of tags associated with the capsule"},
    )
    original_capsule: Optional[OriginalCapsuleInfo] = dataclass_field(
        default=None,
        metadata={
            "description": "Original capsule info when this capsule is duplicated from another"
        },
    )
    release_capsule: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Release capsule ID"},
    )
    submission: Optional[dict] = dataclass_field(
        default=None,
        metadata={
            "description": "Submission info with timestamp, commit hash, "
            "verification_capsule, verified status, and "
            "verified_timestamp"
        },
    )
    versions: Optional[list[dict]] = dataclass_field(
        default=None,
        metadata={
            "description": "Capsule versions with major_version, minor_version, release_time, and DOI"
        },
    )


@dataclass_json
@dataclass(frozen=True)
class CapsuleSearchParams:
    """Parameters for searching capsules with various filters and pagination
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
    sort_field: Optional[CapsuleSortBy] = dataclass_field(
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
    status: Optional[CapsuleStatus] = dataclass_field(
        default=None,
        metadata={"description": "Filter by status (release or non_release) - defaults to all"},
    )
    favorite: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Search only favorite capsules"},
    )
    archived: Optional[bool] = dataclass_field(
        default=None,
        metadata={"description": "Search only archived capsules"},
    )
    filters: Optional[list[SearchFilter]] = dataclass_field(
        default=None,
        metadata={
            "description": "Additional field-level filters for name, description, tags, or custom fields"
        },
    )


@dataclass_json
@dataclass(frozen=True)
class CapsuleSearchResults:
    """Results from a capsule search operation with pagination support."""

    has_more: bool = dataclass_field(
        metadata={"description": "Indicates if there are more results available"},
    )
    results: list[Capsule] = dataclass_field(
        metadata={"description": "Array of capsules found matching the search criteria"},
    )
    next_token: Optional[str] = dataclass_field(
        default=None,
        metadata={"description": "Token for fetching the next page of results"},
    )


@dataclass
class Capsules:
    """Client for interacting with Code Ocean capsule APIs."""

    client: BaseUrlSession

    def get_capsule(self, capsule_id: str) -> Capsule:
        """Retrieve metadata for a specific capsule by its ID."""
        res = self.client.get(f"capsules/{capsule_id}")

        return Capsule.from_dict(res.json())

    def list_computations(self, capsule_id: str) -> list[Computation]:
        """Get all computations associated with a specific capsule."""
        res = self.client.get(f"capsules/{capsule_id}/computations")

        return [Computation.from_dict(c) for c in res.json()]

    def update_permissions(self, capsule_id: str, permissions: Permissions):
        """Update permissions for a capsule."""
        self.client.post(
            f"capsules/{capsule_id}/permissions",
            json=permissions.to_dict(),
        )

    def attach_data_assets(
        self,
        capsule_id: str,
        attach_params: list[DataAssetAttachParams],
    ) -> list[DataAssetAttachResults]:
        """Attach one or more data assets to a capsule with optional mount paths."""
        res = self.client.post(
            f"capsules/{capsule_id}/data_assets",
            json=[j.to_dict() for j in attach_params],
        )

        return [DataAssetAttachResults.from_dict(c) for c in res.json()]

    def detach_data_assets(self, capsule_id: str, data_assets: list[str]):
        """Detach one or more data assets from a capsule by their IDs."""
        self.client.delete(
            f"capsules/{capsule_id}/data_assets/",
            json=data_assets,
        )

    def search_capsules(self, search_params: CapsuleSearchParams) -> CapsuleSearchResults:
        """Search for capsules with filtering, sorting, and pagination
        options."""
        res = self.client.post("capsules/search", json=search_params.to_dict())

        return CapsuleSearchResults.from_dict(res.json())

    def search_capsules_iterator(self, search_params: CapsuleSearchParams) -> Iterator[Capsule]:
        """Iterate through all capsules matching search criteria with automatic pagination."""
        params = search_params.to_dict()
        while True:
            response = self.search_capsules(search_params=CapsuleSearchParams(**params))

            for result in response.results:
                yield result

            if not response.has_more:
                return

            params["next_token"] = response.next_token
