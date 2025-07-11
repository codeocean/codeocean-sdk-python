import unittest
from unittest.mock import patch
from urllib3.util import Retry

from codeocean.client import CodeOcean, MIN_SERVER_VERSION


class TestClient(unittest.TestCase):
    """Test cases for the CodeOcean client class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_domain = "https://codeocean.acme.com"
        self.test_token = "test_token_123"
        self.test_agent_id = "test_agent_456"

    def test_basic_init(self):
        """Test a basic client initialization."""
        client = CodeOcean(
            domain=self.test_domain,
            token=self.test_token,
        )

        # Verify base URL is set correctly
        self.assertEqual(client.session.base_url, f"{self.test_domain}/api/v1/")

        # Verify auth is correctly set
        self.assertEqual(client.session.auth, (self.test_token, ""))

        # Verify the session headers are correctly configured
        headers = client.session.headers
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], "application/json")
        self.assertIn("Min-Server-Version", headers)
        self.assertEqual(headers["Min-Server-Version"], MIN_SERVER_VERSION)

    @patch("codeocean.client.TCPKeepAliveAdapter")
    def test_retry_configuration_types(self, mock_adapter):
        """Test that both integer and Retry object work for retries parameter."""
        # Test with integer
        CodeOcean(
            domain=self.test_domain,
            token=self.test_token,
            retries=5,
        )

        # Test with Retry object
        retry_obj = Retry(total=3, backoff_factor=0.3)
        CodeOcean(
            domain=self.test_domain,
            token=self.test_token,
            retries=retry_obj,
        )

        # Assert both configurations work
        self.assertEqual(mock_adapter.call_count, 2)
        mock_adapter.assert_any_call(max_retries=5)
        mock_adapter.assert_any_call(max_retries=retry_obj)

    def test_agent_id_header_set_when_provided(self):
        """Test that Agent-Id header is set when agent_id is provided."""
        client = CodeOcean(
            domain=self.test_domain,
            token=self.test_token,
            agent_id=self.test_agent_id,
        )

        # Verify the session headers are correctly configured
        headers = client.session.headers
        self.assertIn("Agent-Id", headers)
        self.assertEqual(headers["Agent-Id"], self.test_agent_id)

    def test_agent_id_header_not_set_when_none(self):
        """Test that Agent-Id header is not set when agent_id is None."""
        client = CodeOcean(
            domain=self.test_domain,
            token=self.test_token,
            agent_id=None,
        )

        # Verify the session headers are correctly configured
        headers = client.session.headers
        self.assertNotIn("Agent-Id", headers)
