from __future__ import annotations

from dataclasses import dataclass

from codeocean.capsule import Capsules


@dataclass
class Pipelines(Capsules):
    """Client for interacting with Code Ocean pipeline APIs."""

    _route: str = "pipelines"

    # Aliases for pipeline-specific naming
    get_pipeline = Capsules.get_capsule
    delete_pipeline = Capsules.delete_capsule
    get_pipeline_app_panel = Capsules.get_capsule_app_panel
    archive_pipeline = Capsules.archive_capsule
    search_pipelines = Capsules.search_capsules
    search_pipelines_iterator = Capsules.search_capsules_iterator
