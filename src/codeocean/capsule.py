from __future__ import annotations

from dataclasses import dataclass
from requests_toolbelt.sessions import BaseUrlSession
from time import sleep, time
from typing import Optional, Iterator

from codeocean.models.capsule import (
    Capsule,
    CapsuleReleaseJob,
    CapsuleReleaseJobStatus,
    CapsuleSearchParams,
    CapsuleSearchResults,
    AppPanel,
    GitSyncResults,
)
# Related release models re-exported for convenient access from this module
from codeocean.models.capsule import (  # noqa: F401
    Version,
    CapsuleReleaseValidationIssues,
)
# Re-exports for backward compatibility
from codeocean.models.capsule import (  # noqa: F401
    CapsuleStatus,
    CapsuleSortBy,
    OriginalCapsuleInfo,
    AppPanelDataAssetKind,
    AppPanelParameterType,
    AppPanelCategories,
    AppPanelParameters,
    AppPanelGeneral,
    AppPanelDataAsset,
    AppPanelResult,
    AppPanelProcess,
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

    def get_permissions(self, capsule_id: str) -> Permissions:
        """Get permissions for a specific capsule."""
        res = self.client.get(f"{self._route}/{capsule_id}/permissions")

        return Permissions.from_dict(res.json())

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

    def sync_capsule(self, capsule_id: str) -> GitSyncResults:
        """Sync a capsule with its linked external Git repository."""
        res = self.client.post(f"{self._route}/{capsule_id}/sync")

        return GitSyncResults.from_dict(res.json())

    def release_capsule(self, capsule_id: str) -> CapsuleReleaseJob:
        """Start releasing a new version of an already-released capsule.

        Only subsequent releases are supported - the initial release must be done through the
        app. The release runs asynchronously: this returns a CapsuleReleaseJob with a job_id;
        poll it with get_release_job (or wait_until_release_completed) until the status is
        terminal, at which point release_capsule and release_version are populated.

        Raises:
            codeocean.error.Error: 400 if the capsule has never been released; 403 if the
                capsule does not meet the release requirements - the body carried in
                Error.data can be parsed with CapsuleReleaseValidationIssues.from_dict.
        """
        res = self.client.post(f"{self._route}/{capsule_id}/release")

        return CapsuleReleaseJob.from_dict(res.json())

    def get_release_job(self, capsule_id: str, job_id: str) -> CapsuleReleaseJob:
        """Get the status of a capsule release job.

        On completion the returned job's release_capsule and release_version identify the
        newly released capsule version.
        """
        res = self.client.get(f"{self._route}/{capsule_id}/release/{job_id}")

        return CapsuleReleaseJob.from_dict(res.json())

    def wait_until_release_completed(
        self,
        capsule_id: str,
        job: CapsuleReleaseJob,
        polling_interval: float = 5,
        timeout: Optional[float] = None,
    ) -> CapsuleReleaseJob:
        """Poll a release job until it reaches a terminal state.

        Args:
            capsule_id: The capsule (or pipeline) the release job belongs to
            job: The release job to monitor (as returned by release_capsule)
            polling_interval: Time between status checks in seconds (minimum 5 seconds)
            timeout: Maximum time to wait in seconds, or None for no timeout

        Returns:
            Updated release job once it has completed, failed, or been canceled

        Raises:
            ValueError: If polling_interval < 5 or timeout constraints are violated
            TimeoutError: If the job doesn't reach a terminal state within the timeout period
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
        terminal = [
            CapsuleReleaseJobStatus.Completed,
            CapsuleReleaseJobStatus.Failed,
            CapsuleReleaseJobStatus.Canceled,
        ]
        t0 = time()
        while True:
            current = self.get_release_job(capsule_id, job.job_id)

            if current.status in terminal:
                return current

            if timeout is not None and (time() - t0) > timeout:
                raise TimeoutError(
                    f"Release job {job.job_id} did not complete within {timeout} seconds"
                )

            sleep(polling_interval)

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
