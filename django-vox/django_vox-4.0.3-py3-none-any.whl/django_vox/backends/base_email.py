import base64
import json
from typing import List

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
from django.core import mail
from django.utils.text import re_newlines
from django.utils.translation import ugettext_lazy as _

from . import base


class MultipartMessage:
    def __init__(self):
        self.subject = ""
        self.text = ""
        self.html = ""
        self.attachments = []

    @classmethod
    def from_dict(cls, obj):
        result = cls()
        result.subject = obj.get("subject")
        result.text = obj.get("text")
        result.html = obj.get("html")
        result.attachments = [
            base.AttachmentData(base64.b64decode(a["data"].encode()), a["mime"])
            for a in obj.get("attachments", ())
        ]
        return result

    @classmethod
    def from_string(cls, string):
        return cls.from_dict(json.loads(string))

    def to_dict(self):
        result = {"subject": self.subject, "text": self.text, "html": self.html}
        if self.attachments:
            result["attachments"] = [
                {"data": base64.b64encode(a.data).decode(), "mime": a.mime}
                for a in self.attachments
            ]
        return result

    def __str__(self):
        return json.dumps(self.to_dict())

    def to_mail(self) -> mail.EmailMultiAlternatives:
        email = mail.EmailMultiAlternatives()
        email.subject = re_newlines.sub(" ", self.subject)
        if self.text:
            email.body = self.text
            if self.html:
                email.attach_alternative(self.html, "text/html")
        elif self.html:
            email.body = self.html
            email.content_subtype = "html"
        for attachment in self.attachments:
            # workaround for django 1.10 problem
            data, mime = attachment.data, attachment.mime
            if mime.startswith("text/"):
                data = data.decode()
            email.attach(content=data, mimetype=mime)
        return email

    def attach(self, data: base.AttachmentData):
        self.attachments.append(data)


class Backend(base.Backend):

    ID = "email-basic"
    PROTOCOL = "email"
    VERBOSE_NAME = _("Email (Basic)")
    USE_SUBJECT = True
    USE_ATTACHMENTS = True
    USE_FROM_ADDRESS = True

    @classmethod
    def build_multipart(
        cls, subject: str, body: str, parameters: dict
    ) -> MultipartMessage:
        raise NotImplementedError()

    @classmethod
    def build_message(
        cls,
        subject: str,
        body: str,
        parameters: dict,
        attachments: List[base.AttachmentData],
    ):
        mpm = cls.build_multipart(subject, body, parameters)
        for attachment in attachments:
            mpm.attach(attachment)
        return str(mpm)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        parts = cls.build_multipart(subject, body, parameters)
        if parts.html:
            return parts.html
        return django.utils.html.escape(parts.text)

    def send_message(self, from_address, to_addresses, message):
        mpm = MultipartMessage.from_string(message)
        email = mpm.to_mail()
        email.from_email = from_address
        email.to = list(to_addresses)
        connection = django.core.mail.get_connection()
        connection.send_messages([email])

    @staticmethod
    def get_default_from_address():
        return django.conf.settings.DEFAULT_FROM_EMAIL
