from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional
from time import sleep, time

from codeocean.enum import StrEnum
from codeocean.folder import Folder, DownloadFileURL


class ComputationState(StrEnum):
    """Current state of a computation during its execution lifecycle."""

    Initializing = "initializing"
    Running = "running"
    Finalizing = "finalizing"
    Completed = "completed"
    Failed = "failed"


class ComputationEndStatus(StrEnum):
    """Final status of a computation once it has completed execution."""

    Succeeded = "succeeded"
    Failed = "failed"
    Stopped = "stopped"


@dataclass_json
@dataclass(frozen=True)
class Param:
    """Parameter information for computations with name and value."""

    name: Optional[str] = field(
        default=None, metadata={"description": "Parameter label/display name"}
    )
    param_name: Optional[str] = field(
        default=None, metadata={"description": "Internal parameter name identifier"}
    )
    value: Optional[str] = field(
        default=None, metadata={"description": "Parameter value as string"}
    )


@dataclass_json
@dataclass(frozen=True)
class PipelineProcess:
    """Information about a process within a pipeline execution."""

    name: str = field(
        metadata={"description": "Pipeline process name as it appears in main.nf"}
    )
    capsule_id: str = field(
        metadata={"description": "ID of the capsule executed in this process"}
    )
    version: Optional[int] = field(
        default=None,
        metadata={"description": "Capsule version if it's a released capsule"},
    )
    public: Optional[bool] = field(
        default=None,
        metadata={"description": "Indicates if the capsule is a Code Ocean public app"},
    )
    parameters: Optional[list[Param]] = field(
        default=None, metadata={"description": "Run parameters for this process"}
    )


@dataclass_json
@dataclass(frozen=True)
class InputDataAsset:
    """Data asset attached to a computation with mount information."""

    id: str = field(metadata={"description": "Attached data asset ID"})
    mount: Optional[str] = field(
        default=None, metadata={"description": "Mount path for the attached data asset"}
    )


@dataclass_json
@dataclass(frozen=True)
class Computation:
    """Represents a Code Ocean computation run with its metadata and execution details."""

    id: str = field(metadata={"description": "Unique computation ID"})
    created: int = field(
        metadata={"description": "Computation creation time (int64 timestamp)"}
    )
    name: str = field(metadata={"description": "Display name of the computation"})
    run_time: int = field(metadata={"description": "Total run time in seconds"})
    state: ComputationState = field(
        metadata={
            "description": "Current state of the computation (initializing, running, finalizing, completed, failed)"
        }
    )
    cloud_workstation: Optional[bool] = field(
        default=None,
        metadata={
            "description": "Indicates whether this computation is a cloud workstation"
        },
    )
    data_assets: Optional[list[InputDataAsset]] = field(
        default=None,
        metadata={"description": "List of data assets attached to this computation"},
    )
    parameters: Optional[list[Param]] = field(
        default=None,
        metadata={"description": "Run parameters used for this computation"},
    )
    nextflow_profile: Optional[str] = field(
        default=None,
        metadata={"description": "Pipeline Nextflow profile used for this computation"},
    )
    processes: Optional[list[PipelineProcess]] = field(
        default=None,
        metadata={
            "description": "Pipeline processes information if this is a pipeline computation"
        },
    )
    end_status: Optional[ComputationEndStatus] = field(
        default=None,
        metadata={
            "description": "Final status once computation is completed (succeeded, failed, stopped)"
        },
    )
    exit_code: Optional[int] = field(
        default=None,
        metadata={
            "description": "Exit code (0 for success, non-zero for failure, 1 for pipeline errors)"
        },
    )
    has_results: Optional[bool] = field(
        default=None,
        metadata={
            "description": "Indicates whether the computation has generated results"
        },
    )
    nextflow_profile: Optional[str] = field(
        default=None,
        metadata={"description": "Pipeline Nextflow profile used for this computation"},
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetsRunParam:
    """Data asset parameter for running computations with mount specification."""

    id: str = field(metadata={"description": "Data asset ID to attach"})
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Mount path where the data asset will be accessible"},
    )


@dataclass_json
@dataclass(frozen=True)
class NamedRunParam:
    """Named parameter for running computations with explicit parameter name."""

    param_name: str = field(
        metadata={"description": "Internal parameter name identifier"}
    )
    value: str = field(metadata={"description": "Parameter value as string"})


@dataclass_json
@dataclass(frozen=True)
class PipelineProcessParams:
    """Parameters for configuring a specific process within a pipeline execution."""

    name: str = field(
        metadata={"description": "Name of the pipeline process to configure"}
    )
    parameters: Optional[list[str]] = field(
        default=None,
        metadata={"description": "Ordered list of parameter values for this process"},
    )
    named_parameters: Optional[list[NamedRunParam]] = field(
        default=None, metadata={"description": "Named parameters for this process"}
    )


@dataclass_json
@dataclass(frozen=True)
class RunParams:
    """Complete parameter set for running capsules or pipelines with data assets and configuration."""

    capsule_id: Optional[str] = field(
        default=None,
        metadata={
            "description": "ID of the capsule to run (required for capsule runs)"
        },
    )
    pipeline_id: Optional[str] = field(
        default=None,
        metadata={
            "description": "ID of the pipeline to run (required for pipeline runs)"
        },
    )
    version: Optional[int] = field(
        default=None, metadata={"description": "Specific version of the capsule to run"}
    )
    resume_run_id: Optional[str] = field(
        default=None,
        metadata={"description": "ID of a previous computation to resume from"},
    )
    nextflow_profile: Optional[str] = field(
        default=None,
        metadata={"description": "Pipeline Nextflow profile configuration"},
    )
    data_assets: Optional[list[DataAssetsRunParam]] = field(
        default=None,
        metadata={
            "description": "List of data assets to attach with their mount paths"
        },
    )
    parameters: Optional[list[str]] = field(
        default=None, metadata={"description": "Ordered list of parameter values"}
    )
    named_parameters: Optional[list[NamedRunParam]] = field(
        default=None, metadata={"description": "Named parameters for the computation"}
    )
    processes: Optional[list[PipelineProcessParams]] = field(
        default=None,
        metadata={"description": "Process-specific parameters for pipeline runs"},
    )


@dataclass
class Computations:
    """Client for interacting with Code Ocean computation APIs."""

    client: BaseUrlSession

    def get_computation(self, computation_id: str) -> Computation:
        """Retrieve metadata and status information for a specific computation by its ID."""
        res = self.client.get(f"computations/{computation_id}")

        return Computation.from_dict(res.json())

    def run_capsule(self, run_params: RunParams) -> Computation:
        """
        Execute a capsule or pipeline with specified parameters and data assets.

        For capsule execution: Set run_params.capsule_id and optionally provide data_assets,
        parameters, or named_parameters.

        For pipeline execution: Set run_params.pipeline_id and optionally provide data_assets,
        processes (with process-specific parameters), and nextflow_profile configuration.

        Typical workflow: 1) run_capsule() to start execution, 2) wait_until_completed() to
        monitor progress, 3) list_computation_results() and get_result_file_download_url()
        to retrieve outputs.
        """
        res = self.client.post("computations", json=run_params.to_dict())

        return Computation.from_dict(res.json())

    def wait_until_completed(
        self,
        computation: Computation,
        polling_interval: float = 5,
        timeout: Optional[float] = None,
    ) -> Computation:
        """
        Poll a computation until it reaches 'Completed' or 'Failed' state with configurable timing.

        Args:
            computation: The computation object to monitor
            polling_interval: Time between status checks in seconds (minimum 5 seconds)
            timeout: Maximum time to wait in seconds, or None for no timeout

        Returns:
            Updated computation object once completed or failed

        Raises:
            ValueError: If polling_interval < 5 or timeout constraints are violated
            TimeoutError: If computation doesn't complete within the timeout period
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
                raise TimeoutError(
                    f"Computation {computation.id} did not complete within {timeout} seconds"
                )

            sleep(polling_interval)

    def list_computation_results(self, computation_id: str, path: str = "") -> Folder:
        """List result files and folders generated by a computation
        at the specified path. Empty path retrieves the /results root folder."""
        data = {
            "path": path,
        }

        res = self.client.post(f"computations/{computation_id}/results", json=data)

        return Folder.from_dict(res.json())

    def get_result_file_download_url(
        self, computation_id: str, path: str
    ) -> DownloadFileURL:
        """Generate a download URL for a specific result file from a computation."""
        res = self.client.get(
            f"computations/{computation_id}/results/download_url",
            params={"path": path},
        )

        return DownloadFileURL.from_dict(res.json())

    def delete_computation(self, computation_id: str):
        """Delete a computation and stop it if currently running."""
        self.client.delete(f"computations/{computation_id}")

    def rename_computation(self, computation_id: str, name: str):
        """Rename an existing computation with a new display name."""
        self.client.patch(f"computations/{computation_id}", params={"name": name})
