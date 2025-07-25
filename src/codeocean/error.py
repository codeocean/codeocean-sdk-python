from __future__ import annotations

import json
import requests


class Error(Exception):
    """
    Represents an HTTP error with additional context extracted from the response.

    Attributes:
        status_code (int): The HTTP status code of the error response.
        message (str): A message describing the error, extracted from the response body.
        items (list or None): If the response body is a list, this attribute contains the list; otherwise, it is None.

    Args:
        err (requests.HTTPError): The HTTP error object from which to extract details.
    """
    def __init__(self, err: requests.HTTPError):
        self.status_code = err.response.status_code
        self.message = "An error occurred."
        self.items = None
        self.url = err.response.url

        try:
            body = err.response.json()
            if isinstance(body, dict):
                self.message = body.get("message", self.message)
                for key, value in body.items():
                    if key not in ("message", "code"):
                        self.items = {key: value}
                        break
            elif isinstance(body, list):
                self.items = body
        except Exception:
            # response wasn't JSON – fall back to text
            self.message = err.response.text

        super().__init__(self.message)

    def __str__(self):
        base = f"{self.status_code} Error for URL {self.url}:\n{self.message}"
        if self.items:
            extra = "\n\nAdditional context:\n" + json.dumps(self.items, indent=2)
            return base + extra
        return base
