import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
import requests
from django.utils.translation import ugettext_lazy as _

import django_vox.settings

from . import json_webhook

__all__ = ("Backend",)


class Backend(json_webhook.Backend):

    ID = "postmark-template"
    PROTOCOL = "email"
    EDITOR_TYPE = "html"
    VERBOSE_NAME = _("Email (Postmark Templates)")
    ENDPOINT = "https://api.postmarkapp.com/email/withTemplate"
    USE_SUBJECT = True
    USE_FROM_ADDRESS = True

    def send_message(self, from_address, to_addresses, message):
        subject, model = self.extract_model(message)
        data = {
            "TemplateAlias": subject,
            "TemplateModel": model,
            "From": from_address,
            "To": ",".join(to_addresses),
        }
        token = django_vox.settings.POSTMARK_TOKEN
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "X-Postmark-Server-Token": token,
        }

        response = requests.post(self.ENDPOINT, json=data, headers=headers)
        data_result = response.json()
        if not response.ok:
            raise RuntimeError(
                "Postmark error: {} {}".format(
                    data_result["ErrorCode"], data_result["Message"]
                )
            )

    @staticmethod
    def get_default_from_address():
        return django.conf.settings.DEFAULT_FROM_EMAIL
