import datetime
import decimal
import re

import django.template
from django.utils.translation import ugettext_lazy as _

from django_vox import settings

from . import base, base_email

__all__ = ("Backend",)


class Backend(base_email.Backend):

    ID = "email-md"
    EDITOR_TYPE = "markdown"
    VERBOSE_NAME = _("Email (Markdown)")
    DEPENDS = ("markdown2",)

    @classmethod
    def build_multipart(cls, subject: str, body: str, parameters: dict):
        return email_md(subject, body, parameters)


class MarkdownParameters:

    IGNORED_TYPES = (
        int,
        float,
        decimal.Decimal,
        datetime.timedelta,
        datetime.datetime,
        datetime.date,
        datetime.time,
    )
    MD_SPECIAL_PATTERN = re.compile(r"[\\`*_{\}\[\]()#+\-.!]")

    @classmethod
    def wrap(cls, obj):
        if callable(obj):
            return CallableMarkdownParameters(obj)
        elif isinstance(obj, cls.IGNORED_TYPES):
            return obj
        return MarkdownParameters(obj)

    def __init__(self, obj):
        self._obj = obj

    def __contains__(self, item):
        return self._obj.__contains__(item)

    def __getitem__(self, item):
        return self.wrap(self._obj[item])

    def __getattr__(self, attr):
        return self.wrap(getattr(self._obj, attr))

    def __str__(self):
        return self.MD_SPECIAL_PATTERN.sub(self.escape, str(self._obj))

    @staticmethod
    def escape(patterns) -> str:
        return "\\" + patterns[0]


class CallableMarkdownParameters(MarkdownParameters):
    def __call__(self, *args, **kwargs):
        self.wrap(self._obj.__call__(*args, **kwargs))


def email_md(subject: str, body: str, parameters: dict) -> base_email.MultipartMessage:
    import markdown2

    md_parameters = MarkdownParameters(parameters)
    text_context = django.template.Context(parameters, autoescape=False)
    md_context = django.template.Context(md_parameters, autoescape=False)
    message = base_email.MultipartMessage()
    subject_template = base.template_from_string(subject)
    body_template = base.template_from_string(body)
    message.subject = subject_template.render(text_context)
    message.text = body_template.render(text_context)
    md_body = body_template.render(md_context)
    message.html = markdown2.markdown(
        md_body,
        extras=settings.MARKDOWN_EXTRAS,
        link_patterns=settings.MARKDOWN_LINK_PATTERNS,
    )
    return message
