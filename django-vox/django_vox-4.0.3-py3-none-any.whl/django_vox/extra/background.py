import warnings

from django.apps import apps
from django.contrib.contenttypes.models import ContentType

import django_vox.models


class BackgroundVoxModel(django_vox.models.VoxModel):
    """
    A vox model that sends its calls though a background task
    """

    class Meta:
        abstract = True

    def issue_notification(self, codename: str, target=None, actor=None):
        warnings.warn(
            "BackgroundVoxModel is deprecated and will be removed in "
            "django-vox 5.0. It has been replaced by setting "
            "DJANGO_VOX_ISSUE_METHOD to "
            "'django_vox.extra.background_tasks.issue'."
        )

        kwargs = {}
        self_cls_str = str(self.__class__._meta)
        if target is not None:
            kwargs["target_cls_str"] = str(target.__class__._meta)
            kwargs["target_id"] = target.pk
        if actor is not None:
            kwargs["actor_cls_str"] = str(actor.__class__._meta)
            kwargs["actor_id"] = actor.pk
        issue_notification(codename, self_cls_str, self.pk, **kwargs)


def issue_notification(
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
    notification.issue(obj, actor=actor, target=target)


try:
    from background_task import background

    issue_notification = background(queue="django-vox")(issue_notification)
except ImportError:
    pass
except RuntimeError:
    pass
