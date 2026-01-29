from __future__ import annotations

from dataclasses import dataclass, field
from dataclasses_json import dataclass_json
from typing import Optional

from codeocean.enum import StrEnum


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
        default=None,
        metadata={"description": "Parameter label/display name"},
    )
    param_name: Optional[str] = field(
        default=None,
        metadata={"description": "Internal parameter name identifier"},
    )
    value: Optional[str] = field(
        default=None,
        metadata={"description": "Parameter value as string"},
    )


@dataclass_json
@dataclass(frozen=True)
class PipelineProcess:
    """Information about a process within a pipeline execution."""

    name: str = field(
        metadata={"description": "Pipeline process name as it appears in main.nf"},
    )
    capsule_id: str = field(
        metadata={"description": "ID of the capsule executed in this process"},
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
        default=None,
        metadata={"description": "Run parameters for this process"},
    )


@dataclass_json
@dataclass(frozen=True)
class InputDataAsset:
    """Data asset attached to a computation with mount information."""

    id: str = field(
        metadata={"description": "Attached data asset ID"},
    )
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Mount path for the attached data asset"},
    )


@dataclass_json
@dataclass(frozen=True)
class Computation:
    """Represents a Code Ocean computation run with its metadata and execution details."""

    id: str = field(
        metadata={"description": "Unique computation ID"},
    )
    created: int = field(
        metadata={"description": "Computation creation time (int64 timestamp)"},
    )
    name: str = field(
        metadata={"description": "Display name of the computation"},
    )
    run_time: int = field(
        metadata={"description": "Total run time in seconds"},
    )
    state: ComputationState = field(
        metadata={
            "description": "Current state of the computation (initializing, running, finalizing, completed, failed)",
        },
    )
    cloud_workstation: Optional[bool] = field(
        default=None,
        metadata={
            "description": "Indicates whether this computation is a cloud workstation",
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
            "description": "Pipeline processes information if this is a pipeline computation",
        },
    )
    end_status: Optional[ComputationEndStatus] = field(
        default=None,
        metadata={
            "description": "Final status once computation is completed (succeeded, failed, stopped)",
        },
    )
    exit_code: Optional[int] = field(
        default=None,
        metadata={
            "description": "Exit code (0 for success, non-zero for failure, 1 for pipeline errors)",
        },
    )
    has_results: Optional[bool] = field(
        default=None,
        metadata={
            "description": "Indicates whether the computation has generated results",
        },
    )


@dataclass_json
@dataclass(frozen=True)
class DataAssetsRunParam:
    """Data asset parameter for running computations with mount specification."""

    id: str = field(
        metadata={"description": "Data asset ID to attach"},
    )
    mount: Optional[str] = field(
        default=None,
        metadata={"description": "Mount path where the data asset will be accessible"},
    )


@dataclass_json
@dataclass(frozen=True)
class NamedRunParam:
    """Named parameter for running computations with explicit parameter name."""

    param_name: str = field(
        metadata={"description": "Internal parameter name identifier"},
    )
    value: str = field(
        metadata={"description": "Parameter value as string"},
    )


@dataclass_json
@dataclass(frozen=True)
class PipelineProcessParams:
    """Parameters for configuring a specific process within a pipeline execution."""

    name: str = field(
        metadata={"description": "Name of the pipeline process as it appears in main.nf"},
    )
    parameters: Optional[list[str]] = field(
        default=None,
        metadata={"description": "Ordered list of parameter values for this process"},
    )
    named_parameters: Optional[list[NamedRunParam]] = field(
        default=None,
        metadata={"description": "Named parameters for this process"},
    )


@dataclass_json
@dataclass(frozen=True)
class RunParams:
    """Complete parameter set for running capsules or pipelines with data assets and configuration."""

    capsule_id: Optional[str] = field(
        default=None,
        metadata={
            "description": "ID of the capsule to run (required for capsule runs)",
        },
    )
    pipeline_id: Optional[str] = field(
        default=None,
        metadata={
            "description": "ID of the pipeline to run (required for pipeline runs)",
        },
    )
    version: Optional[int] = field(
        default=None,
        metadata={"description": "Specific version of the capsule or pipeline to run"},
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
            "description": "List of data assets to attach with their mount paths",
        },
    )
    parameters: Optional[list[str]] = field(
        default=None,
        metadata={"description": "Ordered list of parameter values for the computation"},
    )
    named_parameters: Optional[list[NamedRunParam]] = field(
        default=None,
        metadata={"description": "Named parameters for the computation"},
    )
    processes: Optional[list[PipelineProcessParams]] = field(
        default=None,
        metadata={"description": "Process-specific parameters for pipeline runs"},
    )
