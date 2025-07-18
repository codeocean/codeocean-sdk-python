import unittest
from unittest.mock import Mock
import requests

from codeocean.error import Error


class TestError(unittest.TestCase):
    """Test cases for the Error exception class."""

    def test_error_is_exception_subclass(self):
        """Test that Error is a subclass of Exception."""
        self.assertTrue(issubclass(Error, Exception))

    def test_error_with_json_dict_message(self):
        """Test Error creation with JSON dict response containing message."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Custom error message"}

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response

        # Create Error instance
        error = Error(mock_http_error)

        # Verify attributes
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.message, "Custom error message")
        self.assertIsNone(error.items)

    def test_error_with_json_dict_no_message(self):
        """Test Error creation with JSON dict response without message field."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"error": "some other field"}

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response

        # Create Error instance
        error = Error(mock_http_error)

        # Verify attributes
        self.assertEqual(error.status_code, 500)
        self.assertEqual(error.message, "An error occurred.")
        self.assertIsNone(error.items)

    def test_error_with_json_list(self):
        """Test Error creation with JSON list response."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = [{"field": "error1"}, {"field": "error2"}]

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response

        # Create Error instance
        error = Error(mock_http_error)

        # Verify attributes
        self.assertEqual(error.status_code, 403)
        self.assertEqual(error.message, "An error occurred.")
        self.assertEqual(error.items, [{"field": "error1"}, {"field": "error2"}])

    def test_error_with_non_json_response(self):
        """Test Error creation when response is not JSON."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.text = "Page not found"

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response

        # Create Error instance
        error = Error(mock_http_error)

        # Verify attributes
        self.assertEqual(error.status_code, 404)
        self.assertEqual(error.message, "Page not found")
        self.assertIsNone(error.items)
