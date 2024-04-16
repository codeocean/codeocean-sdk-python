from dataclasses import dataclass
from dataclasses_json import dataclass_json
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional
from time import sleep
import sys
if sys.version_info >= (3, 11):
    from enum import StrEnum
else:
    from backports.strenum import StrEnum

class ComputationState(StrEnum):
    Initializing = "initializing"
    Running = "running"
    Finalizing = "finalizing"
    Completed = "completed"
    Failed = "failed"


class ComputationEndStatus(StrEnum):
    Succeeded = "succeeded"
    Failed = "failed"
    Stopped = "stopped"


@dataclass_json
@dataclass(frozen=True)
class Param:
    name: Optional[str] = None
    param_name: Optional[str] = None
    value: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class PipelineProcess:
    name: str
    capsule_id: str
    version: Optional[int] = None
    public: Optional[bool] = None
    parameters: Optional[list[Param]] = None


@dataclass_json
@dataclass(frozen=True)
class InputDataAsset:
    id: str
    mount: Optional[str] = None


@dataclass_json
@dataclass(frozen=True)
class Computation:
    id: str
    created: int
    name: str
    state: ComputationState
    run_time: int
    cloud_workstation: Optional[bool] = None
    data_assets: Optional[list[InputDataAsset]] = None
    end_status: Optional[ComputationEndStatus] = None
    has_results: Optional[bool] = None
    parameters: Optional[list[Param]] = None
    processes: Optional[list[PipelineProcess]] = None


@dataclass_json
@dataclass(frozen=True)
class DataAssetsRunParam:
    id: str
    mount: str


@dataclass_json
@dataclass(frozen=True)
class NamedRunParam:
    param_name: str
    value: str


@dataclass_json
@dataclass(frozen=True)
class PipelineProcessParams:
    name: str
    parameters: Optional[list[str]] = None
    named_parameters: Optional[list[NamedRunParam]] = None


@dataclass_json
@dataclass(frozen=True)
class RunParams:
    capsule_id: Optional[str] = None
    pipeline_id: Optional[str] = None
    version: Optional[int] = None
    resume_run_id: Optional[str] = None
    data_assets: Optional[list[DataAssetsRunParam]] = None
    parameters: Optional[list[str]] = None
    named_parameters: Optional[list[NamedRunParam]] = None
    processes: Optional[list[PipelineProcessParams]] = None


@dataclass_json
@dataclass(frozen=True)
class FolderItem:
    name: str
    path: str
    type: str
    size: Optional[int] = None


@dataclass_json
@dataclass(frozen=True)
class Folder:
    items: list[FolderItem]


@dataclass_json
@dataclass(frozen=True)
class ListFolderParams:
    path: str


@dataclass_json
@dataclass(frozen=True)
class DownloadFileURL:
    url: str


@dataclass
class Computations:

    client: BaseUrlSession

    def get_computation(self, computation_id: str) -> Computation:
        res = self.client.get(f"computations/{computation_id}")

        return Computation.from_dict(res.json())

    def run_capsule(self, run_params: RunParams) -> Computation:
        res = self.client.post("computations", json=run_params.to_dict())

        return Computation.from_dict(res.json())

    def wait_until_completed(self, computation: Computation) -> Computation:
        """
        Polls the given computation until it reaches the 'Completed' or 'Failed' state.
        """
        while True:
            comp = self.get_computation(computation.id)

            if comp.state in [ComputationState.Completed, ComputationState.Failed]:
                return comp

            sleep(5)

    def list_computation_results(self, computation_id: str, path: str = "") -> Folder:
        data = {
            "path": path,
        }

        res = self.client.post(f"computations/{computation_id}/results", json=data)

        return Folder.from_dict(res.json())

    def get_result_file_download_url(self, computation_id: str, path: str) -> DownloadFileURL:
        res = self.client.get(
            f"computations/{computation_id}/results/download_url",
            params={"path": path},
        )

        return DownloadFileURL.from_dict(res.json())

    def delete_computation(self, computation_id: str):
        self.client.delete(f"computations/{computation_id}")
