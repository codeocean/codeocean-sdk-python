import unittest
from unittest.mock import MagicMock

from codeocean.capsule import Capsules, CapsuleReleaseResults, ReleaseVersion
from codeocean.pipeline import Pipelines


class TestRelease(unittest.TestCase):
    """Test cases for releasing capsules and pipelines."""

    def _mock_session(self, body):
        """Build a mock session whose post() returns a response with the given JSON body."""
        session = MagicMock()
        response = MagicMock()
        response.json.return_value = body
        session.post.return_value = response
        return session

    def test_release_capsule_returns_results(self):
        """release_capsule posts to the capsule release route and parses the results."""
        body = {
            "reproducible_run": True,
            "all_tracked": True,
            "metadata": True,
            "no_credentials": True,
            "default_branch": True,
            "git_sync": True,
            "pipeline_capsules_released": True,
            "release_functionality": True,
            "valid_app_panel": True,
            "post_run_capsule_released": True,
            "release_capsule": "pub-cap-999",
            "release_version": {
                "major_version": 2,
                "minor_version": 5,
                "release_time": 1700000000,
                "doi": "10.1234/example",
            },
        }
        session = self._mock_session(body)
        capsules = Capsules(client=session)

        result = capsules.release_capsule("cap-123")

        session.post.assert_called_once_with("capsules/cap-123/release")
        self.assertEqual(
            result,
            CapsuleReleaseResults(
                reproducible_run=True,
                all_tracked=True,
                metadata=True,
                no_credentials=True,
                default_branch=True,
                git_sync=True,
                pipeline_capsules_released=True,
                release_functionality=True,
                valid_app_panel=True,
                post_run_capsule_released=True,
                release_capsule="pub-cap-999",
                release_version=ReleaseVersion(
                    major_version=2,
                    minor_version=5,
                    release_time=1700000000,
                    doi="10.1234/example",
                ),
            ),
        )

    def test_release_capsule_empty_body_defaults(self):
        """An empty body (all fields optional on the server) deserializes to None defaults."""
        session = self._mock_session({})
        capsules = Capsules(client=session)

        result = capsules.release_capsule("cap-123")

        self.assertEqual(result, CapsuleReleaseResults())
        self.assertIsNone(result.release_capsule)
        self.assertIsNone(result.release_version)

    def test_release_pipeline_returns_results(self):
        """release_pipeline posts to the pipeline release route via the capsules delegate."""
        body = {
            "reproducible_run": True,
            "release_capsule": "pub-pipe-777",
            "release_version": {
                "major_version": 1,
                "minor_version": 0,
                "release_time": 1699999999,
            },
        }
        session = self._mock_session(body)
        pipelines = Pipelines(client=session)

        result = pipelines.release_pipeline("pipe-456")

        session.post.assert_called_once_with("pipelines/pipe-456/release")
        self.assertEqual(
            result,
            CapsuleReleaseResults(
                reproducible_run=True,
                release_capsule="pub-pipe-777",
                release_version=ReleaseVersion(
                    major_version=1,
                    minor_version=0,
                    release_time=1699999999,
                ),
            ),
        )
