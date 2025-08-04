from __future__ import annotations

import json
import requests


class Error(Exception):
    """
    Represents an HTTP error with additional context extracted from the response.

    Attributes:
        http_err (requests.HTTPError): The HTTP error object.
        status_code (int): The HTTP status code of the error response.
        message (str): A message describing the error, extracted from the response body.
        data (Any): If the response body is json, this attribute contains the json object; otherwise, it is None.

    Args:
        err (requests.HTTPError): The HTTP error object.
    """
    def __init__(self, err: requests.HTTPError):
        self.http_err = err
        self.status_code = err.response.status_code
        self.message = "An error occurred."
        self.data = None

        try:
            self.data = err.response.json()
            if isinstance(self.data, dict):
                self.message = self.data.get("message", self.message)
        except Exception:
            # response wasn't JSON – fall back to text
            self.message = err.response.text

        super().__init__(self.message)

    def __str__(self) -> str:
        msg = str(self.http_err)
        msg += f"\n\nMessage: {self.message}"
        if self.data:
            msg += "\n\nData:\n" + json.dumps(self.data, indent=2)
        return msg
