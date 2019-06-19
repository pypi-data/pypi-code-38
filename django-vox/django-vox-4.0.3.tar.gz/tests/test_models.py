import datetime
import warnings

import aspy
import pytz
from bs4 import BeautifulSoup
import django.contrib.auth.models as auth_models
from django.contrib.contenttypes.models import ContentType
from django.core import mail
from django.test import Client, TestCase

import django_vox.models
import django_vox.registry

from . import models


class FailmailTests(TestCase):

    fixtures = ["test"]

    def test_email_failure(self):
        assert 0 == len(mail.outbox)
        author = auth_models.User.objects.get(email="author@example.org")
        # by default, with the test config, we throw errors
        with self.settings(EMAIL_BACKEND="Can't import this!"):
            with self.assertRaises(ImportError):
                models.Article.objects.create(
                    slug="second",
                    author=author,
                    title="A second article",
                    content="Whoever thought we'd come this far",
                )
        assert 0 == len(mail.outbox)
        assert 3 == django_vox.models.FailedMessage.objects.count()
        # we can change that though
        with self.settings(
            DJANGO_VOX_THROW_EXCEPTIONS=False, EMAIL_BACKEND="Can't import this!"
        ):
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                models.Article.objects.create(
                    slug="third",
                    author=author,
                    title="A third article",
                    content="Whoever thought we'd come this far",
                )
            # this should create 3 failed messages
            assert 0 == len(mail.outbox)
            messages = django_vox.models.FailedMessage.objects.order_by("created_at")
            assert 6 == len(messages)
            # ends with date
            for message in messages:
                assert "@example.org @ " in str(message)

    def test_email_fail_resend(self):
        with self.settings(
            DJANGO_VOX_THROW_EXCEPTIONS=False, EMAIL_BACKEND="Can't import this!"
        ):
            assert 0 == len(mail.outbox)
            author = auth_models.User.objects.get(email="author@example.org")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                models.Article.objects.create(
                    slug="second",
                    author=author,
                    title="A second article",
                    content="Whoever thought we'd come this far",
                )
            # this should create 3 failed messages
            messages = django_vox.models.FailedMessage.objects.order_by("created_at")
            assert 3 == len(messages)
            for message in messages:
                assert "@example.org @ " in str(message)
            # try resending the first one (to admin)
            with self.assertRaises(Exception):
                messages[0].resend()

        messages = django_vox.models.FailedMessage.objects.order_by("created_at")
        messages[0].resend()
        assert 1 == len(mail.outbox)


class ExtraOptionsTest(TestCase):
    """Test extra notification template options"""

    fixtures = ["test"]

    @staticmethod
    def test_from_address():
        assert len(mail.outbox) == 0
        # get the article created template
        template = django_vox.models.Template.objects.get(pk=1)
        template.from_address = "{{ object.author.email }}"
        template.save()
        # disable message to site contact
        template = django_vox.models.Template.objects.get(pk=2)
        template.enabled = False
        template.save()
        # first we create an article as the author user
        author = auth_models.User.objects.get(email="author@example.org")
        models.Article.objects.create(
            slug="another",
            author=author,
            title="Just another article",
            content="nothing really matters ... to me",
        )
        assert len(mail.outbox) == 2
        for message in mail.outbox:
            assert message.from_email == "author@example.org"


class DemoTests(TestCase):
    """Test the walkthrough in the documentation"""

    fixtures = ["test"]

    @staticmethod
    def test_walkthrough():
        # sanity
        assert len(mail.outbox) == 0
        # first we create an article as the author user
        author = auth_models.User.objects.get(email="author@example.org")
        models.Article.objects.create(
            slug="second",
            author=author,
            title="A second article",
            content="Whoever thought we'd come this far",
        )
        # now a notification should be fired, check the outbox
        # mail.outbox is a list of EmailMultiAlternatives
        assert len(mail.outbox) == 3
        for message in mail.outbox:
            # ignore site message
            if "admin@example.org" in message.to:
                continue
            assert (
                message.content_subtype == "plain" and message.mixed_subtype == "mixed"
            )
            html = message.alternatives[0][0]
            soup = BeautifulSoup(html, "html.parser")
            anchors = soup.find_all("a")
            assert len(anchors) == 1
            url = anchors[0].get("href")
            assert url.startswith("http://127.0.0.1:8000/second/?token=")
            assert len(url) > 31  # if less, token is blank
            client = Client()
            response = client.get(url)
            assert response.status_code == 200
            assert response["Content-Type"] == "text/html; charset=utf-8"

    @staticmethod
    def test_markdown():
        # sanity
        assert len(mail.outbox) == 0
        # get the article created template
        template = django_vox.models.Template.objects.get(pk=1)
        template.backend = "email-md"
        template.subject = "Hi {{ recipient.name }}"
        template.content = (
            "Hi {{ recipient.name }},\n\nA new article, "
            "[{{ object }}](http://127.0.0.1:8000/{{ "
            "object.pk }}/?token={{ recipient.get_token | "
            "urlencode }}), has been published at the "
            "awesome blog."
        )
        template.save()
        # first we create an article as the author user
        author = auth_models.User.objects.get(email="author@example.org")
        models.Article.objects.create(
            slug="second",
            author=author,
            title="A second article",
            content="Whoever thought we'd come this far",
        )
        # now a notification should be fired, check the outbox
        # mail.outbox is a list of EmailMultiAlternatives
        assert len(mail.outbox) == 3
        mail_by_subject = {}
        for message in mail.outbox:
            mail_by_subject[message.subject] = message
        site_mail = mail_by_subject["Hi Subscriber"]
        assert len(site_mail.alternatives) == 1
        soup = BeautifulSoup(site_mail.alternatives[0][0], "html.parser")
        assert len(site_mail.attachments) == 1
        assert site_mail.attachments[0][2] == "text/vcard"
        assert "FN:Author" in site_mail.attachments[0][1]
        anchors = soup.find_all("a")
        assert len(anchors) == 1
        url = anchors[0].get("href")
        assert url.startswith("http://127.0.0.1:8000/second/?token=")
        assert len(url) > 31  # if less, token is blank

    @staticmethod
    def test_choices():
        """
        Test the values of the dropdown fields
        """
        expected_ids = set()
        for model in (
            models.Article,
            models.Subscriber,
            auth_models.User,
            auth_models.Group,
            models.Comment,
            django_vox.models.SiteContact,
            models.Thing,
        ):
            ct = ContentType.objects.get_for_model(model)
            expected_ids.add(ct.id)

        vox_ct_limit = django_vox.registry.channel_type_limit()
        assert "id__in" in vox_ct_limit
        actual_ids = set(vox_ct_limit["id__in"])
        assert expected_ids == actual_ids

    @staticmethod
    def test_previews():
        pp = django_vox.models.PreviewParameters(
            models.Article, auth_models.User, models.Subscriber
        )
        assert "recipient" not in pp
        assert "target" in pp
        assert pp["content"].title == "Why are there so many blog demos"
        assert pp["object"].title == "Why are there so many blog demos"
        assert pp["target"].name == "Subscriber"
        assert pp["actor"].get_full_name() == "Author"
        # now delete the articles and watch it come up with names
        for article in models.Article.objects.all():
            article.delete()
        for sub in models.Subscriber.objects.all():
            sub.delete()
        pp = django_vox.models.PreviewParameters(
            models.Article, auth_models.User, models.Subscriber
        )
        assert "recipient" not in pp
        assert "target" in pp
        assert pp["object"].title == "{title}"
        assert pp["target"].secret == ""
        assert pp["actor"].get_full_name() == "Author"


class TestTemplate(TestCase):

    fixtures = ["test"]

    def test_str(self):
        template = django_vox.models.Template.objects.get(pk=1)
        assert "Email (HTML) for Subscribers" == str(template)


class TestDescriptorChannels(TestCase):

    fixtures = ["test"]

    def test_descriptor_channels(self):
        """
        There are 6 different ways that relations can work, tests there all here
        """
        thingthing_names = ("thing1", "thing2", "thing3", "thing4", "thing5", "thing6")
        # create_one to one channels
        thing1 = models.Thing1.objects.create(email="thing1@test")
        thing2 = models.Thing2.objects.create(email="thing2@test")
        thing3 = models.Thing3.objects.create(email="thing3@test")
        thing = models.Thing.objects.create(thing1=thing1, thing2=thing2)
        thing.thing3.add(thing3)
        models.Thing4.objects.create(thing=thing, email="thing4@test")
        models.Thing5.objects.create(thing=thing, email="thing5@test")
        thing6 = models.Thing6.objects.create(email="thing6@test")
        thing6.thing.add(thing)

        ct = ContentType.objects.get_for_model(thing)
        notification = django_vox.models.Notification.objects.create(
            codename="one_to_one", object_type=ct, description="foo", from_code=False
        )
        for name in thingthing_names:
            django_vox.models.Template.objects.create(
                notification=notification,
                backend="email-html",
                subject=name,
                recipients="c:{}".format(name),
            )

        assert 0 == len(mail.outbox)
        notification.issue(thing)
        assert 6 == len(mail.outbox)


def test_load_aspy_object():
    json = (
        "{\n"
        '"@context": "https://www.w3.org/ns/activitystreams",\n'
        '"type": "Create",\n'
        '"object": {\n'
        '  "type": "Note",\n'
        '  "updated": "2018-11-14T06:47:34Z",\n'
        '  "summary": "Here’s a note"\n'
        "}\n"
        "}"
    )
    obj = django_vox.models.load_aspy_object(json)
    assert isinstance(obj["object"], aspy.Note)
    assert obj["object"]["updated"] == datetime.datetime(
        2018, 11, 14, 6, 47, 34, tzinfo=pytz.utc
    )


def test_one_time_notification():
    """
    Test random fields on OneTimeNotification

    These don't normally get called, but we want to make sure
    they have reasonable values
    """
    n = django_vox.models.OneTimeNotification
    assert "<OneTimeNotification>" == str(n)
    assert None is n.object_type
    assert None is n.actor_type
    assert None is n.target_type
    assert ("", "", "") == n.natural_key()
    assert None is n.get_object_model()
    assert None is n.get_actor_type()
    assert None is n.get_target_type()
    assert aspy.Create == n.get_activity_type()
    assert {} == n.get_recipient_variables()
