from django.core import mail
from django.core.exceptions import ImproperlyConfigured
from django.test.utils import override_settings
import django.contrib.auth.models as auth_models
from django.test import TestCase

import django_vox.settings
import django_vox.models
import django_vox.registry

from . import models


def test_backend_defaults():
    with override_settings(DJANGO_VOX_BACKENDS=None):
        backends = django_vox.settings.BACKENDS
        # we should have all the backend dependencies installed for
        # testing purposes
        expected = [
            "django_vox.backends.markdown_email",
            "django_vox.backends.template_email",
            "django_vox.backends.twilio",
            "django_vox.backends.twitter",
            "django_vox.backends.xmpp",
        ]
        assert expected == backends


class IssueMethodTests(TestCase):

    fixtures = ["test"]

    def test_issue_method(self):
        acn = django_vox.models.Notification.objects.get_by_natural_key(
            "tests", "article", "created"
        )
        article = models.Article.objects.get(pk="too_many")
        user = auth_models.User.objects.get(pk=1)

        # first test the background issuing
        django_vox.models.get_issue_function.cache_clear()
        with override_settings(
            DJANGO_VOX_ISSUE_METHOD="django_vox.extra.background_tasks.issue"
        ):
            acn.issue(article, actor=user, target=article)
            from background_task.models import Task

            all_tasks = Task.objects.all()
            assert len(all_tasks) == 1
            task = all_tasks[0]
            assert task.queue == "django-vox"
            assert task.task_name == "django_vox.extra.background_tasks.delayed_issue"
            # now lets try to manually run the task
            from background_task.tasks import tasks

            assert 0 == len(mail.outbox)
            tasks.run_next_task("django-vox")
            assert 3 == len(mail.outbox)

        django_vox.models.get_issue_function.cache_clear()
        with override_settings(DJANGO_VOX_ISSUE_METHOD="invalid_method!!!"):
            with self.assertRaises(ImproperlyConfigured):
                acn.issue(article, actor=user, target=article)
