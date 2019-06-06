from asyncio import create_subprocess_exec
from asyncio.subprocess import Process
from email.mime.text import MIMEText
from subprocess import PIPE  # nosec
from typing import List

from serverchecks.alerts import AbstractAlert


class SendmailAlert(AbstractAlert):
    """
    Send alert using locally installed /usr/sbin/sendmail program
    """
    name = 'SMTP'

    def __init__(self, **kwargs) -> None:
        self.from_email: str = kwargs.get('from_email')
        self.recipients: List[str] = kwargs.get('recipients')
        self.subject: str = kwargs.get('subject')
        self.sendmail: str = kwargs.get('sendmail', '/usr/sbin/sendmail')

    async def alert(self, message: str) -> None:
        msg = MIMEText(message)
        msg["From"] = self.from_email
        msg["Bcc"] = ';'.join(self.recipients)
        msg["Subject"] = self.subject
        self.process: Process = await create_subprocess_exec(self.sendmail, "-t", stdin=PIPE, universal_newlines=True)
        await self.process.communicate(input=msg.as_string())

    async def close(self) -> None:
        self.process.terminate()

    def __str__(self):
        return f'<{self.name} {self.from_email}>'


alert_class = SendmailAlert
