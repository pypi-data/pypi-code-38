from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import models as auth_models
from django.test import TestCase

import tests.models
from django_vox.management.commands import make_notifications
from django_vox.models import Notification, Template


class MakeNotificationTests(TestCase):
    @staticmethod
    def test_kill_orphans():
        """If you completely remove a class,
        its notification should get deleted."""
        cmd = make_notifications.Command()
        cmd.handle(verbosity=0)
        assert 8 == Notification.objects.all().count()
        # simulate a deleted class
        fake_ct = ContentType.objects.create(app_label="blarg", model="deleted")
        Notification.objects.create(codename="foo", object_type=fake_ct, from_code=True)
        assert 9 == Notification.objects.all().count()
        cmd.handle(verbosity=0)
        assert 8 == Notification.objects.all().count()

    @staticmethod
    def test_keep_orphans_with_templates():
        cmd = make_notifications.Command()
        cmd.handle(verbosity=0)
        assert 8 == Notification.objects.all().count()
        # simulate a deleted class
        fake_ct = ContentType.objects.create(app_label="django_vox", model="deleted")
        notification = Notification.objects.create(
            codename="foo", object_type=fake_ct, from_code=True
        )
        Template.objects.create(
            notification=notification, subject="subject", content="content"
        )
        cmd.handle(verbosity=0)

    @staticmethod
    def test_keep():
        """Make sure we keep notifications with the same IDs
        even if they have no templates"""
        cmd = make_notifications.Command()
        cmd.handle(verbosity=0)
        ids = set(v["id"] for v in Notification.objects.values("id"))
        assert 8 == len(ids)
        notification = Notification.objects.all()[0]
        Template.objects.filter(notification=notification).delete()
        cmd.handle(verbosity=0)
        second_ids = set(v["id"] for v in Notification.objects.values("id"))
        assert ids == second_ids

    @staticmethod
    def test_make_notifications():
        cmd = make_notifications.Command()
        assert 0 == Notification.objects.all().count()
        # dry run
        cmd.handle(dry_run=True)
        assert 0 == Notification.objects.all().count()
        # test basic notification making
        cmd.handle(verbosity=0)
        # now we should have the 3 signal notifications on user & subscriber
        # and the article created and comment created notifications
        assert 8 == Notification.objects.all().count()
        # gather some general things
        article_ct = ContentType.objects.get_for_model(tests.models.Article)
        user_ct = ContentType.objects.get_for_model(auth_models.User)

        # make a notification to delete
        Notification.objects.create(
            codename="foo", object_type=article_ct, from_code=True
        )
        assert 9 == Notification.objects.all().count()
        cmd.handle()
        assert 8 == Notification.objects.all().count()
        # here's one that shouldn't get deleted
        Notification.objects.create(
            codename="foo", object_type=article_ct, from_code=False
        )
        assert 9 == Notification.objects.all().count()
        cmd.handle()
        assert 9 == Notification.objects.all().count()
        # now we'll change one and it should get reverted
        acn = Notification.objects.get_by_natural_key("tests", "article", "created")
        acn.object_model = user_ct
        acn.save()
        cmd.handle(verbosity=0)
        acn = Notification.objects.get_by_natural_key("tests", "article", "created")
        assert acn.actor_type is not None
