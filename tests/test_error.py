import unittest
from unittest.mock import Mock
import requests

from codeocean.error import Error


class TestError(unittest.TestCase):
    """Test cases for the Error exception class."""

    def test_error_is_exception_subclass(self):
        """Test that Error is a subclass of Exception."""
        self.assertTrue(issubclass(Error, Exception))

    def test_error_with_json_dict(self):
        """Test Error creation with JSON dict response containing message."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Custom error message", "datasets": [{"id": "123", "name": "tv"}]}

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response

        # Create Error instance
        error = Error(mock_http_error)

        # Verify attributes
        self.assertEqual(error.status_code, 400)
        self.assertEqual(error.message, "Custom error message")
        self.assertEqual(error.data, {"message": "Custom error message", "datasets": [{"id": "123", "name": "tv"}]})

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
        self.assertEqual(error.data, {"error": "some other field"})

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
        self.assertEqual(error.data, [{"field": "error1"}, {"field": "error2"}])

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
        self.assertIsNone(error.data)

    def test_error_str_method_with_data(self):
        """Test Error __str__ method when data is present."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"message": "Validation failed", "errors": ["field1", "field2"]}

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response
        mock_http_error.__str__ = Mock(return_value="400 Client Error: Bad Request for url: http://example.com")

        # Create Error instance
        error = Error(mock_http_error)

        # Test __str__ method
        error_str = str(error)

        # Verify the string contains expected components
        self.assertEqual(error_str, """400 Client Error: Bad Request for url: http://example.com

Message: Validation failed

Data:
{
  "message": "Validation failed",
  "errors": [
    "field1",
    "field2"
  ]
}""")

    def test_error_str_method_without_data(self):
        """Test Error __str__ method when data is None."""
        # Create mock HTTPError and response
        mock_response = Mock()
        mock_response.status_code = 404
        mock_response.json.side_effect = Exception("Not JSON")
        mock_response.text = "Page not found"

        mock_http_error = Mock(spec=requests.HTTPError)
        mock_http_error.response = mock_response
        mock_http_error.__str__ = Mock(return_value="404 Client Error: Not Found for url: http://example.com")

        # Create Error instance
        error = Error(mock_http_error)

        # Test __str__ method
        error_str = str(error)

        # Verify the string contains expected components
        self.assertEqual(error_str, """404 Client Error: Not Found for url: http://example.com

Message: Page not found""")
