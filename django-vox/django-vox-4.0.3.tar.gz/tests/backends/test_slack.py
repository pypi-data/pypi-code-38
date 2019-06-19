from unittest.mock import patch

from django.test import TestCase

from django_vox.backends.slack import Backend

from tests.mock import MockTextResponse


def mocked_requests_post(url, _data=None, json=None, **_kwargs):
    if url.startswith("https://hooks.slack.com/services/"):
        return MockTextResponse("ok", 200)
    return MockTextResponse("", 404)


class TestSlackBackend(TestCase):

    TEXT = "Here is a text message \n\n for {{ you }}"
    PARAMS = {"you": "me"}
    MESSAGE = "Here is a text message \n\n for me"
    PREVIEW = "Here is a text message <br/><br/> for me"

    def test_send_message(self):
        message = Backend.build_message("", self.TEXT, self.PARAMS, [])
        with patch("requests.post", side_effect=mocked_requests_post):
            webhook = (
                "https://hooks.slack.com/services/T07US72AH/"
                "B91UK823W/bzJGakQaBMDqM7LFC8apWbdB"
            )
            bad_address = (
                "https://hooks.slac.com/services/T07US72AH/"
                "B91UK823W/bzJGakQaBMDqM7LFC8apWbdB"
            )
            instance = Backend()
            import requests

            with self.assertRaises(requests.HTTPError):
                instance.send_message("", [bad_address], message)
            instance.send_message("", [webhook], message)

            assert 2 == len(requests.post.mock_calls)
            call_args = requests.post.mock_calls[1][2]

            assert (
                '{"text": "Here is a text message \\n\\n for me"}' == call_args["data"]
            )
            assert "application/json" == call_args["headers"]["Content-Type"]
