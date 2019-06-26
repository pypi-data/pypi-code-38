"""
Test a few features in the base backend that wouldn't normally get tested
"""
from django.test import TestCase
from django_vox.backends import base

messages = []


class Backend(base.Backend):

    ESCAPE_HTML = True


class TestTestBackend(TestCase):

    TEXT = "Here is a text message <br/><br/> for {{ you }}"
    PARAMS = {"you": "me"}
    MESSAGE = "Here is a text message <br/><br/> for me"
    PREVIEW = "Here is a text message <br/><br/> for me"

    @classmethod
    def test_build_message(cls):
        message = Backend.build_message("", cls.TEXT, cls.PARAMS, [])
        assert cls.MESSAGE == message

    @classmethod
    def test_preview_message(cls):
        message = Backend.preview_message("", cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message

    def test_from_address(self):
        assert "" == Backend.get_default_from_address()
