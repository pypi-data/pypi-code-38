from django.apps import apps
from django.contrib.contenttypes.models import ContentType

import django_vox.models

from background_task import background


def issue(notification, obj, *, actor=None, target=None):

    kwargs = {}
    self_cls_str = str(obj.__class__._meta)
    if actor is not None:
        kwargs["actor_cls_str"] = str(actor.__class__._meta)
        kwargs["actor_id"] = actor.pk
    if target is not None:
        kwargs["target_cls_str"] = str(target.__class__._meta)
        kwargs["target_id"] = target.pk
    delayed_issue(notification.codename, self_cls_str, obj.pk, **kwargs)


@background(queue="django-vox")
def delayed_issue(
    codename: str,
    object_cls_str: str,
    object_id: int,
    target_cls_str: str = "",
    target_id: int = 0,
    actor_cls_str: str = "",
    actor_id: int = 0,
):
    object_model = apps.get_model(object_cls_str)
    obj = object_model.objects.get(pk=object_id)
    object_ct = ContentType.objects.get_for_model(obj)

    target = None
    if target_cls_str != "":
        model = apps.get_model(target_cls_str)
        target = model.objects.get(pk=target_id)
    actor = None
    if actor_cls_str != "":
        model = apps.get_model(actor_cls_str)
        actor = model.objects.get(pk=actor_id)

    notification = django_vox.models.Notification.objects.get(
        codename=codename, object_type=object_ct
    )
    notification.issue_now(obj, actor=actor, target=target)
