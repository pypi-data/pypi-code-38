# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2018 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Email Framework
"""

from __future__ import unicode_literals, absolute_import

import os
import smtplib
import logging
from email.charset import Charset
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

import six

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

from rattail import exceptions
from rattail.core import UNSPECIFIED
from rattail.files import resource_path
from rattail.util import import_module_path
from rattail.time import localtime, make_utc


# NOTE: this bit of magic was stolen from Django
# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
utf8_charset = Charset('utf-8')
utf8_charset.body_encoding = None  # Python defaults to BASE64

log = logging.getLogger(__name__)


def send_email(config, key, data={}, attachments=[], fallback_key=None, enabled=UNSPECIFIED, **kwargs):
    """
    Send an email message of the given type, per config, with the given data
    and/or attachments.
    """
    # TODO: should let config override which handler we use
    handler = EmailHandler(config)
    email = handler.get_email(key, fallback_key=fallback_key)

    if enabled is UNSPECIFIED:
        enabled = handler.get_enabled(email)

    if enabled:
        kwargs['attachments'] = attachments
        handler.send_message(email, data, **kwargs)
    else:
        log.debug("skipping email of type '%s' per config", key)


# TODO: deprecate / remove this (used only for tailbone preview?)
def deliver_message(config, key, msg, recipients=UNSPECIFIED):
    """
    Deliver an email message using the given SMTP configuration.
    """
    if recipients is UNSPECIFIED:
        recips = set()
        to = msg.get_all('To')
        if to:
            recips = recips.union(set(to))
        cc = msg.get_all('Cc')
        if cc:
            recips = recips.union(set(cc))
        bcc = msg.get_all('Bcc')
        if bcc:
            recips = recips.union(set(bcc))
    else:
        recips = set(recipients)
    if not recips:
        raise RuntimeError("No recipients for email: {0}".format(repr(msg)))

    server = config.get('rattail.mail', 'smtp.server', default='localhost')
    username = config.get('rattail.mail', 'smtp.username')
    password = config.get('rattail.mail', 'smtp.password')

    if config.getbool('rattail.mail', 'send_feedback_only', usedb=False, default=False):
        send = key == 'user_feedback'
    else:
        send = config.getbool('rattail.mail', 'send_emails', usedb=False, default=True)

    if send:

        log.debug("attempting to send mail of type: %s", key)
        log.debug("connecting to server: %s", server)
        session = smtplib.SMTP(server)
        if username and password:
            result = session.login(username, password)
            log.debug("login() result is: %s", repr(result))

        result = session.sendmail(msg['From'], recips, msg.as_string())
        log.debug("sendmail() result is: %s", repr(result))
        session.quit()
        return True

    log.debug("config says no emails for '%s', but would have sent one to: %s", key, recips)
    return False


class EmailHandler(object):
    """
    Base class and default implementation for email handlers.
    """

    def __init__(self, config):
        self.config = config
        self.enum = self.config.get_enum()

    def get_email(self, key, fallback_key=None):
        """
        Return an email instance of the given type.
        """
        for email in self.iter_emails():
            if email.key == key or email.__name__ == key:
                return email(self.config, key, fallback_key)
        return Email(self.config, key, fallback_key)

    def iter_emails(self):
        """
        Iterate over all available email types.
        """
        for module in self.config.getlist('rattail.mail', 'emails', default=['rattail.emails']):
            module = import_module_path(module)
            for name in dir(module):
                obj = getattr(module, name)
                if (isinstance(obj, type) and issubclass(obj, Email)
                    and not obj.abstract and obj is not Email):
                    yield obj

    def get_enabled(self, email):
        return email.get_enabled()

    def send_message(self, email, data, **kwargs):
        msg = self.make_message(email, data, **kwargs)

        if self.config.getbool('rattail.mail', 'record_attempts', default=False):
            attempt = self.record_attempt(email, msg)
            try:
                self.deliver_message(email, msg)
            except Exception as e:
                self.record_failure(attempt, e)
            else:
                self.record_success(attempt)

        else: # don't record attempts
            self.deliver_message(email, msg)

    def record_attempt(self, email, msg):
        from rattail.db import Session, model

        session = Session()

        attempt = model.EmailAttempt()
        attempt.key = email.key
        attempt.sender = msg['From']
        attempt.to = msg.get_all('To')
        attempt.cc = msg.get_all('Cc')
        attempt.bcc = msg.get_all('Bcc')
        attempt.subject = msg['Subject']
        attempt.sent = make_utc()
        attempt.status_code = self.enum.EMAIL_ATTEMPT_CREATED

        session.add(attempt)
        session.commit()
        session.close()
        # session.expunge(attempt)
        return attempt

    def record_failure(self, attempt, error):
        from rattail.db import Session

        session = Session()
        attempt = session.merge(attempt)
        attempt.status_code = self.enum.EMAIL_ATTEMPT_FAILURE
        attempt.status_text = six.text_type(error)
        session.commit()
        session.close()

    def record_success(self, attempt):
        from rattail.db import Session

        session = Session()
        attempt = session.merge(attempt)
        attempt.status_code = self.enum.EMAIL_ATTEMPT_SUCCESS
        session.commit()
        session.close()

    def make_message(self, email, data, **kwargs):
        context = self.make_context(**data)
        return email.make_message(context, **kwargs)

    def make_context(self, **context):
        context['rattail_config'] = self.config
        context['app_title'] = self.config.app_title()
        context['localtime'] = localtime
        return context

    def deliver_message(self, email, msg, recipients=UNSPECIFIED):
        """
        Deliver an email message using the given SMTP configuration.
        """
        if recipients is UNSPECIFIED:
            recips = set()
            to = msg.get_all('To')
            if to:
                recips = recips.union(set(to))
            cc = msg.get_all('Cc')
            if cc:
                recips = recips.union(set(cc))
            bcc = msg.get_all('Bcc')
            if bcc:
                recips = recips.union(set(bcc))
        else:
            recips = set(recipients)
        if not recips:
            raise RuntimeError("No recipients for email: {0}".format(repr(msg)))

        server = self.config.get('rattail.mail', 'smtp.server', default='localhost')
        username = self.config.get('rattail.mail', 'smtp.username')
        password = self.config.get('rattail.mail', 'smtp.password')

        if self.config.getbool('rattail.mail', 'send_feedback_only', usedb=False, default=False):
            send = email.key == 'user_feedback'
        else:
            send = self.config.getbool('rattail.mail', 'send_emails', usedb=False, default=True)

        if send:

            log.debug("attempting to send mail of type: %s", email.key)
            log.debug("connecting to server: %s", server)
            session = smtplib.SMTP(server)
            if username and password:
                result = session.login(username, password)
                log.debug("login() result is: %s", repr(result))

            result = session.sendmail(msg['From'], recips, msg.as_string())
            log.debug("sendmail() result is: %s", repr(result))
            session.quit()
            return True

        log.debug("config says no emails for '%s', but would have sent one to: %s", email.key, recips)
        return False


class Email(object):
    # Note: The docstring of an email is leveraged by code, hence this odd one.
    """
    (This email has no description.)
    """
    key = None
    fallback_key = None
    abstract = False
    default_prefix = "[rattail]"
    default_subject = "Automated message"

    # Whether or not the email's :attr:`to` attribute is dynamically determined
    # at run-time, i.e. via some logic other than typical reading from config.
    dynamic_to = False
    dynamic_to_help = None

    def __init__(self, config, key=None, fallback_key=None):
        self.config = config
        self.enum = config.get_enum()

        if key:
            self.key = key
        elif not self.key:
            self.key = self.__class__.__name__
            if self.key == 'Email':
                raise exceptions.ConfigurationError("Email instance has no key: {0}".format(repr(self)))

        if fallback_key:
            self.fallback_key = fallback_key

        templates = config.getlist('rattail.mail', 'templates')
        if templates:
            templates = [resource_path(p) for p in templates]
        self.templates = TemplateLookup(directories=templates)

    def sample_data(self, request):
        return {}

    def get_enabled(self):
        """
        Get the enabled flag for the email's message type.
        """
        enabled = self.config.getbool('rattail.mail', '{0}.enabled'.format(self.key))
        if enabled is not None:
            return enabled
        enabled = self.config.getbool('rattail.mail', 'default.enabled')
        if enabled is not None:
            return enabled
        return self.config.getbool('rattail.mail', 'send_emails', default=True)

    def get_sender(self):
        """
        Returns the value for the message's ``From:`` header.

        :rtype: str
        """
        sender = self.config.get('rattail.mail', '{0}.from'.format(self.key))
        if not sender:
            sender = self.config.get('rattail.mail', 'default.from')
            if not sender:
                raise exceptions.SenderNotFound(self.key)
        return sender

    def get_replyto(self):
        """
        Get the Reply-To address for the message.
        """
        replyto = self.config.get('rattail.mail', '{0}.replyto'.format(self.key))
        if not replyto:
            replyto = self.config.get('rattail.mail', 'default.replyto')
        return replyto

    def get_recips(self, type_='to'):
        """
        Returns a list of recipients of the given type for the message.

        :param type_: Must be one of: ``('to', 'cc', 'bcc')``.

        :rtype: list
        """
        try:
            if type_.lower() not in ('to', 'cc', 'bcc'):
                raise Exception
        except:
            raise ValueError("Recipient type must be one of ('to', 'cc', 'bcc'); "
                             "not: {0}".format(repr(type_)))
        type_ = type_.lower()
        recips = self.config.getlist('rattail.mail', '{0}.{1}'.format(self.key, type_))
        if not recips:
            recips = self.config.getlist('rattail.mail', 'default.{0}'.format(type_))
        return recips

    def get_prefix(self, data={}, magic=True):
        """
        Returns a string to be used as the subject prefix for the message.

        :rtype: str
        """
        prefix = self.config.get('rattail.mail', '{0}.prefix'.format(self.key))
        if not prefix:
            prefix = self.config.get('rattail.mail', 'default.prefix')
        prefix = prefix or self.default_prefix
        if magic and not self.config.production():
            prefix = "[STAGE] {}".format(prefix)
        return prefix

    def get_subject(self, data={}, render=True, template=UNSPECIFIED):
        """
        Returns the base value for the message's subject header, i.e. minus
        prefix.

        :rtype: str
        """
        if template is UNSPECIFIED:
            template = self.config.get('rattail.mail', '{}.subject'.format(self.key),
                                       default=self.default_subject)
            if not template:
                template = self.config.get('rattail.mail', 'default.subject')
        if template and render:
            return Template(template).render(**data)
        return template

    def get_complete_subject(self, data={}, render=True, prefix=UNSPECIFIED, template=UNSPECIFIED):
        """
        Returns the value for the message's ``Subject:`` header, i.e. the base
        subject with the prefix applied.  Note that config may provide the
        complete subject also, in which case the prefix and base subject are
        not considered.

        :rtype: str
        """
        if prefix is UNSPECIFIED:
            prefix = self.get_prefix(data)
        prefix = (prefix or "").rstrip()
        if prefix:
            prefix = "{} ".format(prefix)
        return "{}{}".format(prefix, self.get_subject(data, render=render, template=template))

    def get_template(self, type_):
        """
        Locate and return the Mako email template of the given type
        (e.g. 'html'), or ``None`` if no such template can be found.
        """
        try:
            return self.templates.get_template('{0}.{1}.mako'.format(self.key, type_))
        except TopLevelLookupException:
            if self.fallback_key:
                try:
                    return self.templates.get_template('{0}.{1}.mako'.format(self.fallback_key, type_))
                except TopLevelLookupException:
                    pass

    def normalize_attachments(self, attachments):
        normalized = []
        for attachment in attachments:
            if isinstance(attachment, six.string_types):
                attachment = self.normalize_attachment(attachment)
            normalized.append(attachment)
        return normalized

    ATTACHMENT_MIME_MAP = {
        '.doc': 'application/msword',
        '.pdf': 'pdf',
        '.xls': 'vnd.ms-excel',
    }

    def normalize_attachment(self, path):
        root, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext == '.csv':
            with open(path, 'rb') as f:
                part = MIMEText(f.read(), 'csv', 'utf_8')
            filename = os.path.basename(path)
            part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
            return part
        else:
            mimetype = self.ATTACHMENT_MIME_MAP.get(ext)
            if mimetype:
                with open(path, 'rb') as f:
                    part = MIMEApplication(f.read(), mimetype)
                filename = os.path.basename(path)
                part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
                return part
        raise ValueError("Magic is not (yet) supported, please construct your own attachments for file: {}".format(path))

    def make_message(self, data={}, attachments=[], inlines=[],
                     subject_prefix=UNSPECIFIED, subject_template=UNSPECIFIED,
                     sender=UNSPECIFIED, replyto=UNSPECIFIED,
                     to=UNSPECIFIED, cc=UNSPECIFIED, bcc=UNSPECIFIED):
        """
        Returns a proper email ``Message`` instance which may be sent via SMTP.
        """
        txt_template = self.get_template('txt')
        html_template = self.get_template('html')
        attachments = self.normalize_attachments(attachments)

        # TODO: provide more defaults?
        data.setdefault('six', six)

        if txt_template and html_template:

            txt_part = MIMEText(txt_template.render(**data), _charset='utf_8')

            html_part = MIMEText(html_template.render(**data), _subtype='html', _charset='utf_8')
            if inlines:
                html_part = MIMEMultipart(_subtype='related', _subparts=[html_part] + inlines)

            msg = MIMEMultipart(_subtype='alternative', _subparts=[txt_part, html_part])
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        elif txt_template:

            msg = MIMEText(txt_template.render(**data), _charset='utf_8')
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        elif html_template:

            msg = SafeMIMEText(html_template.render(**data), 'html', utf8_charset)
            if inlines:
                msg = MIMEMultipart(_subtype='related', _subparts=[msg] + inlines)
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        else:
            raise exceptions.MailTemplateNotFound(self.key)

        self.add_headers(msg, data=data,
                         subject_prefix=subject_prefix, subject_template=subject_template,
                         sender=sender, replyto=replyto, to=to, cc=cc, bcc=bcc)
        return msg

    def add_headers(self, msg, data={},
                    subject_prefix=UNSPECIFIED, subject_template=UNSPECIFIED,
                    sender=UNSPECIFIED, replyto=UNSPECIFIED,
                    to=UNSPECIFIED, cc=UNSPECIFIED, bcc=UNSPECIFIED):
        """
        Adds headers for to/from addresses etc. to message
        """
        # subject/from
        msg['Subject'] = self.get_complete_subject(data, prefix=subject_prefix,
                                                   template=subject_template)
        if sender is UNSPECIFIED:
            sender = self.get_sender()
        msg['From'] = sender

        # reply-to
        if replyto is UNSPECIFIED:
            replyto = self.get_replyto()
        if replyto:
            msg.add_header('Reply-To', replyto)

        # recipients
        force_to = self.config.getlist('rattail.mail', 'force_to', usedb=False)
        if force_to:
            to = force_to
            cc = None
            bcc = None
        else:
            if to is UNSPECIFIED:
                to = self.get_recips('to')
            if cc is UNSPECIFIED:
                cc = self.get_recips('cc')
            if bcc is UNSPECIFIED:
                bcc = self.get_recips('bcc')
        if not (to or cc or bcc):
            raise exceptions.RecipientsNotFound(self.key)
        if to:
            for recip in to:
                msg['To'] = recip
        if cc:
            for recip in cc:
                msg['Cc'] = recip
        if bcc:
            for recip in bcc:
                msg['Bcc'] = recip


# NOTE: this bit of magic was stolen from Django
class SafeMIMEText(MIMEText):

    def __init__(self, text, subtype, charset):
        self.encoding = charset
        if charset == 'utf-8':
            # Unfortunately, Python doesn't support setting a Charset instance
            # as MIMEText init parameter (http://bugs.python.org/issue16324).
            # We do it manually and trigger re-encoding of the payload.
            MIMEText.__init__(self, text, subtype, None)
            del self['Content-Transfer-Encoding']
            # TODO: i don't personally need this yet, if ever?
            # # Workaround for versions without http://bugs.python.org/issue19063
            # if (3, 2) < sys.version_info < (3, 3, 4):
            #     payload = text.encode(utf8_charset.output_charset)
            #     self._payload = payload.decode('ascii', 'surrogateescape')
            #     self.set_charset(utf8_charset)
            # else:
            #     self.set_payload(text, utf8_charset)
            self.set_payload(text, utf8_charset)
            self.replace_header('Content-Type', 'text/%s; charset="%s"' % (subtype, charset))
        else:
            MIMEText.__init__(self, text, subtype, charset)
