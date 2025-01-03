from __future__ import annotations

from dataclasses_json import dataclass_json
from dataclasses import dataclass
from requests_toolbelt.sessions import BaseUrlSession
from time import sleep, time
from typing import Optional

from codeocean.components import Ownership, SortOrder, SearchFilter, Permissions
from codeocean.computation import PipelineProcess, Param
from codeocean.enum import StrEnum
from codeocean.folder import Folder, DownloadFileURL


class DataAssetType(StrEnum):
    Dataset = "dataset"
    Result = "result"
    Combined = "combined"
    Model = "model"


class DataAssetState(StrEnum):
    Draft = "draft"
    Ready = "ready"
    Failed = "failed"


@dataclass_json
@dataclass(frozen=True)
class Provenance:
    commit: Optional[str] = None
    run_script: Optional[str] = None
    docker_image: Optional[str] = None
    capsule: Optional[str] = None
    data_assets: Optional[list[str]] = None


class DataAssetOrigin(StrEnum):
    Local = "local"
    AWS = "aws"
    GCP = "gcp"


@dataclass_json
@dataclass(frozen=True)
class SourceBucket:
    origin: DataAssetOrigin
    bucket: Optional[str] = None
    prefix: Optional[str] = None
    external: Optional[bool] = None


@dataclass_json
@dataclass(frozen=True)
class AppParameter:
    name: str
    value: str


@dataclass_json
@dataclass(frozen=True)
class ResultsInfo:
    capsule_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    version: Optional[int] = None
    commit: Optional[str] = None
    run_script: Optional[str] = None
    data_assets: Optional[list[str]] = None
    parameters: Optional[list[Param]] = None
    processes: Optional[list[PipelineProcess]] = None


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
    files: Optional[int] = None
    size: Optional[int] = None
    description: Optional[str] = None
    tags: Optional[list[str]] = None
    provenance: Optional[Provenance] = None
    source_bucket: Optional[SourceBucket] = None
    custom_metadata: Optional[dict] = None
    app_parameters: Optional[list[AppParameter]] = None
    contained_data_assets: Optional[list[ContainedDataAsset]] = None
    last_transferred: Optional[int] = None
    transfer_error: Optional[str] = None
    failure_reason: Optional[str] = None


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
    results_info: Optional[ResultsInfo] = None


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


class DataAssetSearchOrigin(StrEnum):
    Internal = "internal"
    External = "external"


@dataclass_json
@dataclass(frozen=True)
class DataAssetSearchParams:
    query: Optional[str] = None
    next_token: Optional[str] = None
    offset: Optional[int] = None
    limit: Optional[int] = None
    sort_field: Optional[DataAssetSortBy] = None
    sort_order: Optional[SortOrder] = None
    type: Optional[DataAssetType] = None
    ownership: Optional[Ownership] = None
    origin: Optional[DataAssetSearchOrigin] = None
    favorite: Optional[bool] = None
    archived: Optional[bool] = None
    filters: Optional[list[SearchFilter]] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetSearchResults:
    has_more: bool
    results: list[DataAsset]
    next_token: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class ContainedDataAsset:
    id: Optional[str] = None
    mount: Optional[str] = None
    size: Optional[int] = None


@dataclass_json
@dataclass(frozen=True)
class TransferDataParams:
    target: Target
    force: Optional[bool] = None


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

    def wait_until_ready(
        self,
        data_asset: DataAsset,
        polling_interval: float = 5,
        timeout: float | None = None,
    ) -> DataAsset:
        """
        Polls the given data asset until it reaches the 'Ready' or 'Failed' state.

        - `polling_interval` and `timeout` are in seconds
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
                raise TimeoutError(f"Data asset {data_asset.id} was not ready within {timeout} seconds")

            sleep(polling_interval)

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

    def list_data_asset_files(self, data_asset_id: str, path: str = "") -> Folder:
        data = {
            "path": path,
        }

        res = self.client.post(f"data_assets/{data_asset_id}/files", json=data)

        return Folder.from_dict(res.json())

    def get_data_asset_file_download_url(self, data_asset_id: str, path: str) -> DownloadFileURL:
        res = self.client.get(
            f"data_assets/{data_asset_id}/files/download_url",
            params={"path": path},
        )

        return DownloadFileURL.from_dict(res.json())

    def transfer_data_asset(self, data_asset_id: str, transfer_params: TransferDataParams):
        self.client.post(
            f"data_assets/{data_asset_id}/transfer",
            json=transfer_params.to_dict()
        )
