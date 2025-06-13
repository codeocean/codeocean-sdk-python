from __future__ import annotations

from dataclasses import dataclass
from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional, Union
from urllib3.util import Retry
import requests

from codeocean.capsule import Capsules
from codeocean.computation import Computations
from codeocean.data_asset import DataAssets
from codeocean.errors import (
    BadRequestError,
    UnauthorizedError,
    ForbiddenError,
    NotFoundError,
    InternalServerError,
    CodeOceanError
)


@dataclass
class CodeOcean:
    """
    Code Ocean API client.

    This class provides a unified interface to access Code Ocean's API endpoints
    for managing capsules, pipelines, computations, and data assets.

    Fields:
        domain: The Code Ocean domain URL (e.g., 'https://codeocean.acme.com')
        token: Code Ocean API access token
        retries: Optional retry configuration for failed HTTP requests. Can be an integer
                (number of retries) or a urllib3.util.Retry object for advanced
                retry configuration. Defaults to 0 (no retries)
        agent_id: Optional agent identifier for tracking AI agent API usage on behalf of users
    """

    domain: str
    token: str
    retries: Optional[Retry | int] = 0
    agent_id: Optional[str] = None

    # Minimum server version required by this SDK
    MIN_SERVER_VERSION = "3.6.0"

    def __post_init__(self):
        self.session = BaseUrlSession(base_url=f"{self.domain}/api/v1/")
        self.session.auth = (self.token, "")
        self.session.headers.update({
            "Content-Type": "application/json",
            "Min-Server-Version": CodeOcean.MIN_SERVER_VERSION,
        })
        if self.agent_id:
            self.session.headers.update({"Agent-Id": self.agent_id})
        self.session.hooks["response"] = [self.error_handler]
        self.session.mount(self.domain, TCPKeepAliveAdapter(max_retries=self.retries))

        self.capsules = Capsules(client=self.session)
        self.computations = Computations(client=self.session)
        self.data_assets = DataAssets(client=self.session)

    def error_handler(self, response, *args, **kwargs):
        try:
            response.raise_for_status()
        except requests.HTTPError as ex:
            try:
                error_payload = response.json()
                if not isinstance(error_payload, dict):
                    raise ValueError("Response is not a JSON object")
            except ValueError:
                error_payload = {"message": response.text or str(ex)}

            status_code = response.status_code
            if status_code == 400:
                raise BadRequestError.from_dict(error_payload).with_error(ex)
            elif status_code == 401:
                raise UnauthorizedError.from_dict(error_payload).with_error(ex)
            elif status_code == 403:
                raise ForbiddenError.from_dict(error_payload).with_error(ex)
            elif status_code == 404:
                raise NotFoundError.from_dict(error_payload).with_error(ex)
            elif status_code >= 500:
                raise InternalServerError.from_dict(error_payload).with_error(ex)
            else:
                raise CodeOceanError.from_dict(error_payload).with_error(ex)
