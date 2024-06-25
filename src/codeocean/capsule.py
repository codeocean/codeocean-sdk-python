from dataclasses import dataclass
from dataclasses_json import dataclass_json
from enum import StrEnum
from typing import Optional
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.computation import Computation
from codeocean.data_asset import DataAssetAttachParams, DataAssetAttachResults


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
