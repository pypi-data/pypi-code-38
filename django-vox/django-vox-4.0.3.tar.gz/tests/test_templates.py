import datetime

from django.template import TemplateSyntaxError
from django.test import TestCase

from django_vox import models
from django_vox.backends import base_email, markdown_email, template_email


class MultipartMessageTests(TestCase):
    @staticmethod
    def test_all():
        mpm_dict = {
            "subject": "foo",
            "text": "A message about foo",
            "html": "A <blink>message</blink> about foo",
        }
        mpm = base_email.MultipartMessage.from_dict(mpm_dict)
        new_dict = mpm.to_dict()
        assert new_dict == mpm_dict
        serialized = str(mpm)
        new_mpm = base_email.MultipartMessage.from_string(serialized)
        assert new_mpm.subject == mpm.subject
        assert new_mpm.text == mpm.text
        assert new_mpm.html == mpm.html
        # test to mail with both text & html
        mail = mpm.to_mail()
        assert mail.body == mpm_dict["text"]
        assert mail.subject == mpm_dict["subject"]
        assert len(mail.alternatives) == 1
        content, mime = mail.alternatives[0]
        assert content == mpm_dict["html"]
        assert mime == "text/html"
        # test to mail with text only
        mpm.html = ""
        mail = mpm.to_mail()
        assert mail.content_subtype == "plain"
        assert mail.body == mpm_dict["text"]
        # test to mail with html only
        mpm.html = mpm_dict["html"]
        mpm.text = ""
        mail = mpm.to_mail()
        assert mail.content_subtype == "html"
        assert mail.body == mpm_dict["html"]


class TemplateRender(TestCase):
    @staticmethod
    def test_blank():
        assert "" == models.Template(content="").render({})

    @staticmethod
    def test_non_html():
        template = models.Template(content="{{ param }}")
        assert "A&W" == template.render({"param": "A&W"}, autoescape=False)

    @staticmethod
    def test_html():
        template = models.Template(content="{{ param }}")
        assert "A&amp;W" == template.render({"param": "A&W"})

    def test_syntax_error(self):
        template = models.Template(content='{% extends "%}')
        self.assertRaises(TemplateSyntaxError, lambda: template.render({}))

    @staticmethod
    def test_syntax_bad_format():
        template = models.Template(content="{{ }")
        assert "{{ }" == template.render({"param": "A&W"})

    @staticmethod
    def test_param_missing():
        template = models.Template(content="{{ param }}")
        assert "" == template.render({})


class EmailRenderTests(TestCase):
    @staticmethod
    def test_no_parts():
        params = {"message": "There's a new burger at A&W"}
        email = "Hi, John Doe, here is a message: {{ message }}"
        text = "Hi, John Doe, here is a message: There's a new burger at A&W"
        result = template_email.email_parts("", email, params)
        assert result.subject == ""
        assert result.text == text

    @staticmethod
    def test_basic():
        params = {"message": "There's a new burger at A&W"}
        email = """{% block subject %}Test subject{% endblock %}
        {% block text_body %}
        Hi, John Doe, here is a message: {{ message }}
        {% endblock %}
        {% block html_body %}
        <p>Hi, John Doe, here is a message: {{ message }}</p>
        {% endblock %}
        """
        text = "Hi, John Doe, here is a message: There's a new burger at A&W"
        html = (
            "<p>Hi, John Doe, here is a message: "
            "There&#39;s a new burger at A&amp;W</p>"
        )
        result = template_email.email_parts("", email, params)
        assert result.subject == "Test subject"
        assert result.text == text
        assert result.html == html


class MarkdownEmailRenderTests(TestCase):
    @staticmethod
    def test_basic():
        params = {
            "firstname": "Jon",
            "lastname": "Doe",
            "message": "There's a *new* burger at A&W",
            "when": datetime.datetime(2013, 3, 12),
        }
        subject = "Hey {{ firstname }}"
        body = (
            "Hi {{ firstname }} {{ lastname}},\n\n"
            "Here is a message: {{ message }} starting "
            '{{ when | date:"SHORT_DATE_FORMAT" }}'
        )
        text = (
            "Hi Jon Doe,\n\n"
            "Here is a message: There's a *new* burger at A&W "
            "starting 03/12/2013"
        )
        html = (
            "<p>Hi Jon Doe,</p>\n\n"
            "<p>Here is a message: There&#8217;s a *new* burger "
            "at A&amp;W starting 03/12/2013</p>\n"
        )
        result = markdown_email.email_md(subject, body, params)
        assert result.subject == "Hey Jon"
        assert result.text == text
        assert result.html == html
