import json

from django.test import TestCase
import django.conf
import django.core.mail

from django_vox.backends.html_email import Backend


class TestHtmlEmailBackend(TestCase):

    TEXT = "<p>Here is a message <br/><br/> for {{ you }}"
    PARAMS = {"you": "me"}
    SUBJECT = "SUBJECT"
    MESSAGE = {
        "subject": "SUBJECT",
        "text": "Here is a message\n\nfor me",
        "html": "<p>Here is a message <br/><br/> for me",
    }
    PREVIEW = "<p>Here is a message <br/><br/> for me"

    @classmethod
    def test_build_message(cls):
        message = Backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS, [])
        obj = json.loads(message)
        assert cls.MESSAGE == obj

    @classmethod
    def test_preview_message(cls):
        message = Backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        message = Backend.build_message(self.SUBJECT, self.TEXT, self.PARAMS, [])

        from_address = django.conf.settings.DEFAULT_FROM_EMAIL
        to_addresses = ["george@example.test"]

        instance = Backend()
        instance.send_message(from_address, to_addresses, message)
        assert 1 == len(django.core.mail.outbox)
        mail = django.core.mail.outbox[0]
        assert mail.from_email == "admin@example.test"
        assert mail.to == ["george@example.test"]
        assert mail.body == self.MESSAGE["text"]
        assert mail.alternatives[0][1] == "text/html"
