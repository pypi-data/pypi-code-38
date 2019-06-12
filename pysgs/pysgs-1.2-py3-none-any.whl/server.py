"""
Use smtplib to send message through SendGrid
"""
import smtplib
from smtplib import SMTPServerDisconnected
from pysgs.exceptions import SGSError


class Server:
    """
    Server class to send messages
    """
    service = None

    def __init__(self):
        pass


    @property
    def api_key(self):
        return self._api_key


    @api_key.setter
    def api_key(self, value):
        self._api_key = value if value is not None else ""


    @property
    def api_user(self):
        return self._api_user


    @api_user.setter
    def api_user(self, value):
        self._api_user = value


    @property
    def smtp_host(self):
        return self._smtp_host


    @smtp_host.setter
    def smtp_host(self, value):
        self._smtp_host = value


    @property
    def smtp_port(self):
        return self._smtp_port


    @smtp_port.setter
    def smtp_port(self, value):
        port = value if value is not None else '25'
        self._smtp_port = port


    def send(self):
        """
        Send message with smtplib
        """

        if not self._session_message:
            raise SGSError('Message could not been send.')

        # Validate initialized service
        if self.service is None:
            self.__setup_smtp()

        return self.sender()


    def close(self):
        """
        Quit SMTP Server
        """
        self.service.quit()


    def sender(self):
        """
        Send message with smtplib
        """

        if not self._session_message:
            raise SGSError('Message could not been send.')

        return self.service.sendmail(
            self._session_message['From'],
            self._session_message['To'],
            self._session_message.as_string()
        )


    def __setup_smtp(self):
        """
        Initialize SMTP Server
        """
        try:
            smtp_data = f"{self.smtp_host}: {self.smtp_port}"

            self.service = smtplib.SMTP(smtp_data)
            self.service.starttls()

            self.service.login(self.api_user, self.api_key)
        except SMTPServerDisconnected as disconnected:
            raise SGSError(str(disconnected))
