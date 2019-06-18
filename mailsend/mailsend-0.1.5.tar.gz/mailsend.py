from __future__ import unicode_literals, absolute_import

from contextlib import contextmanager
from collections import namedtuple
from email.encoders import encode_base64
from email.message import Message as stdlib_Message
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.nonmultipart import MIMENonMultipart
from email.charset import Charset, QP
from email.utils import formatdate
from email.utils import make_msgid
import logging
import smtplib
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import envparse

__version__ = '0.1.5'

logger = logging.getLogger(__name__)

# Sniff SMTPUTF8 support through existance of SMTPNotSupportedError (py35+)
try:
    SMTPNotSupportedError = smtplib.SMTPNotSupportedError
    SMTPUTF8 = 'SMTPUTF8'
except AttributeError:
    SMTPUTF8 = None

env = envparse.Env(
    MAILSEND_SERVER={'cast': str, 'default': 'localhost'},
    MAILSEND_PORT={'cast': int, 'default': 25},
    MAILSEND_USERNAME=str,
    MAILSEND_PASSWORD=str,
    MAILSEND_SSL={'cast': bool, 'default': False},
    MAILSEND_TLS={'cast': bool, 'default': False},
    MAILSEND_DEBUG={'cast': bool, 'default': False},
)

Attachment = namedtuple('Attachment', ['filename', 'content_type', 'data',
                                       'disposition', 'headers'])


class BadHeaderError(ValueError):
    """
    Invalid value in a message header
    """


class MailSessionBase(object):

    def __init__(self, connection):
        self.rewrite_to = connection.rewrite_to
        self.bcc = connection.bcc
        self.outbox = connection.outbox
        self.log_messages = connection.log_messages

    def rewrite_envelope(self, envelope_from, envelope_to):
        if self.rewrite_to:
            envelope_to = self.rewrite_to

        if self.bcc:
            envelope_to = set(envelope_to) | set(self.bcc)

        return envelope_from, envelope_to

    def send(self, *args, **kwargs):

        mail_options = list(kwargs.pop('mail_options', []))

        if len(args) == 1 and isinstance(args[0], stdlib_Message) and not kwargs:
            msg, = args
            envelope_from = (msg.get_unixfrom() or msg['From'])
            envelope_to = [s.strip() for s in msg['To'].split(',')]

        else:
            if len(args) == 1 and isinstance(args[0], Message) and not kwargs:
                msg, = args
            else:
                msg = Message(*args, **kwargs)

            envelope_from = msg.sender
            envelope_to = msg.send_to

            if msg.has_utf8_addresses():
                if SMTPUTF8:
                    mail_options.append(SMTPUTF8)

        envelope_from, envelope_to = self.rewrite_envelope(
            envelope_from, envelope_to)

        self.outbox.append(msg)
        if self.log_messages:
            logger.info("MAIL FROM %r TO %r:\n\n%s",
                        envelope_from,
                        envelope_to,
                        msg.as_string())
        self._send(envelope_from, envelope_to, msg.as_string(), mail_options)

    def _send(self, envelope_from, envelope_to, message, mail_options):
        raise NotImplementedError()

    def close(self):
        pass


class MailSession(MailSessionBase):

    def __init__(self, connection):
        super(MailSession, self).__init__(connection)

        SMTP = smtplib.SMTP_SSL if connection.ssl else smtplib.SMTP
        self._smtp = SMTP(connection.hostname, connection.port)
        self._smtp.set_debuglevel(connection.debug)
        if connection.tls:
            self._smtp.starttls()
        if connection.username:
            self._smtp.login(connection.username, connection.password)

    def _send(self, envelope_from, envelope_to, message, mail_options):
        mail_options = list(mail_options or [])
        self._smtp.sendmail(envelope_from,
                            envelope_to,
                            message,
                            mail_options=mail_options)

    def close(self):
        self._smtp.close()


class NoMailSession(MailSessionBase):

    def _send(self, envelope_from, envelope_to, message, mail_options):
        pass


class Outbox(list):
    """
    Store emails sent by a :class:`Mail` object in a list for
    later inspection (eg by a test function)
    """


class NullOutbox(Outbox):
    """
    Outbox that drops all emails
    """
    def append(self, thing):
        pass


class Mail(object):

    def __init__(self, hostname=None, port=None, username=None, password=None,
                 ssl=False, tls=False, debug=False, rewrite_to=None,
                 bcc=None, suppress_send=False, log_messages=False):
        """
        :param hostname: hostname of the mail server, OR a URL of the form
                         ``smtps+tls://scott:tiger@mail.example.org:25``
        :param port: port number of the mail server. Default is 25 unless SSL
                     is specified
        :param username: mail server login user
        :param password: mail server login password
        :param ssl: If True, use SSL (changes the default port to 465)
        :param tls: If True, use TLS
        :param debug: If True, turns on smtplib connection debugging
        :param rewrite_to: List of email address to rewrite all mails to
                           Useful in dev environments to avoid accidentally
                           emailing real users.
        :param bcc: List of email addresses to BCC on every message sent.
        :param suppress_send: If true, messages will not be sent, but will be
                              collected in an outbox variable
        :param log_messages: If true, the text of messages will be logged
        """

        url = hostname or env('MAILSEND_URL', default='')
        if url and '://' in url:
            url = urlparse(url)
            scheme = url.scheme or 'smtp'
            assert scheme in ('smtp', 'smtps', 'smtp+tls')
            ssl = scheme == 'smtps'
            tls = scheme == 'smtp+tls'
            hostname = url.hostname or None
            port = url.port or (465 if ssl else 25)
            username = url.username
            password = url.password

        self.hostname = hostname or env('MAILSEND_SERVER')
        self.port = port or env('MAILSEND_PORT', default=25)
        self.username = username or env('MAILSEND_USERNAME', default=None)
        self.password = password or env('MAILSEND_PASSWORD', default=None)
        self.ssl = ssl or env('MAILSEND_SSL', default=False)
        self.tls = tls or env('MAILSEND_TLS', default=False)
        self.debug = debug or env('MAILSEND_DEBUG', default=False)
        self.rewrite_to = rewrite_to or \
                env('MAILSEND_REWRITE_TO', default=None)
        self.bcc = bcc or env('MAILSEND_BCC', default=None)
        self.suppress_send = suppress_send or \
                env('MAILSEND_SUPPRESS_SEND', default=False)
        if self.suppress_send:
            self.mailsession_cls = NoMailSession
        else:
            self.mailsession_cls = MailSession
        self.log_messages = log_messages
        self.outbox = NullOutbox()

    @contextmanager
    def connect(self):
        yield self.mailsession_cls(self)

    def send(self, *args, **kwargs):
        """
        Send a single message
        """
        with self.connect() as c:
            c.send(*args, **kwargs)

    @contextmanager
    def subscribe(self, supress_send=True):
        """
        Return a fresh :class:`mailsend.Outbox` list. Any mails sent while
        the ``subscribe`` context manager is in place will not be relayed,
        but instead collected in this outbox.
        """
        saved = self.outbox, self.mailsession_cls
        self.outbox = Outbox()
        if supress_send:
            self.mailsession_cls = NoMailSession
        yield self.outbox
        self.outbox, self.mailsession_cls = saved


class Message(object):

    """
    Encapsulates an email message.

    :param subject: email subject header
    :param recipients: list of email addresses
    :param body: plain text message
    :param html: HTML message
    :param sender: email sender address, or **DEFAULT_MAIL_SENDER** by default
    :param cc: CC list
    :param bcc: BCC list
    :param attachments: list of Attachment instances
    :param reply_to: reply-to address
    :param date: send date
    :param charset: message character set
    :param extra_headers: A dictionary of additional headers for the message

    Source: Flask-Mail by Dan Jacob
    """
    def __init__(self, sender, subject,
                 recipients=None,
                 body=None,
                 html=None,
                 cc=None,
                 bcc=None,
                 attachments=None,
                 reply_to=None,
                 date=None,
                 charset=None,
                 extra_headers=None):

        self.subject = subject
        self.sender = sender
        self.body = body
        self.html = html
        self.date = date
        self.charset = charset
        self.extra_headers = extra_headers

        self.cc = cc
        self.bcc = bcc
        self.reply_to = reply_to

        if recipients is None:
            recipients = []

        self.recipients = list(recipients)

        if attachments is None:
            attachments = []

        self.attachments = attachments

    @property
    def send_to(self):
        return set(self.recipients) | set(self.bcc or ()) | set(self.cc or ())

    def _mimetext(self, text, subtype='plain'):
        """
        Creates a MIMEText object with the given subtype (default: 'plain')
        If the text is unicode, the utf-8 charset is used.
        """
        charset = self.charset or 'utf-8'
        part = MIMENonMultipart('text', subtype, charset=charset)
        cs = Charset(charset)
        cs.body_encoding = QP
        part.set_payload(text, charset=cs)
        return part

    def as_message(self):
        """
        Return the message as a :class:`email.message.Message` object.
        """
        has_html = self.html is not None
        has_attachments = len(self.attachments) > 0

        if not has_html and not has_attachments:
            # No html content and zero attachments means plain text
            msg = self._mimetext(self.body)

        elif has_attachments and not has_html:
            # No html and at least one attachment means multipart
            msg = MIMEMultipart()
            msg.attach(self._mimetext(self.body))

        elif has_html and not has_attachments:
            # html and no attachments means multipart/alternative
            # (a regular multipart/mixed payload results in outlook 2011
            # refusing to show the body)
            msg = MIMEMultipart('alternative')
            msg.attach(self._mimetext(self.body, 'plain'))
            msg.attach(self._mimetext(self.html, 'html'))

        else:
            # Anything else
            msg = MIMEMultipart()
            alternative = MIMEMultipart('alternative')
            alternative.attach(self._mimetext(self.body, 'plain'))
            alternative.attach(self._mimetext(self.html, 'html'))
            msg.attach(alternative)

        msg['Subject'] = self.subject
        msg['From'] = self.sender
        msg['To'] = ', '.join(self.recipients)

        msg['Date'] = formatdate(self.date, localtime=True)

        if self.bcc:
            msg['Bcc'] = ', '.join(self.bcc)

        if self.cc:
            msg['Cc'] = ', '.join(self.cc)

        if self.reply_to:
            msg['Reply-To'] = self.reply_to

        if self.extra_headers:
            for k in self.extra_headers:
                msg[k] = self.extra_headers[k]

        if 'message-id' not in msg:
            msg['Message-ID'] = make_msgid()

        for attachment in self.attachments:
            f = MIMEBase(*attachment.content_type.split('/'))
            f.set_payload(attachment.data)
            encode_base64(f)

            f.add_header('Content-Disposition', '%s;filename=%s' %
                         (attachment.disposition, attachment.filename))

            for key, value in attachment.headers:
                f.add_header(key, value)

            msg.attach(f)

        return msg

    def as_string(self):
        """
        Return the message encoded as a string.
        """
        return self.as_message().as_string()

    def __str__(self):
        return self.as_string()

    def has_bad_headers(self):
        """
        Checks for bad headers i.e. newlines in subject, sender or recipients.
        """

        reply_to = self.reply_to or ''
        for val in [self.subject, self.sender, reply_to] + self.recipients:
            for c in '\r\n':
                if c in val:
                    return True
        return False

    def send(self, connection):
        """
        Verifies and sends the message.
        """

        assert self.recipients, "No recipients have been added"
        assert self.body or self.html, "No body or HTML has been set"
        assert self.sender, "No sender address has been set"

        if self.has_bad_headers():
            raise BadHeaderError()

        connection.send(self)

    def add_recipient(self, recipient):
        """
        Adds another recipient to the message.

        :param recipient: email address of recipient.
        """

        self.recipients.append(recipient)

    def attach(self,
               filename=None,
               content_type=None,
               data=None,
               disposition=None,
               headers=None):

        """
        Adds an attachment to the message.

        :param filename: filename of attachment
        :param content_type: file mimetype
        :param data: the raw file data
        :param disposition: content-disposition (if any)
        """
        self.attachments.append(
            Attachment(filename, content_type, data, disposition, headers))

    def all_addresses(self):
        addresses = []
        addresses.extend(self.recipients)
        if self.sender:
            addresses.append(self.sender)
        if self.cc:
            addresses.extend(self.cc)
        if self.bcc:
            addresses.extend(self.bcc)
        if self.reply_to:
            addresses.append(self.reply_to)
        return addresses

    def has_utf8_addresses(self):
        addresses = self.all_addresses()
        for a in addresses:
            if isinstance(a, bytes):
                try:
                    a = a.decode('ascii')
                except UnicodeDecodeError:
                    return True
            else:
                try:
                    a = a.encode('ascii')
                except UnicodeEncodeError:
                    return True
        return False
