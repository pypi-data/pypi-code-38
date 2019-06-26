import json

from django.test import TestCase

import django_vox.backends.template_email


class TestTemplateEmailBackend(TestCase):

    TEXT = (
        "{% block text_body%}"
        "Here is a message \n\n for {{ you }}"
        "{% endblock %}"
        "{% block html_body %}"
        "<p>Here is a message <br/><br/> for {{ you }}"
        "{% endblock %}"
        ""
    )
    PARAMS = {"you": "me"}
    SUBJECT = "SUBJECT"
    MESSAGE = {
        "subject": "SUBJECT",
        "text": "Here is a message \n\n for me",
        "html": "<p>Here is a message <br/><br/> for me",
    }
    PREVIEW = "<p>Here is a message <br/><br/> for me"

    @classmethod
    def test_build_message(cls):
        backend = django_vox.backends.template_email.Backend
        message = backend.build_message(cls.SUBJECT, cls.TEXT, cls.PARAMS, [])
        obj = json.loads(message)
        assert cls.MESSAGE == obj

    @classmethod
    def test_preview_message(cls):
        backend = django_vox.backends.template_email.Backend
        message = backend.preview_message(cls.SUBJECT, cls.TEXT, cls.PARAMS)
        assert cls.PREVIEW == message
