import typing

import django.conf
import django.core.mail.backends.base
import django.core.mail.backends.smtp
import django.template
import django.utils.html
import lxml.etree
import requests
from django.utils.translation import ugettext_lazy as _

from . import base

__all__ = ("Backend",)


class Backend(base.Backend):

    ID = "json-webhook"
    PROTOCOL = "json-webhook"
    EDITOR_TYPE = "basic"
    VERBOSE_NAME = _("Generic Webhook (JSON)")

    @classmethod
    def parse_message(cls, body: str) -> typing.Mapping[str, str]:
        data = {}
        for line in body.split("\n"):
            parts = line.split(":")
            key = parts[0].strip()
            if key == "":
                continue
            data[key] = (":".join(parts[1:])).strip()
        return data

    @classmethod
    def build_message(cls, subject: str, body: str, parameters: dict, attachments):
        data = cls.parse_message(body)
        if cls.USE_SUBJECT:
            subject_html = "<h1>{}</h1>\n".format(subject)
        else:
            subject_html = ""
        def_list = "\n".join(
            "<dt>{}</dt><dd>{}</dd>".format(key, value) for key, value in data.items()
        )
        html = "<html>\n{}<dl>\n{}\n</dl>\n</html>".format(subject_html, def_list)
        context = django.template.Context(parameters)
        template = base.template_from_string(html)
        return template.render(context)

    @classmethod
    def preview_message(cls, subject: str, body: str, parameters: dict):
        return cls.build_message(subject, body, parameters, [])

    @classmethod
    def extract_model(cls, message):
        tree = lxml.etree.fromstring(message)
        if tree[0].tag == "h1":
            subject = tree[0].text
            dl_element = tree[1]
        else:
            subject = ""
            dl_element = tree[0]
        model = {}
        key = ""
        for element in dl_element:
            if element.tag == "dt":
                key = element.text
            else:
                model[key] = element.text
        return subject, model

    def send_message(self, _from_address, to_addresses, message):
        subject, model = self.extract_model(message)
        headers = {"Content-Type": "application/json"}
        for address in to_addresses:
            response = requests.post(address, json=model, headers=headers)
        if not response.ok:
            raise RuntimeError("HTTP error: {}".format(response.text))
