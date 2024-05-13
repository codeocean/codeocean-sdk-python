from dataclasses_json import dataclass_json
from dataclasses import dataclass
from enum import StrEnum
from requests_toolbelt.sessions import BaseUrlSession
from time import sleep
from typing import Optional

from codeocean.components import SortOrder, SearchFilter, Permissions


class DataAssetType(StrEnum):
    Dataset = "dataset"
    Result = "result"


class DataAssetState(StrEnum):
    Draft = "draft"
    Ready = "ready"
    Failed = "failed"


@dataclass_json
@dataclass(frozen=True)
class Provenance:
    commit: str
    run_script: str
    data_assets: str
    docker_image: str
    capsule: str


class DataAssetOrigin(StrEnum):
    Local = "local"
    AWS = "aws"
    GCP = "gcp"


@dataclass_json
@dataclass(frozen=True)
class SourceBucket:
    origin: DataAssetOrigin
    bucket: str
    prefix: str
    external: bool


@dataclass_json
@dataclass(frozen=True)
class AppParameter:
    name: str
    value: str


@dataclass_json
@dataclass(frozen=True)
class DataAsset:
    id: str
    created: int
    name: str
    mount: str
    state: DataAssetState
    type: DataAssetType
    last_used: int
    app_parameters: Optional[list[AppParameter]] = None
    custom_metadata: Optional[dict] = None
    description: Optional[str] = None
    failure_reason: Optional[str] = None
    files: Optional[int] = None
    provenance: Optional[Provenance] = None
    size: Optional[int] = None
    source_bucket: Optional[SourceBucket] = None
    tags: Optional[list[str]] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetUpdateParams:
    name: str
    description: str
    tags: list[str]
    mount: str
    custom_metadata: Optional[dict] = None


@dataclass_json
@dataclass(frozen=True)
class AWSS3Source:
    bucket: str
    prefix: Optional[str] = None
    keep_on_external_storage: Optional[bool] = None
    public: Optional[bool] = None


@dataclass_json
@dataclass(frozen=True)
class GCPCloudStorageSource:
    bucket: str
    client_id: Optional[str] = None
    client_secret: Optional[str] = None
    prefix: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class ComputationSource:
    id: str
    path: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class Source:
    aws: Optional[AWSS3Source] = None
    gcp: Optional[GCPCloudStorageSource] = None
    computation: Optional[ComputationSource] = None


@dataclass_json
@dataclass(frozen=True)
class AWSS3Target:
    bucket: str
    prefix: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class Target:
    aws: Optional[AWSS3Target] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetParams:
    name: str
    tags: list[str]
    mount: str
    description: Optional[str] = None
    source: Optional[Source] = None
    target: Optional[Target] = None
    custom_metadata: Optional[dict] = None
    data_asset_ids: Optional[list[str]] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetAttachParams:
    id: str
    mount: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetAttachResults:
    id: str
    mount: str
    mount_state: str
    job_id: str
    external: bool
    ready: bool


class DataAssetSortBy(StrEnum):
    Created = "created"
    Type = "type"
    Name = "name"
    Size = "size"


class DataAssetOwnership(StrEnum):
    Private = "private"
    Shared = "shared"
    Created = "created"


class DataAssetSearchOrigin(StrEnum):
    Internal = "internal"
    External = "external"


@dataclass_json
@dataclass(frozen=True)
class DataAssetSearchParams:
    limit: int
    offset: int
    archived: bool
    favorite: bool
    query: Optional[str] = None
    sort_field: Optional[DataAssetSortBy] = None
    sort_order: Optional[SortOrder] = None
    type: Optional[DataAssetType] = None
    ownership: Optional[DataAssetOwnership] = None
    origin: Optional[DataAssetSearchOrigin] = None
    filters: Optional[list[SearchFilter]] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetSearchResults:
    has_more: bool
    results: list[DataAsset]


@dataclass
class DataAssets:

    client: BaseUrlSession

    def get_data_asset(self, data_asset_id: str) -> DataAsset:
        res = self.client.get(f"data_assets/{data_asset_id}")

        return DataAsset.from_dict(res.json())

    def update_metadata(self, data_asset_id: str, update_params: DataAssetUpdateParams) -> DataAsset:
        res = self.client.put(f"data_assets/{data_asset_id}", json=update_params.to_dict())

        return DataAsset.from_dict(res.json())

    def create_data_asset(self, data_asset_params: DataAssetParams) -> DataAsset:
        res = self.client.post("data_assets", json=data_asset_params.to_dict())

        return DataAsset.from_dict(res.json())

    def wait_until_ready(self, data_asset: DataAsset) -> DataAsset:
        """
        Polls the given data asset until it reaches the 'Ready' or 'Failed' state.
        """
        while True:
            da = self.get_data_asset(data_asset.id)

            if da.state in [DataAssetState.Ready, DataAssetState.Failed]:
                return da

            sleep(5)

    def delete_data_asset(self, data_asset_id: str):
        self.client.delete(f"data_assets/{data_asset_id}")

    def update_permissions(self, data_asset_id: str, permissions: Permissions):
        self.client.post(
            f"data_assets/{data_asset_id}/permissions",
            json=permissions.to_dict(),
        )

    def archive_data_asset(self, data_asset_id: str, archive: bool):
        self.client.patch(
            f"data_assets/{data_asset_id}/archive",
            params={"archive": archive},
        )

    def search_data_assets(self, search_params: DataAssetSearchParams) -> DataAssetSearchResults:
        res = self.client.post("data_assets/search", json=search_params.to_dict())

        return DataAssetSearchResults.from_dict(res.json())
