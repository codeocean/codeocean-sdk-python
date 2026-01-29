from __future__ import annotations

from dataclasses import dataclass
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional, Iterator

from codeocean.models.capsule import (
    Capsule,
    CapsuleSearchParams,
    CapsuleSearchResults,
    AppPanel
)
from codeocean.models.components import Permissions
from codeocean.models.computation import Computation
from codeocean.models.data_asset import DataAssetAttachParams, DataAssetAttachResults


@dataclass
class Capsules:
    """Client for interacting with Code Ocean capsule APIs."""

    client: BaseUrlSession
    _route: str = "capsules"

    def get_capsule(self, capsule_id: str) -> Capsule:
        """Retrieve metadata for a specific capsule by its ID."""
        res = self.client.get(f"{self._route}/{capsule_id}")

        return Capsule.from_dict(res.json())

    def delete_capsule(self, capsule_id: str):
        """Delete a capsule permanently."""
        self.client.delete(f"{self._route}/{capsule_id}")

    def get_capsule_app_panel(self, capsule_id: str, version: Optional[int] = None) -> AppPanel:
        """Retrieve app panel information for a specific capsule by its ID."""
        res = self.client.get(f"{self._route}/{capsule_id}/app_panel", params={"version": version} if version else None)

        return AppPanel.from_dict(res.json())

    def list_computations(self, capsule_id: str) -> list[Computation]:
        """Get all computations associated with a specific capsule."""
        res = self.client.get(f"{self._route}/{capsule_id}/computations")

        return [Computation.from_dict(c) for c in res.json()]

    def update_permissions(self, capsule_id: str, permissions: Permissions):
        """Update permissions for a capsule."""
        self.client.post(
            f"{self._route}/{capsule_id}/permissions",
            json=permissions.to_dict(),
        )

    def attach_data_assets(
        self,
        capsule_id: str,
        attach_params: list[DataAssetAttachParams],
    ) -> list[DataAssetAttachResults]:
        """Attach one or more data assets to a capsule with optional mount paths."""
        res = self.client.post(
            f"{self._route}/{capsule_id}/data_assets",
            json=[j.to_dict() for j in attach_params],
        )

        return [DataAssetAttachResults.from_dict(c) for c in res.json()]

    def detach_data_assets(self, capsule_id: str, data_assets: list[str]):
        """Detach one or more data assets from a capsule by their IDs."""
        self.client.delete(
            f"{self._route}/{capsule_id}/data_assets/",
            json=data_assets,
        )

    def archive_capsule(self, capsule_id: str, archive: bool):
        """Archive or unarchive a capsule to control its visibility and accessibility."""
        self.client.patch(
            f"{self._route}/{capsule_id}/archive",
            params={"archive": archive},
        )

    def search_capsules(self, search_params: CapsuleSearchParams) -> CapsuleSearchResults:
        """Search for capsules with filtering, sorting, and pagination
        options."""
        res = self.client.post(f"{self._route}/search", json=search_params.to_dict())

        return CapsuleSearchResults.from_dict(res.json())

    def search_capsules_iterator(self, search_params: CapsuleSearchParams) -> Iterator[Capsule]:
        """Iterate through all capsules matching search criteria with automatic pagination."""
        params = search_params.to_dict()
        while True:
            response = self.search_capsules(search_params=CapsuleSearchParams(**params))

            for result in response.results:
                yield result

            if not response.has_more:
                return

            params["next_token"] = response.next_token
