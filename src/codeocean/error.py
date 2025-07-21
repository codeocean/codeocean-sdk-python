from __future__ import annotations

import requests


class Error(Exception):
    """
    Represents an HTTP error with additional context extracted from the response.

    Attributes:
        status_code (int): The HTTP status code of the error response.
        message (str): A message describing the error, extracted from the response body or defaulting to a generic message.
        items (list or None): If the response body is a list, this attribute contains the list; otherwise, it is None.

    Args:
        err (requests.HTTPError): The HTTP error object from which to extract details.
    """
    def __init__(self, err: requests.HTTPError):
        self.status_code = err.response.status_code
        self.message = "An error occurred."
        self.items = None

        try:
            body = err.response.json()
            if isinstance(body, dict):
                self.message = body.get("message", self.message)
            elif isinstance(body, list):
                self.items = body
        except Exception:
            # response wasn't JSON – fall back to text
            self.message = err.response.text
