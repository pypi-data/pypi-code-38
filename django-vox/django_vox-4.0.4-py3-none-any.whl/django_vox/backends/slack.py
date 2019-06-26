import json

import requests
from django.utils.translation import ugettext_lazy as _

from . import base

__all__ = ("Backend",)


class Backend(base.Backend):

    ID = "slack-webhook"
    PROTOCOL = "slack-webhook"
    ESCAPE_HTML = False
    EDITOR_TYPE = "basic"
    VERBOSE_NAME = _("Slack")

    def send_message(self, _from_address, to_addresses, message):
        data = json.dumps({"text": message})
        headers = {"Content-Type": "application/json"}
        for address in to_addresses:
            result = requests.post(address, data=data, headers=headers)
            if not result.ok:
                raise requests.HTTPError(result.text)
