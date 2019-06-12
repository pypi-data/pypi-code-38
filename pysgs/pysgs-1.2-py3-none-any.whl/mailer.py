"""
Process the email configuration
"""
import os
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from pysgs.server import Server
from pysgs.exceptions import SGSError


class Mailer(Server):
    """
    Mailer class to process messages
    """

    def __init__(self, api_key, smtp_port=None):
        """
        Keyword Arguments:
            api_key {str} -- SendGrid Api Key
            smtp_port {str} -- Sendgrid support different smtp ports (optional)
        """

        self.api_key = api_key
        self.api_user = 'apikey'
        self.smtp_port = smtp_port
        self.smtp_host = 'smtp.sendgrid.net'


    def headers(self, sender, recipients, subject):
        """Setting mail configuration

        Keyword Arguments:
            sender {str} -- Email who sends the message (default: {''})
            recipients {str} or {list} -- Recipient Emails (default: {None})
            subject {str} -- Subject of the message (default: {''})

        Raises:
            Exception -- Recipients information has not a valid type
        """

        self.__initialize()

        self._session_message['From'] = sender
        self._session_message['Subject'] = subject

        if isinstance(recipients, list):
            self._session_message['To'] = ", ".join(recipients)
        elif isinstance(recipients, str):
            self._session_message['To'] = recipients
        else:
            raise SGSError('Recipients information has not a valid value.')


    def content(self, content, content_type="plain", is_attach=False):
        """[summary]

        Keyword Arguments:
            content {str} -- Plain text, HTML content or File path
            content_type {str} -- plain or html (default: {plain})
        """

        if is_attach:
            self.__add_attachment(content)

        else:
            self.__add_content(content, content_type)


    def __initialize(self):
        self._session_message = MIMEMultipart()


    def __add_attachment(self, path_attach=""):
        """Add an attachment to the message

        Keyword Arguments:
            path_attach {str} -- File path (default: {''})

        Raises:
            Exception -- Path is not a valid file type
        """

        if not os.path.isfile(path_attach):
            raise SGSError('Path is not a valid file type.')


        def guess_mime(path_attach):
            """
            Guess file mimetype
            """
            ctype, encoding = mimetypes.guess_type(path_attach)
            if ctype is None or encoding is not None:
                ctype = 'application/octet-stream'

            main_type, sub_type = ctype.split('/', 1)
            return main_type, sub_type

        def open_attach(path_attach):
            """
            Open and read file
            """
            with open(path_attach, 'rb') as file_name:
                return file_name.read()
            return ""

        def get_filename(path_attach):
            file_path = open(path_attach)
            return os.path.basename(file_path.name)

        # Guess Mime
        main_type, sub_type = guess_mime(path_attach)
        if main_type == 'text':
            content = ""
            with open(path_attach) as file_name:
                content = file_name.read()

            attach = MIMEText(content, _subtype=sub_type)
        else:
            # Object
            content = open_attach(path_attach)
            if main_type == 'image':
                attach = MIMEImage(content, _subtype=sub_type)
            elif main_type == 'audio':
                attach = MIMEAudio(content, _subtype=sub_type)
            else:
                attach = MIMEBase(main_type, sub_type)
                attach.set_payload(content)

        # Set the filename parameter
        attach.add_header(
            'Content-Disposition',
            'attachment',
            filename=get_filename(path_attach)
        )

        self._session_message.attach(attach)


    def __add_content(self, text="", content_type="plain"):
        """[summary]

        Keyword Arguments:
            text {str} -- Plain text or HTML content (default: {""})
            content_type {str} -- html or plain (default: {plain})
        """

        self._session_message.attach(MIMEText(text, content_type))
