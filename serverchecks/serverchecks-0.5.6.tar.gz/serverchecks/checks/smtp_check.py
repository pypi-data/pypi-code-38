import smtplib
import socket
from email.message import EmailMessage
from typing import Optional

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class SmtpCheck(AbstractCheck):
    name = 'SMTP'

    def __init__(self, **kwargs) -> None:
        self.host: str = kwargs.get('host')
        self.port: int = kwargs.get('port', 25)
        self.username: Optional[str] = kwargs.get('username', None)
        self.password: Optional[str] = kwargs.get('password', None)

        if self.host is None:
            raise ValueError(f'{self.name} required `host` parameter is missing')

    async def check(self) -> Outcome:
        try:
            smtp = smtplib.SMTP(self.host, timeout=2.0, port=self.port)
        except (socket.timeout, ConnectionError) as e:
            return Outcome(False, f'SMTP {self.host}:{self.port} timed out: {e}')

        # STARTTLS usually requires EHLO
        smtp.ehlo(socket.getfqdn())

        try:
            smtp.starttls()
        except smtplib.SMTPNotSupportedError as e:
            return Outcome(False, f'SMTP STARTTLS failed on {self.host}:{self.port}: {e}')

        auth = 'not authenticated'

        if self.username:
            msg = EmailMessage()
            msg.set_content('test')
            msg['From'] = self.username
            msg['To'] = self.username
            msg['Subject'] = 'test'

            smtp.login(self.username, self.password)

            try:
                smtp.send_message(msg, self.username, self.username)
            except smtplib.SMTPException as e:
                return Outcome(False, f'SMTP send failed on {self.host}:{self.port}: {e}')

            auth = 'authenticated'

        smtp.quit()

        return Outcome(True, f'SMTP successful on {self.host}:{self.port} ({auth})')

    def __str__(self):
        return f'<{self.name} {self.host}>'


check_class = SmtpCheck
