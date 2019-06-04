import socket
import ssl
from datetime import datetime, timedelta
from typing import Optional, Dict

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class TlsCheck(AbstractCheck):
    name = 'TLS'

    def __init__(self, **kwargs) -> None:
        self.host: str = kwargs.get('host')
        self.port: int = kwargs.get('port', 443)
        self.cert_days: int = kwargs.get('cert_days', 5)
        self.timeout: float = kwargs.get('timeout', 2.0)

    def _date(self, d: str) -> Optional[datetime]:
        try:
            # try decoding locale representation first
            return datetime.strptime(d, '%c')
        except ValueError:
            try:
                # try 'Jan 30 23:00:15 2019 GMT' representation
                return datetime.strptime(d, '%b %d %H:%M:%S %Y %Z')
            except ValueError:
                return None

    async def check(self) -> Outcome:
        context: ssl.SSLContext = ssl.create_default_context()

        try:
            with socket.create_connection((self.host, self.port), self.timeout) as sock:
                with context.wrap_socket(sock, server_hostname=self.host) as ssl_sock:
                    cert: Dict = ssl_sock.getpeercert()
        except ssl.SSLError as e:
            return Outcome(False, f'TLS error for {self.host}: {e}')
        else:
            not_before: datetime = self._date(cert.get('notBefore'))
            not_after: datetime = self._date(cert.get('notAfter'))

            now: datetime = datetime.now()

            if not not_before or not not_after:
                return Outcome(False, f'Unable to determine notBefore or notAfter dates in {cert}')

            if now < not_before:
                return Outcome(False, f'TLS certificate for {self.host} not valid as {now} is before {not_before}')

            target_date: datetime = now + timedelta(days=self.cert_days)
            if target_date > not_after:
                return Outcome(False,
                               f'TLS certificate for {self.host} not valid as {target_date} is after {not_after}')

            return Outcome(True, f'Certificate for {self.host} valid until {not_after}')

    def __str__(self):
        return f'<{self.name} {self.host}>'


check_class = TlsCheck
