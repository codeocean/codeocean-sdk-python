import unittest
from unittest.mock import MagicMock

from codeocean.capsule import (
    Capsules,
    CapsuleReleaseJob,
    CapsuleReleaseJobStatus,
    CapsuleReleaseValidationIssues,
    Version,
)
from codeocean.pipeline import Pipelines


class TestRelease(unittest.TestCase):
    """Test cases for releasing capsules and pipelines and polling the release job."""

    def _mock_session(self, post_body=None, get_body=None):
        """Build a mock session whose post()/get() return responses with the given JSON."""
        session = MagicMock()
        post_response = MagicMock()
        post_response.json.return_value = post_body or {}
        session.post.return_value = post_response
        get_response = MagicMock()
        get_response.json.return_value = get_body or {}
        session.get.return_value = get_response
        return session

    def test_release_capsule_returns_job(self):
        """release_capsule posts to the capsule release route and parses the job."""
        session = self._mock_session(post_body={"job_id": "job-1", "status": "created"})
        capsules = Capsules(client=session)

        result = capsules.release_capsule("cap-123")

        session.post.assert_called_once_with("capsules/cap-123/release")
        self.assertEqual(
            result,
            CapsuleReleaseJob(job_id="job-1", status=CapsuleReleaseJobStatus.Created),
        )

    def test_release_pipeline_returns_job(self):
        """release_pipeline posts to the pipeline release route via the capsules delegate."""
        session = self._mock_session(post_body={"job_id": "job-2", "status": "started"})
        pipelines = Pipelines(client=session)

        result = pipelines.release_pipeline("pipe-456")

        session.post.assert_called_once_with("pipelines/pipe-456/release")
        self.assertEqual(result.job_id, "job-2")
        self.assertEqual(result.status, CapsuleReleaseJobStatus.Started)

    def test_get_release_job_completed(self):
        """A completed job carries release_capsule and release_version."""
        body = {
            "job_id": "job-1",
            "status": "completed",
            "started": 1700000000,
            "duration": 42,
            "release_capsule": "pub-cap-999",
            "release_version": {
                "major_version": 2,
                "minor_version": 5,
                "release_time": 1700000100,
            },
        }
        session = self._mock_session(get_body=body)
        capsules = Capsules(client=session)

        result = capsules.get_release_job("cap-123", "job-1")

        session.get.assert_called_once_with("capsules/cap-123/release/job-1")
        self.assertEqual(
            result,
            CapsuleReleaseJob(
                job_id="job-1",
                status=CapsuleReleaseJobStatus.Completed,
                started=1700000000,
                duration=42,
                release_capsule="pub-cap-999",
                release_version=Version(
                    major_version=2,
                    minor_version=5,
                    release_time=1700000100,
                ),
            ),
        )

    def test_get_release_job_pipeline_route(self):
        """get_release_job delegates to the pipeline release-job route."""
        session = self._mock_session(get_body={"job_id": "job-2", "status": "started"})
        pipelines = Pipelines(client=session)

        pipelines.get_release_job("pipe-456", "job-2")

        session.get.assert_called_once_with("pipelines/pipe-456/release/job-2")

    def test_wait_until_release_completed_returns_terminal_job(self):
        """wait_until_release_completed returns immediately once the job is terminal."""
        session = self._mock_session(get_body={"job_id": "job-1", "status": "completed"})
        capsules = Capsules(client=session)
        job = CapsuleReleaseJob(job_id="job-1", status=CapsuleReleaseJobStatus.Created)

        result = capsules.wait_until_release_completed("cap-123", job)

        session.get.assert_called_once_with("capsules/cap-123/release/job-1")
        self.assertEqual(result.status, CapsuleReleaseJobStatus.Completed)

    def test_wait_until_release_completed_rejects_short_interval(self):
        """A polling interval below 5 seconds is rejected."""
        capsules = Capsules(client=self._mock_session())
        job = CapsuleReleaseJob(job_id="job-1", status=CapsuleReleaseJobStatus.Created)

        with self.assertRaises(ValueError):
            capsules.wait_until_release_completed("cap-123", job, polling_interval=1)

    def test_validation_issues_parse_from_403_body(self):
        """The 403 validation-issues body (issue-only flags) parses into the typed model."""
        body = {"missing_reproducible_run": True, "git_out_of_sync": True}

        issues = CapsuleReleaseValidationIssues.from_dict(body)

        self.assertTrue(issues.missing_reproducible_run)
        self.assertTrue(issues.git_out_of_sync)
        # Requirements that are met are simply absent from the body.
        self.assertIsNone(issues.uncommitted_files)
        self.assertIsNone(issues.invalid_app_panel)
