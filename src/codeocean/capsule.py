from __future__ import annotations

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import Optional
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.computation import Computation
from codeocean.data_asset import DataAssetAttachParams, DataAssetAttachResults
from codeocean.enum import StrEnum


class CapsuleStatus(StrEnum):
    NonPublished = "non-published"
    Submitted = "submitted"
    Publishing = "publishing"
    Published = "published"
    Verified = "verified"


@dataclass_json
@dataclass(frozen=True)
class OriginalCapsuleInfo:
    id: Optional[str] = None
    major_version: Optional[int] = None
    minor_version: Optional[int] = None
    name: Optional[str] = None
    created: Optional[int] = None
    public: Optional[bool] = None


@dataclass_json
@dataclass(frozen=True)
class Capsule:
    id: str
    created: int
    name: str
    status: CapsuleStatus
    owner: str
    slug: str
    article: Optional[dict] = None
    cloned_from_url: Optional[str] = None
    description: Optional[str] = None
    field: Optional[str] = None
    keywords: Optional[list[str]] = None
    original_capsule: Optional[OriginalCapsuleInfo] = None
    published_capsule: Optional[str] = None
    submission: Optional[dict] = None
    versions: Optional[list[dict]] = None


@dataclass_json
@dataclass(frozen=True)
class CapsuleSearchParams:
    query: Optional[str] = None
    next_token: Optional[str] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    sort_field: Optional[CapsuleSortBy] = None
    sort_order: Optional[SortOrder] = None
    ownership: Optional[CapsuleOwnership] = None
    status: Optional[CapsuleStatus] = None
    favorite: Optional[bool] = None
    archived: Optional[bool] = None
    filters: Optional[list[SearchFilter]] = None


@dataclass_json
@dataclass(frozen=True)
class CapsuleSearchResults:
    has_more: bool
    results: list[Capsule]
    next_token: Optional[str] = None


@dataclass
class Capsules:

    client: BaseUrlSession

    def get_capsule(self, capsule_id: str) -> Capsule:
        res = self.client.get(f"capsules/{capsule_id}")

        return Capsule.from_dict(res.json())

    def list_computations(self, capsule_id: str) -> list[Computation]:
        res = self.client.get(f"capsules/{capsule_id}/computations")

        return [Computation.from_dict(c) for c in res.json()]

    def attach_data_assets(
            self,
            capsule_id: str,
            attach_params: list[DataAssetAttachParams]) -> list[DataAssetAttachResults]:
        res = self.client.post(
            f"capsules/{capsule_id}/data_assets",
            json=[j.to_dict() for j in attach_params],
        )

        return [DataAssetAttachResults.from_dict(c) for c in res.json()]

    def detach_data_assets(self, capsule_id: str, data_assets: list[str]):
        self.client.delete(
            f"capsules/{capsule_id}/data_assets/",
            json=data_assets,
        )
    
    def search_capsules(self, search_params: CapsuleSearchParams) -> CapsuleSearchResults:
        res = self.client.post("capsules/search", json=search_params.to_dict())

        return CapsuleSearchResults.from_dict(res.json())
