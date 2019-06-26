import august
import django.template
from django.utils.translation import ugettext_lazy as _

from . import base, base_email

__all__ = ("Backend",)


class Backend(base_email.Backend):

    ID = "email-html"
    VERBOSE_NAME = _("Email (HTML)")
    EDITOR_TYPE = "html"
    DEPENDS = ()

    @classmethod
    def build_multipart(cls, subject: str, body: str, parameters: dict):
        return email_html(subject, body, parameters)


def email_html(
    subject: str, body: str, parameters: dict
) -> base_email.MultipartMessage:
    text_context = django.template.Context(parameters, autoescape=False)
    html_context = django.template.Context(parameters, autoescape=True)
    message = base_email.MultipartMessage()
    # subject
    subject_template = base.template_from_string(subject)
    message.subject = subject_template.render(text_context)
    # html
    body_template = base.template_from_string(body)
    message.html = body_template.render(html_context)
    message.text = august.convert(message.html)
    return message
