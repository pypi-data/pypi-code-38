import socket
from urllib.error import URLError
from urllib.parse import urlparse, ParseResult
from urllib.request import urlopen

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class UrlCheck(AbstractCheck):
    name = 'URL'

    def __init__(self, **kwargs) -> None:
        self.url: str = kwargs.get('url')
        self.url_parsed: ParseResult = urlparse(self.url)
        self.expect_code: int = kwargs.get('expect_code', 200)
        self.timeout: float = kwargs.get('timeout', 2.0)

        if self.url is None:
            raise ValueError(f'{self.name} required `url` parameter is missing')
        allowed = ('http', 'https')
        if self.url_parsed.scheme not in allowed:
            raise ValueError(f'{self.name} only {allowed} schemes are supported: {self.url_parsed.scheme}')

    async def check(self) -> Outcome:
        try:
            ret = urlopen(self.url, timeout=self.timeout)  # nosec
        except (URLError, socket.timeout) as e:
            return Outcome(False, f'URL {self.url} failed: {e}')
        else:
            ret_code: int = ret.getcode()
            if ret_code == self.expect_code:
                return Outcome(True, f'URL {self.url} returned code {ret_code}')
            else:
                return Outcome(False, f'URL {self.url} returned code {ret_code} vs expected {self.expect_code}')

    def __str__(self):
        return f'<{self.name} {self.url:.20}>'


check_class = UrlCheck
