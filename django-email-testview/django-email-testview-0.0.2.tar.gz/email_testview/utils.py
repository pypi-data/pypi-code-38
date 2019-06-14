from django.conf import settings
from django.core import mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .registry import registry


def send_mail(identifier, *email_args, **email_kwargs):
    email_func = registry.get_email_func(identifier)
    email_kwargs = email_func(*email_args, **email_kwargs)
    app_name, email_name = registry.get_app_and_email_name(identifier)

    if email_kwargs.get('from_email', None) is None:
        from_email = settings.FROM_EMAIL
    if email_kwargs.get('recipients', None) is None:
        recipients = [x[1] for x in settings.MANAGERS]
    if getattr(settings, 'EMAIL_DEBUG', False):
        recipients = [settings.ADMINS[0][1]]

    context = email_kwargs.get('context')
    subject = render_to_string(
        f'{app_name}/email/subject/{email_name}.html', context=context)
    html_message = render_to_string(
        f'{app_name}/email/body/{email_name}.html', context=context)
    plain_text = strip_tags(html_message)
    mail.send_mail(
        subject, plain_text, from_email, recipients, html_message=html_message)
