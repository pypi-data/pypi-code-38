# -*- coding: utf-8 -*-
from congo.communication import get_connection, get_full_email
from congo.communication.classes import SimpleSMSMessage
from congo.conf import settings
from congo.maintenance import get_current_site
from congo.utils.crypto import get_sha1
from congo.utils.text import render_content
from congo.utils.validators import POLISH_PHONE_REGEX
from datetime import datetime
from django.core.exceptions import ValidationError
from django.core.mail.message import EmailMultiAlternatives
from django.db import models
from django.db.models.aggregates import Count
from django.template import loader
from django.template.defaultfilters import truncatechars
from django.urls.base import reverse
from django.utils import translation, timezone
from django.utils.crypto import get_random_string
from django.utils.datastructures import OrderedDict
from django.utils.translation import gettext_lazy as _, pgettext, gettext
from email.mime.image import MIMEImage
from premailer import Premailer
from urllib.parse import urljoin
import logging
import os
import re
import string
import sys

class AbstractEmailSender(models.Model):
    name = models.CharField(_("Nazwa"), max_length = 255)
    email = models.EmailField(_("Adres e-mail"), unique = True)

    class Meta:
        verbose_name = _("Nadawca e-mail")
        verbose_name_plural = _("Nadawcy e-mail")
        abstract = True

    def __str__(self):
        return "%s (%s)" % (self.name, self.email)

    def get_full_email(self):
        return get_full_email(self.email, self.name)

class AbstractRecipientGroup(models.Model):
    name = models.CharField("Nazwa", max_length = 255)
    add_date = models.DateTimeField(auto_now_add = True, verbose_name = "Data utworzenia")
    change_date = models.DateTimeField(auto_now = True, verbose_name = "Data modyfikacji")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

    def get_recipients(self):
        raise NotImplementedError()

class AbstractEmailRecipientGroup(AbstractRecipientGroup):
    class Meta:
        verbose_name = _("Grupa odbiorców e-mail")
        verbose_name_plural = _("Grupy odbiorców e-mail")
        ordering = ('name',)
        abstract = True

class AbstractSMSRecipientGroup(AbstractRecipientGroup):
    class Meta:
        verbose_name = _("Grupa odbiorców SMS")
        verbose_name_plural = _("Grupy odbiorców SMS")
        ordering = ('name',)
        abstract = True

class AbstractRecipient(models.Model):
    OFF_LINE_FORM = 0
    ON_LINE_FORM = 1
    ON_LINE_ORDER = 2
    PHONE = 3
    EMAIL = 4
    PHONE_CALL = 5

    SOURCE_CHOICE = (
        (OFF_LINE_FORM, _("Formularz off-line")),
        (ON_LINE_FORM, _("Formularz on-line")),
        (ON_LINE_ORDER, _("Zamówienie on-line")),
        (EMAIL, _("Korespondencja e-mail")),
        (PHONE_CALL, _("Rozmowa telefoniczna")),
    )

    source = models.IntegerField(_("Źródło"), choices = SOURCE_CHOICE)
    add_date = models.DateTimeField(_("Data dodania"), default = timezone.now)
    change_date = models.DateTimeField(_("Data zmiany"), auto_now = True)
    is_tester = models.BooleanField(_("Jest testerem"), default = False, help_text = _("Czy otrzymuje wiadomości testowe?"))
    is_active = models.BooleanField(_("Aktywny"), default = True, help_text = _("Czy otrzymuje wiadomości?"))
    is_confirmed = models.BooleanField(_("Zatwierdzony"), default = False, help_text = _("Czy zatwierdzony?"))

    class Meta:
        abstract = True

    def get_token(self):
        return get_sha1(self.id)

    def check_token(self, token):
        return self.get_token() == token


class AbstractEmailRecipient(AbstractRecipient):
    SEX_CHOICES = (
        ('m', _("Male")),
        ('f', _("Female")),
    )

    name = models.CharField(_("Nazwa"), max_length = 255, null = True, blank = True, help_text = _("np. Jan Nowak"))
    vocative = models.CharField(_("Wołacz"), max_length = 255, null = True, blank = True, help_text = "np. Janie")
    sex = models.CharField(_("Płeć"), max_length = 1, null = True, blank = True, choices = SEX_CHOICES)
    email = models.EmailField(_("Adres e-mail"), unique = True)

    objects = models.Manager()

    class Meta:
        verbose_name = _("Odbiorca e-mail")
        verbose_name_plural = _("Odbiorcy e-mail")
        ordering = ('-add_date',)
        abstract = True

    def __str__(self):
        if self.name:
            return "%s (%s)" % (self.name, self.email)
        else:
            return self.email

    def get_full_email(self):
        return get_full_email(self.email, self.name)

    def get_greeting(self):
        if self.sex == "m":
            return (pgettext("pan", "Szanowny Panie %s!") % self.vocative) if self.vocative else _("Szanowny Panie!")
        elif self.sex == "f":
            return (pgettext("pani", "Szanowna Pani %s!") % self.vocative) if self.vocative else _("Szanowna Pani!")
        else:
            return gettext("Szanowni Państwo!")

#    def get_dative(self):
#        # @OG trans
#        # dative = celownik
#        # Komu? Czemu? (się przyglądam)
#        if self.sex == "m":
#            return "Pan"
#        elif self.sex == "f":
#            return "Pani"
#        else:
#            return "Państw"
#
#    def get_genitive(self):
#        # @OG trans
#        # dopełniacz = genitive
#        # Kogo? Czego? (nie ma)
#        if self.sex == "m":
#            return "Pana"
#        elif self.sex == "f":
#            return "Pani"
#        else:
#            return "Państwa"

    def get_token(self):
        return get_sha1(self.email)

    def check_token(self, token):
        return self.get_token() == token

    @classmethod
    def get_sex(cls, name):
        first_name = name.split(' ')[0]
        sex_list = cls.objects.filter(name__istartswith = "%s " % first_name, is_confirmed = True).values('sex').annotate(count = Count('sex')).order_by('-count')

        if sex_list:
            if sex_list[0]['count'] > 2:
                return sex_list[0]['sex']
        return None

    @classmethod
    def get_vocative(cls, name):
        first_name = name.split(' ')[0]
        vocative_list = cls.objects.filter(name__istartswith = "%s " % first_name, is_confirmed = True).values('vocative').annotate(count = Count('vocative')).order_by('-count')

        if vocative_list:
            if vocative_list[0]['count'] > 2:
                return vocative_list[0]['vocative']
        return ""

    @classmethod
    def subscribe(cls, email, name, source):
        recipient, created = cls.objects.get_or_create(email = email, defaults = {'source': source})

        if not recipient.is_active or not recipient.is_confirmed:
            recipient.name = name
            recipient.sex = cls.get_sex(name)
            recipient.vocative = cls.get_vocative(name)
            recipient.is_active = True
            recipient.is_confirmed = False
            recipient.save()


class AbstractSMSRecipient(AbstractRecipient):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, related_name = "user_sms_recipient", verbose_name = "Użytkownik", on_delete = models.CASCADE)

    class Meta:
        verbose_name = _("Odbiorca SMS")
        verbose_name_plural = _("Odbiorcy SMS")
        ordering = ('-add_date',)
        abstract = True

    def __str__(self):
        if self.name:
            return "%s (%s)" % (self.name, self.mobile_phone)
        else:
            return self.mobile_phone

    @property
    def name(self):
        return self.user.get_full_name()

    @property
    def mobile_phone(self):
        return self.user.mobile_phone

    def is_mobile_phone_valid(self):
        # @OG should by country resistant
        try:
            POLISH_PHONE_REGEX(self.user.mobile_phone)
        except ValidationError:
            return False
        return True

    def get_clean_mobile_phone(self):
        # @OG should by country resistant
        mobile_phone = self.mobile_phone
        if mobile_phone.startswith('+48'):
            return mobile_phone[3:]
        elif mobile_phone.startswith('0048'):
            return mobile_phone[4:]
        return mobile_phone

class AbstractMessage(models.Model):
    TEMPLATE_TAGS = '' # eg 'nested i18n'

    add_date = models.DateTimeField(_("Data dodania"), auto_now_add = True)
    change_date = models.DateTimeField(_("Data zmiany"), auto_now = True)
    is_tested = models.BooleanField(_("Przetestowany"), default = False, help_text = _("Czy wysłano do testerów?"))

    class Meta:
        abstract = True

    @property
    def template_tags(self):
        if not hasattr(self, '_templatetags'):
            return self.TEMPLATE_TAGS

    @template_tags.setter
    def template_tags(self, value):
        self._template_tags = value

    def get_token(self):
        return get_sha1(self.id)

    def check_token(self, token):
        return self.get_token() == token


class AbstractEmailMessage(AbstractMessage):
    """
    Abstrakcyjny model wiadomości e-mail.
    """

    TEMPLATE_CHOICE = (
        ('default', _("Szablon domyślny")),
    )

    sender = models.ForeignKey(settings.CONGO_EMAIL_SENDER_MODEL, related_name = "sender_email_messages", verbose_name = _("Nadawca"), on_delete = models.CASCADE)
    reply_to = models.ForeignKey(settings.CONGO_EMAIL_SENDER_MODEL, blank = True, null = True, related_name = "reply_to_email_messages", verbose_name = _("Odpowiedz do"), on_delete = models.CASCADE)
    subject = models.CharField(_("Temat"), max_length = 255)
    preheader = models.CharField(_("Preheader"), max_length = 100, blank = True, null = True)
    template = models.CharField(_("Szablon"), max_length = 50, choices = TEMPLATE_CHOICE)
    html_content = models.TextField(_("Treść HTML"))
    text_content = models.TextField(_("Treść tekstowa"))
    send_date = models.DateTimeField(_("Data wysłania"), default = timezone.now)

    class Meta:
        verbose_name = _("Wiadomość e-mail")
        verbose_name_plural = _("Wiadomości e-mail")
        ordering = ('-add_date',)
        abstract = True

    def __str__(self):
        return self.subject

    def get_absolute_url(self):
        return reverse('congo:email_preview', kwargs = {'message_id': self.id})

    def get_url_params(self):
        # http://support.google.com/analytics/bin/answer.py?hl=en&topic=1007028&answer=1033867
        pattern = '\?ga='
        params = "?utm_source=congo&utm_medium=email&utm_campaign=%s" % datetime.strftime(self.add_date, '%Y-%m-%d')
        return [(pattern, params)]

    def get_html_content(self, context_dict = {}, context = None, language = None):
        if not hasattr(self, '_html_content'):
            self._html_content = render_content(self.html_content, context_dict, context, language, self.template_tags)
        return self._html_content

    def get_text_content(self, context_dict = {}, context = None, language = None):
        if not hasattr(self, '_text_content'):
            self._text_content = render_content(self.text_content, context_dict, context, language, self.template_tags)
        return self._text_content

    def get_site(self):
        if not hasattr(self, 'site'):
            return None

        if not self.site and settings.CONGO_SITE_MODEL:
            self.site = get_current_site()
        return self.site

    def get_protocol(self):
        return settings.CONGO_EMAIL_PROTOCOL

    def get_domain(self):
        site = self.get_site()
        if site:
            return site.domain
        return settings.CONGO_EMAIL_TEMPLATE_DOMAIN

    def get_language(self):
        # override this method if languges are supported
        return None

    def get_unsubscribe_url(self, recipient, prepend_domain = True):
        if settings.CONGO_EMAIL_UNSUBSCRIBE_URL_NAME:
            url = reverse(settings.CONGO_EMAIL_UNSUBSCRIBE_URL_NAME, kwargs = {'object_id': recipient.id, 'token': recipient.get_token()})
            if prepend_domain:
                return "%s://%s%s" % (self.get_protocol(), self.get_domain(), url)
            return url
        return None

    def get_list_unsubscribe(self, recipient):
        list_unsubscribe = []

        unsubscribe_email = settings.CONGO_EMAIL_UNSUBSCRIBE_EMAIL
        if unsubscribe_email:
            list_unsubscribe.append("<mailto:%s>" % unsubscribe_email)

        unsubscribe_url = self.get_unsubscribe_url(recipient)
        if unsubscribe_url:
            list_unsubscribe.append("<%s>" % unsubscribe_url)

        return list_unsubscribe

    def render_template_tags(self):
        template_domain = settings.CONGO_EMAIL_TEMPLATE_DOMAIN
        site = self.get_site()
        protocol = self.get_protocol()
        domain = self.get_domain()
        language = self.get_language()

        text_template = loader.get_template('congo/email/%s.txt' % self.template)
        html_template = loader.get_template('congo/email/%s.html' % self.template)

        context = {
            'site': site,
            'protocol': protocol,
            'domain': domain,
            'subject': self.subject,
            'preheader': self.preheader,
            'text_content': self.get_text_content(),
            'html_content': self.get_html_content(),
        }

        # activate translation
        if language:
            translation.activate(language)

        # https://github.com/bendavis78/django-template-email/blob/master/template_email/__init__.py
        # https://github.com/peterbe/premailer/blob/master/premailer/premailer.py
        text_content = text_template.render(context)
        html_content = Premailer(html_template.render(context), base_path = settings.CONGO_EMAIL_PREMAILER_BASE_PATH).transform()

        # deactivate translation
        if language:
            translation.deactivate()

        text_content = re.sub(template_domain, domain, text_content)
        html_content = re.sub(template_domain, domain, html_content)

        # zamienie <a ... href="adres" ...> na <a ... href="http://www.faktor.pl/adres" ...>
        pattern = re.compile("""(<a[\s][^>]*href=['"])([^'"]*)(['"][^>]*>)""", re.IGNORECASE)
        html_content = pattern.sub(lambda x: x.group(1) + urljoin("http://%s/" % domain, x.group(2)) + x.group(3), html_content)

        # zamienie <a ... href="adres" ...> na <a ... href="http://www.faktor.pl/adres" ...>
        pattern = re.compile("""(<img[\s][^>]*src=['"])([^'"]*)(['"][^>]*>)""", re.IGNORECASE)
        html_content = pattern.sub(lambda x: x.group(1) + urljoin("http://%s/" % domain, x.group(2)) + x.group(3), html_content)

        # nowa linia po każdym zamkniętym tagu td, p lub div
        pattern = re.compile(r'</(td|p|div)>')
        html_content = pattern.sub(lambda x: x.group(0) + "\n", html_content)

        pattern = re.compile(r'(\r?\n)+')
        html_content = pattern.sub('\n', html_content)

        # for Google Analytics url params
        for pattern, params in self.get_url_params():
            text_content = re.sub(pattern, params, text_content)
            html_content = re.sub(pattern, params, html_content)

        return (text_content, html_content)

    def render_recipient_tags(self, text_content, html_content, recipient):
        html_content = re.sub(r'%7B!%20', '{! ', html_content)
        html_content = re.sub(r'%20!%7D', ' !}', html_content)

        unsubscribe_url = self.get_unsubscribe_url(recipient, prepend_domain = False)
        if unsubscribe_url:
            text_content = re.sub(r'{! unsubscribe !}', unsubscribe_url, text_content)
            html_content = re.sub(r'{! unsubscribe !}', unsubscribe_url, html_content)

        greeting = recipient.get_greeting()

        text_content = re.sub('{! greeting !}', greeting, text_content)
        html_content = re.sub('{! greeting !}', greeting, html_content)

#        dative = recipient.get_dative()
#        text_content = re.sub(r'{! dative !}', dative, text_content)
#        html_content = re.sub(r'{! dative !}', dative, html_content)
#
#        genitive = recipient.get_genitive()
#        text_content = re.sub(r'{! genitive !}', genitive, text_content)
#        html_content = re.sub(r'{! genitive !}', genitive, html_content)

#        code_pattern = """{! discount_code ([0-9]+) !}"""
#
#        def replace(matched_object):
#            return DiscountCode.generate_code(int(matched_object.group(1)), recipient.id)
#
#        html_content = re.sub(code_pattern, replace, html_content)
#        text_content = re.sub(code_pattern, replace, text_content)

        return (text_content, html_content)

    def render_images(self, html_content):
        image_pattern = """src=['"](?P<img_src>%s[^'"]*)['"]""" % settings.MEDIA_URL
        image_matches = re.findall(image_pattern, html_content)
        unique_matches = {}
        attachment_list = []
        domain = self.get_domain()
        chars = string.ascii_uppercase + string.digits

        for image_match in image_matches:
            if image_match not in unique_matches:
                image_path = os.path.join(settings.MEDIA_ROOT, image_match.replace(settings.MEDIA_URL, '').replace(domain, ''))
                image_file = open(image_path, 'rb').read()
                content_id = get_random_string(8, chars)
                mime_image = MIMEImage(image_file)
                mime_image.add_header('Content-ID', '<%s>' % content_id)
                mime_image.add_header('Content-Disposition', 'inline')
                attachment_list.append(mime_image)
                unique_matches[image_match] = content_id

        def replace(matched_object):
#             x = matched_object.group('img_src')
#             y = 'cid:%s' % str(unique_matches[matched_object.group('img_src')])
            return matched_object.group(0).replace(matched_object.group('img_src'), 'cid:%s' % unique_matches[matched_object.group('img_src')])

        if unique_matches:
            html_content = re.sub(image_pattern, replace, html_content)

        return (html_content, attachment_list)

    def send(self, recipient_list, user = None, **kwargs):
        logger = logging.getLogger('system.communication.send_email')

        # Renderujemy tagi szablonów
        text_content, html_content = self.render_template_tags()

        attachment_list = []

        # Pobieramy listę załączników
        if kwargs.get('attach_image', False):
            html_content, attachment_list = self.render_images(html_content)

        # Tworzymy i wysyłamy wiadomości
        sent_count = 0
        from_email = self.sender.get_full_email()
        reply_to_email = self.reply_to.get_full_email() if self.reply_to else None

        for recipient in recipient_list:
            extra = {
                'user': user,
                'extra_info': OrderedDict(),
            }

            if isinstance(recipient, AbstractEmailMessageQueue):
                mailing_queue = recipient
                recipient = mailing_queue.recipient
            else:
                mailing_queue = None

            # Renderujemy tagi odbiorcy
            recipient_text_content, recipient_html_content = self.render_recipient_tags(text_content, html_content, recipient)

            no = (sent_count + 1) if not mailing_queue else mailing_queue.id
            to_email = [recipient.get_full_email()]

            headers = {}
            if reply_to_email:
                headers['Reply-To'] = reply_to_email

            list_unsubscribe = self.get_list_unsubscribe(recipient)
            if list_unsubscribe:
                headers['List-Unsubscribe'] = ', '.join(list_unsubscribe)

            extra['extra_info']['no'] = no
            extra['extra_info']['recipient'] = to_email[0]

            subject = "[TEST] %s" % self.subject if kwargs.get('test', False) else self.subject
            message = EmailMultiAlternatives(subject, recipient_text_content, from_email, to_email, headers = headers)
            message.attach_alternative(recipient_html_content, 'text/html')
            message.mixed_subtype = 'related'

            # Załączamy załączniki
            for attachment in attachment_list:
                message.attach(attachment)

            try:
                sent_count += message.send()

                if mailing_queue:
                    mailing_queue.is_sent = True
                    mailing_queue.send_date = timezone.now()
                    mailing_queue.save()

                msg = _("Wysłano \"%s\" wiadomości") % self
                logger.debug(msg, extra = extra)
            except:
                msg = _("Wysłanie \"%s\" nie powidło się") % self
                exc_info = sys.exc_info()
                logger.error(msg, exc_info = exc_info, extra = extra)

            del message

        return sent_count

class AbstractSMSMessage(AbstractMessage):
    SENDER_CHOICE = settings.CONGO_SMS_SENDER_LIST

    sender = models.CharField(_("Nadawca"), max_length = 50, choices = SENDER_CHOICE)
    content = models.TextField(_("Treść"))
    send_date = models.DateTimeField(_("Data wysłania"), default = timezone.now)

    class Meta:
        verbose_name = _("Wiadomość SMS")
        verbose_name_plural = _("Wiadomości SMS")
        ordering = ('-add_date',)
        abstract = True

    def __str__(self):
        return truncatechars(self.content, 50)

    def get_content(self, context_dict = {}, context = None, language = None):
        if not hasattr(self, '_content'):
            self._content = str(render_content(self.content, context_dict, context, language, self.template_tags))
        return self._content

    def render_recipient_tags(self, content, recipient):
        # override this method
        return content

    def send(self, recipient_list, user):
        logger = logging.getLogger('system.communication.send_sms')
        sent_count = 0

        connection = get_connection()
        connection.open()

        content = self.get_content()

        for recipient in recipient_list:
            extra = {
                'user': user,
                'extra_info': OrderedDict(),
            }

            if isinstance(recipient, AbstractSMSMessageQueue):
                mailing_queue = recipient
                recipient = mailing_queue.recipient
            else:
                mailing_queue = None

            no = (sent_count + 1) if not mailing_queue else mailing_queue.id
            mobile_phone = recipient.get_clean_mobile_phone()

            if mobile_phone:
                extra['extra_info']['no'] = no
                extra['extra_info']['recipient'] = mobile_phone

                rendered_content = self.render_recipient_tags(content, recipient)
                message = SimpleSMSMessage(sender_name = self.sender, recipient_mobile_phone = mobile_phone, content = rendered_content, connection = connection)

                try:
                    for result in message.send():
                        extra['extra_info']['result_id'] = result.id
                        extra['extra_info']['result_status'] = result.status

                    sent_count += 1

                    if mailing_queue:
                        mailing_queue.is_sent = True
                        mailing_queue.send_date = timezone.now()
                        mailing_queue.save()

                    msg = _("Wysłano \"%s\" wiadomości") % self
                    logger.debug(msg, extra = extra)
                except:
                    msg = _("Wysłanie \"%s\" nie powidło się") % self
                    exc_info = sys.exc_info()
                    logger.error(msg, exc_info = exc_info, extra = extra)
            else:
                msg = _("Wysłanie \"%s\" nie powidło się") % self
                extra['extra_info']['error'] = _("Brak numeru telefonu dla odbiorcy %(name)s (ID: %(id)s)") % {'name': recipient.name, 'id': recipient.id}
                logger.error(msg, extra = extra)

        connection.close()

        return sent_count

#    @permalink
#    def get_absolute_url(self):
#        return ('communication_sms', (), {'object_id': self.id, 'token': self.get_token()})

class AbstractMessageQueue(models.Model):
    add_date = models.DateTimeField(_("Data dodania"), auto_now_add = True)
    send_date = models.DateTimeField(_("Data wysłania"), null = True, blank = True)
    is_sent = models.BooleanField(_("Wysłane"), default = False, help_text = _("Wysłane do odbiorców?"))

    class Meta:
        abstract = True

    @classmethod
    def has_messages_in_queue(cls):
        count = cls.objects.filter(is_sent = False).count()
        return count > 0


class AbstractEmailMessageQueue(AbstractMessageQueue):
    recipient = models.ForeignKey(settings.CONGO_EMAIL_RECIPIENT_MODEL, verbose_name = _("E-mail recipient"), on_delete = models.CASCADE)
    message = models.ForeignKey(settings.CONGO_EMAIL_MESSAGE_MODEL, verbose_name = _("E-mail message"), on_delete = models.CASCADE)

    class Meta:
        verbose_name = _("Kolejka wiadmości e-mail")
        verbose_name_plural = _("Kolejki wiadomości e-mail")
        unique_together = ('recipient', 'message',)
        ordering = ('-id',)
        abstract = True

    def __str__(self):
        return _("%(message)s do %(recipient)s") % {'message': self.message, 'recipient': self.recipient}

    @classmethod
    def send_messages(cls, limit = 5, user = None):
        logger = logging.getLogger('system.communication.send_email_queue')

        extra = {
            'user': user,
        }

        i = j = k = 0

        try:
            message = cls.objects.filter(is_sent = False, message__send_date__lte = timezone.now()).order_by('id')[0].message
            queue = cls.objects.filter(is_sent = False, message = message)
            k = queue.count()

            if k:
                queue = queue.order_by('id')[:limit]
                j = len(queue)
                msg = _("Wysyłanie \"%(message)s\" wiadomości (%(x)s / %(y)s)") % {'message': message, 'x': j, 'y': k}
                logger.debug(msg, extra = extra)
                i = message.send(queue, user)
        except IndexError:
            msg = _("Wysyłanie wiadomości e-mail (%(x)s / %(y)s)") % {'x': j, 'y': k}
            logger.debug(msg, extra = extra)

        return i, j, k


class AbstractSMSMessageQueue(AbstractMessageQueue):
    recipient = models.ForeignKey(settings.CONGO_SMS_RECIPIENT_MODEL, verbose_name = _("Odbiorca SMS"), on_delete = models.CASCADE)
    message = models.ForeignKey(settings.CONGO_SMS_MESSAGE_MODEL, verbose_name = _("SMS message"), on_delete = models.CASCADE)

    class Meta:
        verbose_name = _("Kolejka wiadomości SMS")
        verbose_name_plural = _("Kolejki wiadomości SMS")
        unique_together = ('recipient', 'message',)
        ordering = ('-id',)
        abstract = True

    def __str__(self):
        return _("%(message)s do %(recipient)s") % {'message': self.message, 'recipient': self.recipient}

    @classmethod
    def send_messages(cls, limit = 100, user = None):
        logger = logging.getLogger('system.communication.send_sms_queue')

        extra = {
            'user': user,
        }

        i = j = k = 0

        try:
            message = cls.objects.filter(is_sent = False, message__send_date__lte = timezone.now()).order_by('id')[0].message
            queue = cls.objects.filter(is_sent = False, message = message)
            k = queue.count()

            queue = queue.order_by('id')[:limit]
            j = len(queue)
            msg = _("Wysyłanie \"%(message)s\" wiadomości (%(x)s / %(y)s)") % {'message': message, 'x': j, 'y': k}
            logger.debug(msg, extra = extra)
            i = message.send(queue, user)

        except IndexError:
            msg = _("Wysyłanie wiadomości e-mail (%(x)s / %(y)s)") % {'x': j, 'y': k}
            logger.debug(msg, extra = extra)

        return i, j, k
