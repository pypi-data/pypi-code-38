# -*- coding: utf-8 -*-
from congo.communication import get_full_email
from congo.maintenance import get_current_site
from django.conf import settings
from django.core.mail.message import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from premailer import Premailer
import re
from django.core.mail import get_connection
from smtplib import SMTPRecipientsRefused

class SimpleEmailSender(object):
    def __init__(self, email = None, name = None):
        self.email = email or settings.DEFAULT_FROM_EMAIL

        if name:
            self.name = name

    def get_full_email(self):
        return get_full_email(self.email, self.name)

class SimpleEmailMessage(object):
    def __init__(self, subject, sender_email = None, sender_name = None, recipient_email = None, recipient_name = None, data_dict = {}, headers = {}, mimetype = "html", site = None, domain = None, protocol = None, template = 'base', language = None, attachments = [], base_attachments = []):
        self.subject = subject
        self.sender_email = sender_email
        self.sender_name = sender_name
        self.recipient_email = recipient_email
        self.recipient_name = recipient_name
        self.data_dict = data_dict
        self.headers = headers
        self.mimetype = mimetype # html lub plain
        self.site = site
        self.domain = domain
        self.protocol = protocol
        self.template = template
        self.language = language
        self.attachments = attachments # list of paths to files
        self.base_attachments = base_attachments # list of base files

        if self.sender_name:
            self.sender_name = self.sender_name.replace("\"", "'")

    def __unicode__(self):
        return u"%s" % self.subject

    def get_sender_full_email(self):
        sender_email = self.sender_email
        sender_name = self.sender_name

        if not sender_email:
            sender_email = settings.DEFAULT_FROM_EMAIL
            if not sender_name:
                sender_name = settings.CONGO_DEFAULT_FROM_EMAIL_NAME

        return get_full_email(sender_email, sender_name)

    def get_recipient_full_email(self):
        return get_full_email(self.recipient_email, self.recipient_name)

    def get_site(self):
        if not self.site and settings.CONGO_SITE_MODEL:
            self.site = get_current_site()
        return self.site

    def get_domain(self):
        if self.domain:
            return self.domain
        site = self.get_site()
        if site:
            return site.domain
        return settings.CONGO_EMAIL_TEMPLATE_DOMAIN

    def get_protocol(self):
        if self.protocol:
            return self.protocol
        return settings.CONGO_EMAIL_PROTOCOL

    def get_language(self):
        if not self.language:
            site = self.get_site()
            if self.site:
                self.language = site.language
        return self.language

    def render_content(self):

        template_domain = settings.CONGO_EMAIL_TEMPLATE_DOMAIN
        site = self.get_site()
        protocol = self.get_protocol()
        domain = self.get_domain()
        language = self.get_language()

        data_dict = {
            'site': site,
            'protocol': protocol,
            'domain': domain,
            'subject': self.subject,
        }

        data_dict.update(self.data_dict)

        # translation
        if language:
            translation.activate(language)

        template_name = 'email/%s.txt' % self.template
        text_content = render_to_string(template_name, data_dict)

        text_content = re.sub(template_domain, domain, text_content)

        if self.mimetype == 'html':
            template_name = 'email/%s.html' % self.template
            html_string = render_to_string(template_name, data_dict)

            # https://github.com/bendavis78/django-template-email/blob/master/template_email/__init__.py
            # https://github.com/peterbe/premailer/blob/master/premailer/premailer.py
            base_url = "%s://%s" % (protocol, domain)
            html_content = Premailer(html_string, base_path = settings.CONGO_EMAIL_PREMAILER_BASE_PATH, base_url = base_url).transform()

#            # @OG! dobugowanie css'a w mailu
#            import sys
#            import logging
#
#            exc_info = sys.exc_info()
#            extra = {
#                'extra_info': {}
#            }
#
#            extra['extra_info']['html_string'] = html_string
#            extra['extra_info']['html_content'] = html_content
#            extra['extra_info']['base_path'] = settings.CONGO_EMAIL_PREMAILER_BASE_PATH
#            extra['extra_info']['base_url'] = base_url
#
#            logger = logging.getLogger('system.mail')
#            logger.log(logging.INFO, 'html_content', exc_info = exc_info, extra = extra)


            if self.site:
                html_content = re.sub(template_domain, domain, html_content)

            # nowa linia po każdym zamkniętym tagu td, p lub div
            pattern = re.compile(r'</(td|p|div)>')
            html_content = pattern.sub(lambda x: x.group(0) + "\n", html_content)

            pattern = re.compile(r'(\r?\n)+')
            html_content = pattern.sub('\n', html_content)
        else:
            html_content = None

        # translation
        if language:
            translation.deactivate()

        return (text_content, html_content)

    def send(self):
        text_content, html_content = self.render_content()

        from_email = self.get_sender_full_email()
        to_email = [self.get_recipient_full_email()]
        reply_to = self.headers.pop('Reply-To', None)

        # @og metoda EmailMultiAlternatives._create_attachment() tworzy załącznik jako:
        # Content-Disposition: attachment; filename="plik.pdf"
        # a powinna:
        # Content-Disposition: attachment; filename="plik.pdf"; size=136557
        # ...nadpisać tę metodę.
        message = EmailMultiAlternatives(self.subject, text_content, from_email, to_email, headers = self.headers, reply_to = reply_to)

        if html_content:
            message.attach_alternative(html_content, 'text/html')
            message.mixed_subtype = 'related'

        for attachment in self.attachments:
            message.attach_file(attachment)

        for base_attachment in self.base_attachments:
            message.attach(base_attachment['filename'], base_attachment['content'], base_attachment['mimetype'])

#        # @OG! dobugowanie wysyłki maila
#        connection = get_connection()
#        message.connection = connection
#
#        import sys
#        import logging
#
#        exc_info = sys.exc_info()
#        extra = {
#            'extra_info': {}
#        }
#
#        extra['extra_info']['connection'] = connection
#        extra['extra_info']['from_email'] = from_email
#        extra['extra_info']['to_email'] = to_email
#        extra['extra_info']['headers'] = self.headers
#        extra['extra_info']['reply_to'] = reply_to
#        extra['extra_info']['subject'] = self.subject
#        extra['extra_info']['text_content'] = text_content
#
#        logger = logging.getLogger('system.mail')
#        logger.log(logging.INFO, 'mail_test', exc_info = exc_info, extra = extra)

        try:
            return message.send()
        except SMTPRecipientsRefused:
            pass

class SMSAPIDummyResult():
    id = 0
    status = 0

@python_2_unicode_compatible
class SimpleSMSMessage(object):
    def __init__(self, sender_name, recipient_mobile_phone, content, connection = None):
        self.sender_name = sender_name
        self.recipient_mobile_phone = recipient_mobile_phone
        self.content = content
        self.connection = connection

    def __str__(self):
        return _(u"SMS od %(sender_name)s do %(recipient_mobile_phone)s") % {'sender_name': self.sender_name, 'recipient_mobile_phone': self.recipient_mobile_phone}

    def get_connection(self, fail_silently = False, **kwargs):
        if not self.connection:
            self.connection = get_connection(fail_silently = fail_silently, **kwargs)
        return self.connection

    def send(self, fail_silently = False):
        result = self.get_connection(fail_silently).send_messages([self])
        try:
            return result[0]
        except IndexError:
            return [SMSAPIDummyResult()]
