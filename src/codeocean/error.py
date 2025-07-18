from __future__ import annotations

import requests


class Error(Exception):

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
