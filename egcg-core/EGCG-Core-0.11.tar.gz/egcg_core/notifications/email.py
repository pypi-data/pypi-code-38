import warnings
import jinja2
import smtplib
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.utils import COMMASPACE
from time import sleep
from os.path import basename

from egcg_core.app_logging import AppLogger
from egcg_core.exceptions import EGCGError
from .notification import Notification


class EmailSender(AppLogger):

    def __init__(self, subject, mailhost, port, sender, recipients, email_template=None):
        self.subject = subject
        self.mailhost = mailhost
        self.port = port
        self.sender = sender
        self.recipients = recipients
        self.email_template = email_template

    def send_email(self, **kwargs):
        email = self._build_email(**kwargs)
        success = self._try_send(email)
        if not success:
            err_msg = 'Failed to send message with following args: ' + str(kwargs)
            raise EGCGError(err_msg)

    def _try_send(self, msg, retries=3):
        """
        Attempt to send an email a set number of times.
        :param int retries: Which retry we're currently on
        :return: True if a message is sucessfully sent, otherwise False
        """
        try:
            self._connect_and_send(msg)
            return True
        except (smtplib.SMTPException, TimeoutError) as e:
            retries -= 1
            self.warning('Encountered a %s exception. %s retries remaining', str(e), retries)
            if retries:
                sleep(2)
                return self._try_send(msg, retries)

            return False

    def _build_email(self, **kwargs):
        """
        Create a MIMEText from plain text or Jinja2-formatted html and send by email. If attachments are provided, the
        message will be a MIMEMultipart containing the MimeText message plus MIMEApplication attachments.

        _build_email has two modes: plain text and html. The following keyword args are useable for both:
          - email_subject: (str) override the EmailSender subject
          - email_sender: (str) override the EmailSender sender
          - email_recipients: (list) override the EmailSender recipients
          - attachments: list of file paths to attach to the email

        In plain text mode:
          - text_message (str) is required and contains the plain text to send in the email
        In html mode:
          - email_template (str) can be user to override the EmailSender email_template
          - all other keyword args are passed to the Jinja template
        """
        email_template = kwargs.get('email_template', self.email_template)
        if email_template:
            content = jinja2.Template(open(email_template).read())
            text = MIMEText(content.render(**kwargs), 'html')
        elif 'text_message' in kwargs:
            text = MIMEText(kwargs.get('text_message'))
        else:
            raise EGCGError('EmailSender needs either a text_message or an email template')
        if 'attachments' in kwargs and kwargs['attachments']:
            if isinstance(kwargs['attachments'], str):
                kwargs['attachments'] = [kwargs['attachments']]
            msg = MIMEMultipart()
            msg.attach(text)
            for attachment in kwargs['attachments']:
                with open(attachment, 'rb') as f:
                    part = MIMEApplication(f.read(), Name=basename(attachment))
                    part['Content-Disposition'] = 'attachment; filename="%s"' % basename(attachment)
                    msg.attach(part)
        else:
            msg = text

        msg['Subject'] = kwargs.get('email_subject', self.subject)
        msg['From'] = kwargs.get('email_sender', self.sender)
        msg['To'] = COMMASPACE.join(kwargs.get('email_recipients', self.recipients))
        return msg

    def _connect_and_send(self, msg):
        connection = smtplib.SMTP(self.mailhost, self.port)
        connection.send_message(msg, self.sender, self.recipients)
        connection.quit()


class EmailNotification(Notification):
    translation_map = {' ': '&nbsp', '\n': '<br/>'}

    def __init__(self, name, mailhost, port, sender, recipients, strict=False, email_template=None):
        super().__init__(name)
        self.email_sender = EmailSender(name, mailhost, port, sender, recipients, email_template)
        self.strict = strict
        self.email_template = email_template

    def notify(self, msg, attachments=None):
        try:
            if self.email_template:
                self.email_sender.send_email(title=self.name, body=self._prepare_string(msg), attachments=attachments)
            else:
                self.email_sender.send_email(text_message=msg, attachments=attachments)
        except EGCGError:
            err_msg = 'Failed to send message: ' + str(msg)
            if self.strict:
                raise EGCGError(err_msg)
            else:
                self.critical(err_msg)

    @classmethod
    def _prepare_string(cls, msg):
        for k in cls.translation_map:
            msg = msg.replace(k, cls.translation_map[k])
        return msg


def send_email(msg, mailhost, port, sender, recipients, subject, email_template=None, attachments=None, **kwargs):
    warnings.warn('send_email is deprecated - use send_plain_text_email or send_html_email instead', DeprecationWarning)
    if msg and not email_template:
        send_plain_text_email(msg, mailhost, port, sender, recipients, subject, attachments)
    elif email_template and not msg:
        send_html_email(mailhost, port, sender, recipients, subject, email_template, attachments, **kwargs)
    else:
        send_html_email(mailhost, port, sender, recipients, subject, email_template, attachments, msg=msg, **kwargs)


def send_plain_text_email(msg, mailhost, port, sender, recipients, subject, attachments=None):
    EmailSender(
        subject,
        mailhost,
        port,
        sender,
        recipients,
    ).send_email(text_message=msg, attachments=attachments)


def send_html_email(mailhost, port, sender, recipients, subject, email_template, attachments=None, **kwargs):
    EmailSender(
        subject,
        mailhost,
        port,
        sender,
        recipients,
        email_template=email_template
    ).send_email(attachments=attachments, **kwargs)
