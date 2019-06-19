from django.utils.translation import ugettext_lazy as _

from django_vox import settings

from . import base

__all__ = ("Backend",)


class Backend(base.Backend):

    ID = "twilio"
    PROTOCOL = "sms"
    USE_FROM_ADDRESS = True
    ESCAPE_HTML = False
    EDITOR_TYPE = "basic"
    VERBOSE_NAME = _("Twilio")
    DEPENDS = ("twilio",)

    def __init__(self):
        from twilio.rest import Client

        self.client = Client(
            username=settings.TWILIO_ACCOUNT_SID, password=settings.TWILIO_AUTH_TOKEN
        )

    def send_message(self, from_address, to_addresses, message):
        for address in to_addresses:
            self.client.messages.create(to=address, from_=from_address, body=message)

    @classmethod
    def get_default_from_address(cls):
        return settings.TWILIO_FROM_NUMBER
