from unittest.mock import patch

import django.conf
from django.test import TestCase

from django_vox.backends.twilio import Backend


class TestTwilioBackend(TestCase):

    TEXT = "Here is a text message \n\n for {{ you }}"
    PARAMS = {"you": "me"}
    SUBJECT = "IGNORED"
    MESSAGE = "Here is a text message \n\n for me"
    PREVIEW = "Here is a text message <br/><br/> for me"

    @classmethod
    def test_build_message(cls):
        message = Backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS, [])
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        message = Backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        message = Backend.build_message(self.SUBJECT, self.TEXT, self.PARAMS, [])
        with patch("twilio.rest.Client"):
            with self.assertRaises(django.conf.ImproperlyConfigured):
                Backend()
            with self.settings(
                DJANGO_VOX_TWILIO_ACCOUNT_SID="abc",
                DJANGO_VOX_TWILIO_AUTH_TOKEN="secret",
                DJANGO_VOX_TWILIO_FROM_NUMBER="+321",
            ):
                instance = Backend()
                from_address = Backend.get_from_address("", {})
                instance.send_message(from_address, ["+123"], message)
                import twilio.rest

                client = twilio.rest.Client
                assert len(client.mock_calls) > 1
                assert client.mock_calls[0][0] == ""  # class instantiation
                fname, args, kwargs = client.mock_calls[1]
                assert fname == "().messages.create"
                assert args == ()
                assert len(kwargs) == 3
                assert "+123" == kwargs["to"]
                assert "+321" == kwargs["from_"]
                assert self.MESSAGE == kwargs["body"]
