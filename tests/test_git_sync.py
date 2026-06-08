import unittest
from unittest.mock import MagicMock

from codeocean.capsule import Capsules, GitSyncResults
from codeocean.pipeline import Pipelines


class TestGitSync(unittest.TestCase):
    """Test cases for capsule and pipeline Git sync."""

    def _mock_session(self, body):
        """Build a mock session whose post() returns a response with the given JSON body."""
        session = MagicMock()
        response = MagicMock()
        response.json.return_value = body
        session.post.return_value = response
        return session

    def test_sync_capsule_returns_results(self):
        """sync_capsule posts to the capsule sync route and parses the results."""
        session = self._mock_session({"pushed": 2, "pulled": 1, "new_branch": True})
        capsules = Capsules(client=session)

        result = capsules.sync_capsule("cap-123")

        session.post.assert_called_once_with("capsules/cap-123/sync")
        self.assertEqual(result, GitSyncResults(pushed=2, pulled=1, new_branch=True))

    def test_sync_capsule_empty_body_defaults(self):
        """An empty body (all fields omitempty on the server) deserializes to zero defaults."""
        session = self._mock_session({})
        capsules = Capsules(client=session)

        result = capsules.sync_capsule("cap-123")

        self.assertEqual(result, GitSyncResults(pushed=0, pulled=0, new_branch=False))

    def test_sync_pipeline_returns_results(self):
        """sync_pipeline posts to the pipeline sync route and parses the results."""
        session = self._mock_session({"pushed": 0, "pulled": 3, "new_branch": False})
        pipelines = Pipelines(client=session)

        result = pipelines.sync_pipeline("pipe-456")

        session.post.assert_called_once_with("pipelines/pipe-456/sync")
        self.assertEqual(result, GitSyncResults(pushed=0, pulled=3, new_branch=False))
