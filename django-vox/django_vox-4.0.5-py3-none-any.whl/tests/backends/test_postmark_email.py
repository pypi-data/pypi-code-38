from unittest.mock import patch

import django.conf
from django.test import TestCase

from django_vox.backends.postmark_email import Backend

from tests.mock import MockJsonResponse


def mocked_requests_post(url, _data=None, json=None, **_kwargs):
    if url == Backend.ENDPOINT:
        if not (json.get("TemplateAlias") or json.get("TemplateId")):
            return MockJsonResponse({"ErrorCode": "403", "Message": "details"}, 422)
        else:
            return MockJsonResponse(
                {
                    "To": "george@example.test",
                    "SubmittedAt": "2014-02-17T07:25:01.4178645-05:00",
                    "MessageID": "0a129aee-e1cd-480d-b08d-4f48548ff48d",
                    "ErrorCode": 0,
                    "Message": "OK",
                },
                200,
            )
    return MockJsonResponse(None, 404)


class TestPostmarkBackend(TestCase):

    TEXT = (
        "line 1 : {{ line_1 }}\n"
        "line 2 : {{ line_2 }}\n"
        "line 3 : {{ line_3 }}\n"
        "line 4 : {{ line_4 }}\n"
        "\n\n"
        "c'est vide"
    )
    PARAMS = {
        "line_1": "poisson un",
        "line_2": "poisson deux",
        "line_3": "poisson rouge",
        "line_4": "poisson bleu",
    }
    SUBJECT = "SUBJECT"
    MESSAGE = (
        "<html>\n"
        "<h1>SUBJECT</h1>\n"
        "<dl>\n"
        "<dt>line 1</dt><dd>poisson un</dd>\n"
        "<dt>line 2</dt><dd>poisson deux</dd>\n"
        "<dt>line 3</dt><dd>poisson rouge</dd>\n"
        "<dt>line 4</dt><dd>poisson bleu</dd>\n"
        "<dt>c'est vide</dt><dd></dd>\n"
        "</dl>\n"
        "</html>"
    )
    PREVIEW = MESSAGE

    @classmethod
    def test_build_message(cls):
        backend = Backend()
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS, [])
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        backend = Backend()
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_send_message(self):
        backend = Backend
        bad_message = backend.build_message("", self.TEXT, self.PARAMS, [])
        message = backend.build_message(self.SUBJECT, self.TEXT, self.PARAMS, [])
        from_address = backend.get_default_from_address()
        to_addresses = ["george@example.test"]
        with patch("requests.post", side_effect=mocked_requests_post):
            instance = backend()
            with self.assertRaises(django.conf.ImproperlyConfigured):
                instance.send_message(from_address, to_addresses, message)
            with self.settings(DJANGO_VOX_POSTMARK_TOKEN="token"):
                with self.assertRaises(RuntimeError):
                    instance.send_message(from_address, to_addresses, bad_message)
                instance.send_message(from_address, to_addresses, message)
                import requests

                call_json = requests.post.mock_calls[1][2]["json"]
                assert "admin@example.test" == call_json["From"]
                assert "george@example.test" == call_json["To"]
                check_model = call_json["TemplateModel"]
                assert check_model["line 1"] == "poisson un"
                assert check_model["line 2"] == "poisson deux"
                assert "c'est vide" in check_model
