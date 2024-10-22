from dataclasses import dataclass
from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter
from requests_toolbelt.sessions import BaseUrlSession
from typing import Optional
from urllib3.util import Retry

from codeocean.capsule import Capsules
from codeocean.computation import Computations
from codeocean.data_asset import DataAssets


@dataclass
class CodeOcean:

    domain: str
    token: str
    retries: Optional[Retry | int] = 0

    def __post_init__(self):
        self.session = BaseUrlSession(base_url=f"{self.domain}/api/v1/")
        self.session.auth = (self.token, "")
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.hooks["response"] = [
            lambda response, *args, **kwargs: response.raise_for_status()
        ]
        self.session.mount(self.domain, TCPKeepAliveAdapter(max_retries=self.retries))

        self.capsules = Capsules(client=self.session)
        self.computations = Computations(client=self.session)
        self.data_assets = DataAssets(client=self.session)
