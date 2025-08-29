from __future__ import annotations

from dataclasses import dataclass
from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional
from urllib3.util import Retry
import requests

from codeocean.capsule import Capsules
from codeocean.computation import Computations
from codeocean.custom_metadata import CustomMetadataSchema
from codeocean.data_asset import DataAssets
from codeocean.error import Error


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
        self.session.hooks["response"] = [self._error_handler]
        self.session.mount(self.domain, TCPKeepAliveAdapter(max_retries=self.retries))

        self.capsules = Capsules(client=self.session)
        self.computations = Computations(client=self.session)
        self.custom_metadata = CustomMetadataSchema(client=self.session)
        self.data_assets = DataAssets(client=self.session)

    def _error_handler(self, response, *args, **kwargs):
        try:
            response.raise_for_status()
        except requests.HTTPError as err:
            raise Error(err) from err
