from unittest.mock import patch

import django.conf
from django.test import TestCase

import django_vox.backends.twitter


class TestTwitterBackend(TestCase):

    TEXT = "Here is a text message \n\n for {{ you }}"
    PARAMS = {"you": "me"}
    SUBJECT = "IGNORED"
    MESSAGE = "Here is a text message \n\n for me"
    PREVIEW = "Here is a text message <br/><br/> for me"

    @classmethod
    def test_build_message(cls):
        backend = django_vox.backends.twitter.Backend
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS, [])
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        backend = django_vox.backends.twitter.Backend
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        backend = django_vox.backends.twitter.Backend
        message = backend.build_message(self.SUBJECT, self.TEXT, self.PARAMS, [])
        with patch("twitter.Api"):
            with self.assertRaises(django.conf.ImproperlyConfigured):
                backend()
            with self.settings(
                DJANGO_VOX_TWITTER_CONSUMER_KEY="consumer key",
                DJANGO_VOX_TWITTER_CONSUMER_SECRET="consumer secret",
                DJANGO_VOX_TWITTER_TOKEN_KEY="token key",
                DJANGO_VOX_TWITTER_TOKEN_SECRET="token secret",
            ):
                instance = backend()
                # post a public message
                instance.send_message("", [], message)
                instance.send_message("", ["foo"], message)
                client = instance.client
                assert len(client.mock_calls) >= 2
                assert client.mock_calls[0][0] == "PostUpdate"
                assert client.mock_calls[0][1] == (message,)
                assert client.mock_calls[1][0] == "PostDirectMessage"
                assert client.mock_calls[1][1] == (message,)
                assert client.mock_calls[1][2] == {"screen_name": "foo"}
