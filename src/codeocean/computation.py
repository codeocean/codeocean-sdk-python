from __future__ import annotations

from dataclasses import dataclass
from dataclasses_json import dataclass_json
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional
from time import sleep, time

from codeocean.enum import StrEnum
from codeocean.folder import Folder, DownloadFileURL


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
    run_time: int
    state: ComputationState
    cloud_workstation: Optional[bool] = None
    data_assets: Optional[list[InputDataAsset]] = None
    parameters: Optional[list[Param]] = None
    processes: Optional[list[PipelineProcess]] = None
    end_status: Optional[ComputationEndStatus] = None
    exit_code: Optional[int] = None
    has_results: Optional[bool] = None


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


@dataclass
class Computations:

    client: BaseUrlSession

    def get_computation(self, computation_id: str) -> Computation:
        res = self.client.get(f"computations/{computation_id}")

        return Computation.from_dict(res.json())

    def run_capsule(self, run_params: RunParams) -> Computation:
        res = self.client.post("computations", json=run_params.to_dict())

        return Computation.from_dict(res.json())

    def wait_until_completed(
        self,
        computation: Computation,
        polling_interval: float = 5,
        timeout: Optional[float] = None,
    ) -> Computation:
        """
        Polls the given computation until it reaches the 'Completed' or 'Failed' state.

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
            comp = self.get_computation(computation.id)

            if comp.state in [ComputationState.Completed, ComputationState.Failed]:
                return comp

            if timeout is not None and (time() - t0) > timeout:
                raise TimeoutError(f"Computation {computation.id} did not complete within {timeout} seconds")

            sleep(polling_interval)

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

    def rename_computation(self, computation_id: str, name: str):
        self.client.patch(
            f"computations/{computation_id}",
            params={"name": name}
            )
