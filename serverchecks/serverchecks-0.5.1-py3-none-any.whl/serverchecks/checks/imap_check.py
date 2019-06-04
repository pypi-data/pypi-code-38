import imaplib
from typing import Union, Optional

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class ImapCheck(AbstractCheck):
    name = 'IMAP'

    def __init__(self, **kwargs) -> None:
        self.imap_server: str = kwargs.get('imap_server')
        self.tls_mode: str = kwargs.get('tls_mode')
        allowed = ('tls', 'starttls')
        if self.tls_mode not in allowed:
            raise ValueError(f'tls_mode must be one of {allowed}: {self.tls_mode}')

        self.username: Optional[str] = kwargs.get('username', None)
        self.password: Optional[str] = kwargs.get('password', None)
        self.imap: Optional[Union[imaplib.IMAP4_SSL, imaplib.IMAP4]] = None

    async def check(self) -> Outcome:
        if self.tls_mode == 'tls':
            self.imap: imaplib.IMAP4_SSL = imaplib.IMAP4_SSL(self.imap_server)
        else:
            self.imap: imaplib.IMAP4 = imaplib.IMAP4(self.imap_server)
            try:
                self.imap.starttls()
            except self.imap.error as e:
                return Outcome(False, f'IMAP STARTTLS failed {self.imap.host}:{self.imap.port}: {e}')

        if not len(self.imap.capabilities) > 0:
            return Outcome(False,
                           f'IMAP capabilities are empty on {self.imap.host}:{self.imap.port}: {self.imap.capabilities}')

        # skip any further tests in non-authenticated mode
        if not self.username:
            return Outcome(True, f'IMAP test successful on {self.imap.host}:{self.imap.port} (not authenticated)')

        try:
            self.imap.login(self.username, self.password)
        except self.imap.error as e:
            return Outcome(False, f'IMAP login failed on {self.imap.host}:{self.imap.port}: {e}')

        self.imap.select()

        status, messages = self.imap.search(None, 'ALL')
        if status != 'OK':
            return Outcome(False, f'Cannot search messages on {self.imap.host}:{self.imap.port}')

        self.imap.close()

        return Outcome(True, f'IMAP test successful on {self.imap.host}:{self.imap.port} (authenticated)')

    def __str__(self):
        return f'<{self.name} {self.imap_server}>'


check_class = ImapCheck
