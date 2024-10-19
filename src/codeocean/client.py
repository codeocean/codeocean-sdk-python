from typing import Tuple

from requests_toolbelt.sessions import BaseUrlSession
from requests_toolbelt.adapters.socket_options import TCPKeepAliveAdapter
from requests.adapters import HTTPAdapter
from dataclasses import dataclass, field

from codeocean.capsule import Capsules
from codeocean.computation import Computations
from codeocean.data_asset import DataAssets


@dataclass
class CodeOcean:

    domain: str
    token: str
    _optional_adapters: Tuple[HTTPAdapter] = field(default=tuple(), repr=False)

    def __post_init__(self):
        self.session = BaseUrlSession(base_url=f"{self.domain}/api/v1/")
        self.session.auth = (self.token, "")
        self.session.mount(self.domain, TCPKeepAliveAdapter())

        for optional_adapter in self._optional_adapters:
            self.session.mount(self.domain, optional_adapter)
        self.session.headers.update({"Content-Type": "application/json"})
        self.session.hooks["response"] = [
            lambda response, *args, **kwargs: response.raise_for_status()
        ]

        self.capsules = Capsules(client=self.session)
        self.computations = Computations(client=self.session)
        self.data_assets = DataAssets(client=self.session)
