import django.template
from django.utils.translation import ugettext_lazy as _

from . import base, base_email

__all__ = ("Backend",)


class Backend(base_email.Backend):

    ID = "email"
    EDITOR_TYPE = "html"
    VERBOSE_NAME = _("Email (Template-based)")

    @classmethod
    def build_multipart(cls, subject: str, body: str, parameters: dict):
        return email_parts(subject, body, parameters)


# inspired by django-templated-mail
def email_parts(
    subject: str, body: str, parameters: dict
) -> base_email.MultipartMessage:
    message = base_email.MultipartMessage()
    html_context = django.template.Context(parameters)
    text_context = django.template.Context(parameters, autoescape=False)
    node_parts = {}
    subject_template = base.template_from_string(subject)
    body_template = base.template_from_string(body)
    message.subject = subject_template.render(text_context)

    for node in body_template.nodelist:
        name = getattr(node, "name", None)
        if name is not None:
            node_parts[name] = node

    with html_context.bind_template(body_template):
        with text_context.bind_template(body_template):
            if "subject" in node_parts:
                message.subject = node_parts["subject"].render(text_context).strip()
            has_parts = False
            if "text_body" in node_parts:
                has_parts = True
                message.text = node_parts["text_body"].render(text_context).strip()
            if "html_body" in node_parts:
                has_parts = True
                message.html = node_parts["html_body"].render(html_context).strip()
            if not has_parts:
                message.text = body_template.render(text_context).strip()
    return message
