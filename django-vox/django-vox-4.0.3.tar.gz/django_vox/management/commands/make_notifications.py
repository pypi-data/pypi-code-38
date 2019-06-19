"""
Creates permissions for all installed apps that need permissions.
"""
from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import DEFAULT_DB_ALIAS, router
from django.db.models import Model


from django_vox import registry


class Command(BaseCommand):
    help = "Creates notifications based on VoxMeta instances in classes"

    def add_arguments(self, parser):  # pragma: no cover
        parser.add_argument(
            "--dry-run",
            action="store_true",
            dest="dry_run",
            default=False,
            help="Don't actually make changes",
        )

    def handle(self, *args, verbosity=1, dry_run=False, **kwargs):
        make_notifications(verbosity=verbosity, dry_run=dry_run)


def make_notifications(verbosity=1, dry_run=False, using=DEFAULT_DB_ALIAS):
    try:
        contenttype_class = apps.get_model("contenttypes", "ContentType")
        notification_class = apps.get_model("django_vox", "Notification")
        template_class = apps.get_model("django_vox", "Template")
    except LookupError:
        return

    if not router.allow_migrate_model(using, notification_class):
        return

    # This will hold the notifications we're looking for as
    # (object_type, codename)
    searched_notifications = []
    # The code names and content types that should exist.

    object_types = set()
    for cls, obj_item in registry.objects.items():
        if issubclass(cls, Model):
            # Force looking up the content types in the current database
            # before creating foreign keys to them.
            object_type = contenttype_class.objects.db_manager(using).get_for_model(cls)
            object_types.add(object_type)
            for params in obj_item.registration.get_notifications():
                searched_notifications.append((object_type, params))

    # Find all the Notification that have a object_type for a model we're
    # looking for.  We don't need to check for code names since we already have
    # a list of the ones we're going to create.
    all_notifications = {}
    for item in notification_class.objects.using(using).all():
        all_notifications[(item.object_type_id, item.codename)] = item

    new_notifications = []
    for ct, params in searched_notifications:
        notification = all_notifications.get((ct.pk, params.codename))
        if notification is None:
            new_notifications.append(notification_class.from_scheme(params, ct))
        else:
            if not params.params_equal(notification):
                if verbosity > 0:
                    print("Altering notification '%s'" % notification)
                params.set_params(notification)
                if not dry_run:
                    notification.save()
            del all_notifications[(ct.pk, params.codename)]

    if verbosity > 0:
        for notification in new_notifications:
            print("Added notification '%s'" % notification)

    for notification in all_notifications.values():
        if not notification.from_code:
            continue
        templates = template_class.objects.filter(notification=notification)
        if templates.count() > 0:
            if verbosity > 0:
                print(
                    "Skipping removal of notification '%s' "
                    "still has templates" % notification
                )
            continue
        if verbosity > 0:
            print("Removing notification '%s'" % notification)
        if not dry_run:
            notification.delete(using=using)
    if not dry_run:
        notification_class.objects.using(using).bulk_create(new_notifications)
