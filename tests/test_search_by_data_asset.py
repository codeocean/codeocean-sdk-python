import unittest
from unittest.mock import MagicMock

from codeocean.capsule import Capsules
from codeocean.pipeline import Pipelines


CAPSULE = {
    "id": "cap-123",
    "created": 1700000000,
    "name": "My Capsule",
    "status": "non_release",
    "owner": "user-1",
    "slug": "1234567",
}

OTHER_CAPSULE = {
    "id": "cap-456",
    "created": 1700000001,
    "name": "My Other Capsule",
    "status": "release",
    "owner": "user-1",
    "slug": "7654321",
}


class TestSearchByDataAsset(unittest.TestCase):
    """Test cases for finding capsules and pipelines by attached data asset."""

    def _mock_session(self, *bodies):
        """Build a mock session whose successive post() calls return the given JSON bodies."""
        session = MagicMock()
        responses = []
        for body in bodies:
            response = MagicMock()
            response.json.return_value = body
            responses.append(response)
        session.post.side_effect = responses
        return session

    def _posted(self, session):
        """Return the (route, body) pairs of every post() call made on the mock session."""
        return [(c.args[0], c.kwargs["json"]) for c in session.post.call_args_list]

    def test_search_capsules_by_data_asset_returns_capsules(self):
        """The data asset ID is sent as the search query and matches are returned."""
        session = self._mock_session({"has_more": False, "results": [CAPSULE]})
        capsules = Capsules(client=session)

        results = capsules.search_capsules_by_data_asset("asset-789")

        [(route, body)] = self._posted(session)
        self.assertEqual(route, "capsules/search")
        self.assertEqual(body["query"], "asset-789")
        self.assertEqual([c.id for c in results], ["cap-123"])
        self.assertEqual(results[0].name, "My Capsule")

    def test_search_capsules_by_data_asset_not_attached(self):
        """A data asset attached to no capsule yields an empty list."""
        session = self._mock_session({"has_more": False, "results": []})
        capsules = Capsules(client=session)

        results = capsules.search_capsules_by_data_asset("asset-789")

        self.assertEqual(results, [])
        self.assertFalse(results)

    def test_search_capsules_by_data_asset_follows_pagination(self):
        """All pages are collected when the first response reports more results."""
        session = self._mock_session(
            {"has_more": True, "results": [CAPSULE], "next_token": "token-1"},
            {"has_more": False, "results": [OTHER_CAPSULE]},
        )
        capsules = Capsules(client=session)

        results = capsules.search_capsules_by_data_asset("asset-789")

        self.assertEqual([c.id for c in results], ["cap-123", "cap-456"])

        posted = self._posted(session)
        self.assertEqual([route for route, _ in posted], ["capsules/search"] * 2)
        self.assertEqual([body["query"] for _, body in posted], ["asset-789"] * 2)
        self.assertIsNone(posted[0][1]["next_token"])
        self.assertEqual(posted[1][1]["next_token"], "token-1")

    def test_search_pipelines_by_data_asset_uses_pipelines_route(self):
        """The pipeline variant searches the pipelines route."""
        session = self._mock_session({"has_more": False, "results": [CAPSULE]})
        pipelines = Pipelines(client=session)

        results = pipelines.search_pipelines_by_data_asset("asset-789")

        [(route, body)] = self._posted(session)
        self.assertEqual(route, "pipelines/search")
        self.assertEqual(body["query"], "asset-789")
        self.assertEqual([p.id for p in results], ["cap-123"])
