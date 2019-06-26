from datetime import datetime
from unittest.mock import patch

from django.test import TestCase

from django_vox.backends.json_webhook import Backend

from tests.mock import MockJsonResponse


def mocked_requests_post(url, _data=None, json=None, **_kwargs):
    if url == "https://webhook.example":
        return MockJsonResponse("", 200)
    return MockJsonResponse(None, 404)


class TestJsonWebhookBackend(TestCase):

    TEXT = (
        'birthday : {{ birthday | date:"r" }}\n'
        'empty: {{ null_value | default:"blank" }}\n'
        "html: <i>{{ html }}</i>\n"
        "\n"
    )
    PARAMS = {
        "birthday": datetime(1984, 12, 11),
        "html": "<b>BOO!</b>",
        "null_value": None,
    }
    MESSAGE = (
        "<html>\n"
        "<dl>\n"
        "<dt>birthday</dt><dd>Tue, 11 Dec 1984 00:00:00 -0600</dd>\n"
        "<dt>empty</dt><dd>blank</dd>\n"
        "<dt>html</dt><dd><i>&lt;b&gt;BOO!&lt;/b&gt;</i></dd>\n"
        "</dl>\n"
        "</html>"
    )
    PREVIEW = MESSAGE

    @classmethod
    def test_build_message(cls):
        message = Backend.build_message("", cls.TEXT, cls.PARAMS, [])
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        message = Backend.preview_message("", cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        message = Backend.build_message("", self.TEXT, self.PARAMS, [])
        bad_address = "https://not.example"
        address = "https://webhook.example"
        with patch("requests.post", side_effect=mocked_requests_post):
            instance = Backend()
            with self.assertRaises(RuntimeError):
                instance.send_message("", [bad_address], message)
            instance.send_message("", [address], message)
            import requests

            check_model = requests.post.mock_calls[0][2]["json"]
            assert check_model["birthday"] == "Tue, 11 Dec 1984 00:00:00 -0600"
            assert check_model["empty"] == "blank"
            # not sure if this is actually what we want, but it's what
            # currently happens
            assert check_model["html"] is None

    def test_from_address(self):
        # we don't use from addresses, so this should be blank
        assert "" == Backend.get_from_address("foo", {})
