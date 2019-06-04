import smtplib
import socket
from email.message import EmailMessage

from serverchecks import Outcome
from serverchecks.checks import AbstractCheck


class SmtpCheck(AbstractCheck):
    name = 'SMTP'

    def __init__(self, **kwargs) -> None:
        self.smtp_server: str = kwargs.get('smtp_server')
        self.smtp_port: int = kwargs.get('smtp_port', 25)
        self.username: str = kwargs.get('username', None)
        self.password: str = kwargs.get('password', None)

    async def check(self) -> Outcome:
        try:
            smtp = smtplib.SMTP(self.smtp_server, timeout=2.0, port=self.smtp_port)
        except socket.timeout as e:
            return Outcome(False, f'SMTP {self.smtp_server}:{self.smtp_port} timed out: {e}')

        # STARTTLS usually requires EHLO
        smtp.ehlo(socket.getfqdn())

        try:
            smtp.starttls()
        except smtplib.SMTPNotSupportedError as e:
            return Outcome(False, f'SMTP STARTTLS failed on {self.smtp_server}:{self.smtp_port}: {e}')

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
                return Outcome(False, f'SMTP send failed on {self.smtp_server}:{self.smtp_port}: {e}')

            auth = 'authenticated'

        smtp.quit()

        return Outcome(True, f'SMTP successful on {self.smtp_server}:{self.smtp_port} ({auth})')

    def __str__(self):
        return f'<{self.name} {self.smtp_server}>'


check_class = SmtpCheck
