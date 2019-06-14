import django.apps
from django.db import models
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver
from filelock import FileLock

from acmin.utils import attr
from .base import AcminModel
from .group import Group
from .user import User

lock = FileLock("contenttype.lock")
lock.release(force=True)

cache = dict()


@receiver(post_save)
@receiver(post_delete)
def handle_model_change(sender, **kwargs):
    if sender in [ContentType, GroupContentType, UserContentType]:
        with lock:
            cache.clear()


def init_contenttype():
    from acmin.models import ContentType, AcminModel
    contenttypes = {}
    for contenttype in ContentType.objects.all():
        contenttypes[contenttype.app + "-" + contenttype.name] = contenttype
    all_models = {}
    for model in [model for model in django.apps.apps.get_models() if issubclass(model, AcminModel)]:
        app = model.__module__.split(".")[0]
        name = model.__name__
        all_models[app + "-" + name] = model

    type_map = {}
    for flag, model in all_models.items():
        contenttype = contenttypes.get(flag)
        verbose_name = model._meta.verbose_name
        if contenttype:
            if contenttype.verbose_name != verbose_name:
                contenttype.verbose_name = verbose_name
                contenttype.save()
        else:
            app, name = flag.split("-")
            contenttype = ContentType.objects.create(app=app, name=name, verbose_name=verbose_name)
        type_map[model] = contenttype
    for flag, contenttype in contenttypes.items():
        if flag not in all_models:
            contenttype.delete()

    return type_map


def get_map():
    from collections import defaultdict
    if not cache:
        with lock:
            contenttypes = {contenttype.get_key(): contenttype for contenttype in ContentType.objects.all()}
            cache['contenttypes'] = contenttypes
            cache['models'] = {model.get_contenttype_key(): model for model in django.apps.apps.get_models() if
                               issubclass(model, AcminModel)}

            group_contenttypes = defaultdict(dict)
            for c in GroupContentType.objects.all():
                group_contenttypes[str(c.group.id)][c.get_key()] = c
            cache['group_contenttypes'] = group_contenttypes

            user_contenttypes = defaultdict(dict)
            for c in UserContentType.objects.all():
                user_contenttypes[str(c.user.id)][c.get_key()] = c
            cache['user_contenttypes'] = group_contenttypes

    return cache


@receiver(post_save)
@receiver(post_delete)
def clear_map(sender, **kwargs):
    if sender in [Group, User] or issubclass(sender, BaseContentType):
        with lock:
            cache.clear()


class BaseContentType(AcminModel):
    class Meta:
        abstract = True

    verbose_name = models.CharField("描述", max_length=100)
    sequence = models.IntegerField("排序", default=100)
    app = models.CharField("应用", max_length=100)
    name = models.CharField("名称", max_length=100)

    def __str__(self):
        return self.verbose_name

    @classmethod
    def get(cls, app, name):
        return cls.get_by_key(f"{app}.{name}")

    @classmethod
    def get_by_user_and_model(cls, user, model):
        cache = get_map()
        key = model.get_contenttype_key()
        return attr(cache, f'user_contenttypes.{user.id}.{key}') or attr(cache, f'group_contenttypes.{user.group_id}.{key}') or attr(cache, f'contenttypes.{key}')

    @classmethod
    def get_by_model(cls, model):
        return get_map()['contenttypes'][model.get_contenttype_key()]

    def get_model(self):
        return get_map()['models'][self.get_key()]

    def get_key(self):
        return self.app + "_" + self.name

    @classmethod
    def get_by_key(cls, key):
        print(key)
        return get_map()['contenttypes'][key]

    @classmethod
    def get_model_by_key(cls, key):
        return get_map()['models'][key]


class ContentType(BaseContentType):
    class Meta:
        ordering = ['sequence', "id"]
        verbose_name_plural = verbose_name = "模型"
        unique_together = [("app", "name")]


class GroupContentType(BaseContentType):
    class Meta:
        ordering = ['group', 'sequence']
        verbose_name_plural = verbose_name = "模型(用户组)"
        unique_together = ("group", "app", "name")

    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class UserContentType(BaseContentType):
    class Meta:
        ordering = ['user', 'sequence']
        verbose_name_plural = verbose_name = "模型(用户)"
        unique_together = ("user", "app", "name")

    user = models.ForeignKey(User, on_delete=models.CASCADE)
