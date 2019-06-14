import collections

from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from filelock import FileLock
from python_utils import converters

from .base import AcminModel
from .group import Group
from .user import User

locker = FileLock("config.lock")
locker.release(force=True)
cache = collections.defaultdict(dict)


@receiver(post_save)
@receiver(post_delete)
def handle_model_change(sender, **kwargs):
    if sender in [Group, User, Config, UserConfig, GroupConfig]:
        with locker:
            cache.clear()


def get_configs():
    if not cache:
        with locker:
            for user in User.objects.all():
                for config in Config.objects.all():
                    cache[user][config.name] = config.value
            for config in GroupConfig.objects.all():
                for user in User.objects.filter(group=config.group).all():
                    cache[user][config.name] = config.value

            for config in UserConfig.objects.all():
                cache[user][config.name] = config.value
    return cache


class BaseConfig(AcminModel):
    class Meta:
        abstract = True

    name = models.CharField('名称', max_length=50, unique=True)
    value = models.TextField("值")

    def __str__(self):
        return self.name

    @classmethod
    def get(cls, user, name, default=None):
        return get_configs()[user].get(name, default)

    @classmethod
    def get_int(cls, user, name, default=0):
        return converters.to_int(cls.get(user, name), default)

    @classmethod
    def get_bool(cls, user, name):
        return cls.get(user, name, "").upper() in ["TRUE", "1", "YES", "Y"]


class Config(BaseConfig):
    class Meta:
        verbose_name = verbose_name_plural = '配置'


class GroupConfig(BaseConfig):
    class Meta:
        verbose_name = verbose_name_plural = '配置(用户组)'

    group = models.ForeignKey(Group, on_delete=models.CASCADE)


class UserConfig(BaseConfig):
    class Meta:
        verbose_name = verbose_name_plural = '配置(用户)'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
