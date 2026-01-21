from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterator
from requests_toolbelt.sessions import BaseUrlSession

from codeocean.capsule import (
    Capsule,
    Capsules,
    CapsuleSearchParams,
    CapsuleSearchResults,
    AppPanel,
)
from codeocean.components import Permissions
from codeocean.computation import Computation
from codeocean.data_asset import DataAssetAttachParams, DataAssetAttachResults


@dataclass
class Pipelines:
    """Client for interacting with Code Ocean pipeline APIs."""

    client: BaseUrlSession
    _capsules: Capsules = field(init=False, repr=False)

    def __post_init__(self):
        self._capsules = Capsules(client=self.client, _route="pipelines")

    def get_pipeline(self, pipeline_id: str) -> Capsule:
        """Retrieve metadata for a specific pipeline by its ID."""
        return self._capsules.get_capsule(pipeline_id)

    def delete_pipeline(self, pipeline_id: str):
        """Delete a pipeline permanently."""
        return self._capsules.delete_capsule(pipeline_id)

    def get_pipeline_app_panel(self, pipeline_id: str, version: int | None = None) -> AppPanel:
        """Retrieve app panel information for a specific pipeline by its ID."""
        return self._capsules.get_capsule_app_panel(pipeline_id, version)

    def list_computations(self, pipeline_id: str) -> list[Computation]:
        """Get all computations associated with a specific pipeline."""
        return self._capsules.list_computations(pipeline_id)

    def update_permissions(self, pipeline_id: str, permissions: Permissions):
        """Update permissions for a pipeline."""
        return self._capsules.update_permissions(pipeline_id, permissions)

    def attach_data_assets(
        self,
        pipeline_id: str,
        attach_params: list[DataAssetAttachParams],
    ) -> list[DataAssetAttachResults]:
        """Attach one or more data assets to a pipeline with optional mount paths."""
        return self._capsules.attach_data_assets(pipeline_id, attach_params)

    def detach_data_assets(self, pipeline_id: str, data_assets: list[str]):
        """Detach one or more data assets from a pipeline by their IDs."""
        return self._capsules.detach_data_assets(pipeline_id, data_assets)

    def archive_pipeline(self, pipeline_id: str, archive: bool):
        """Archive or unarchive a pipeline to control its visibility and accessibility."""
        return self._capsules.archive_capsule(pipeline_id, archive)

    def search_pipelines(self, search_params: CapsuleSearchParams) -> CapsuleSearchResults:
        """Search for pipelines with filtering, sorting, and pagination options."""
        return self._capsules.search_capsules(search_params)

    def search_pipelines_iterator(self, search_params: CapsuleSearchParams) -> Iterator[Capsule]:
        """Iterate through all pipelines matching search criteria with automatic pagination."""
        return self._capsules.search_capsules_iterator(search_params)
