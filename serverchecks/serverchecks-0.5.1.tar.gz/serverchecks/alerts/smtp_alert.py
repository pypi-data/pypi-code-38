import smtplib
import socket
from email.message import EmailMessage

from serverchecks.alerts import AbstractAlert


class SmtpAlert(AbstractAlert):
    """
    Send alert in an email message over SMTP
    """
    name = 'SMTP'

    def __init__(self, **kwargs) -> None:
        self.from_email: str = kwargs.get('from_email')
        self.to_email: str = kwargs.get('to_email')
        self.subject: str = kwargs.get('subject')
        self.smtp_server: str = kwargs.get('smtp_server', 'localhost')
        self.smtp_port: int = kwargs.get('smtp_port', 587)

        # optional SMTP authentication parameters
        self.username: str = kwargs.get('username', None)
        self.password: str = kwargs.get('password', None)

    async def open(self) -> None:
        # open SMTP server connection
        self.smtp: smtplib.SMTP = smtplib.SMTP(self.smtp_server, timeout=5.0, port=self.smtp_port)
        self.smtp.ehlo(socket.getfqdn())
        self.smtp.starttls()
        if self.username:
            self.smtp.login(self.username, self.password)

    async def test(self) -> bool:
        self.smtp.noop()

    async def alert(self, message: str) -> None:
        msg = EmailMessage()
        msg.set_content(message)
        msg["From"] = self.from_email
        msg["To"] = self.to_email
        msg["Subject"] = self.subject
        self.smtp.send_message(msg, self.from_email, self.to_email)

    async def close(self) -> None:
        self.smtp.quit()

    def __str__(self):
        return f'<{self.name} {self.from_email}>'


alert_class = SmtpAlert
