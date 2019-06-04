import socket
from urllib.error import URLError
from urllib.request import urlopen

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class UrlCheck(AbstractCheck):
    name = 'URL'

    def __init__(self, **kwargs) -> None:
        self.url: str = kwargs.get('url')
        self.expect_code: int = kwargs.get('expect_code', 200)
        self.timeout: float = kwargs.get('timeout', 2.0)

    async def check(self) -> Outcome:
        try:
            ret = urlopen(self.url, timeout=self.timeout)
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
