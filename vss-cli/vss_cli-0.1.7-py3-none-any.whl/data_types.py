from dataclasses import dataclass, field
import re
from typing import List, Optional, Union

from dataclasses_json import dataclass_json
from validators import url as is_url
import vss_cli.const as const
from vss_cli.exceptions import ValidationError


class Url(str):
    def __new__(cls, val):
        if is_url(val):
            return str.__new__(cls, val)
        else:
            raise ValidationError(f'{val} is not a valid URL')


@dataclass_json
@dataclass
class ConfigFileGeneral:
    check_for_updates: bool = const.DEFAULT_CHECK_UPDATES
    check_for_messages: bool = const.DEFAULT_CHECK_MESSAGES
    default_endpoint_name: str = const.DEFAULT_ENDPOINT_NAME
    debug: bool = False
    output: str = const.DEFAULT_RAW_OUTPUT
    table_format: str = 'simple'
    timeout: int = const.DEFAULT_TIMEOUT
    verbose: bool = False


@dataclass_json
@dataclass
class ConfigEndpoint:
    url: Url
    name: Optional[str] = None
    auth: Optional[str] = None
    token: Optional[str] = None

    def __post_init__(self):
        def get_hostname_from_url(
                url: str,
                hostname_regex: str = const.DEFAULT_HOST_REGEX
        ) -> str:
            """Parse hostname from URL"""
            re_search = re.search(hostname_regex, url)
            _, _hostname = re_search.groups() if re_search else ('', '')
            _host = _hostname.split('.')[0] if _hostname.split('.') else ''
            return _host
        if not self.name:
            self.name = get_hostname_from_url(self.url)


@dataclass_json
@dataclass
class ConfigFile:
    general: ConfigFileGeneral
    endpoints: Optional[Union[List[ConfigEndpoint]]] = field(
        default_factory=lambda: []
    )

    def get_endpoint(
            self, ep_name_or_url: str
    ) -> List[ConfigEndpoint]:
        if self.endpoints:
            ep = list(
                filter(lambda i: ep_name_or_url == i.name, self.endpoints)
            ) or list(
                filter(lambda i: ep_name_or_url == i.url, self.endpoints)
            )
            return ep
        else:
            return []

    def update_endpoint(
            self, endpoint: ConfigEndpoint
    ) -> List[ConfigEndpoint]:
        if self.endpoints:
            for idx, val in enumerate(self.endpoints):
                if val.name == endpoint.name:
                    self.endpoints[idx] = endpoint
                    return self.endpoints
        else:
            self.endpoints = []
        # adding
        self.endpoints.append(endpoint)
        return self.endpoints

    def update_endpoints(self, *endpoints: List[ConfigEndpoint]
                         ) -> List[ConfigEndpoint]:
        for endpoint in endpoints:
            self.update_endpoint(endpoint)
        return self.endpoints
