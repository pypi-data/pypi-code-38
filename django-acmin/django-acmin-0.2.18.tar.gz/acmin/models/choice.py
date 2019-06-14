import collections

import django.apps
from django.db import models
from filelock import FileLock

from acmin.utils import attr
from .base import AcminModel
from .field import Field

lock = FileLock("choice.lock")
lock.release(force=True)


def init_choices():
    with lock:
        news = []
        exists = collections.defaultdict(dict)
        for choice in Choice.objects.all():
            exists[choice.field][choice.value] = choice
        for model in django.apps.apps.get_models():
            if issubclass(model, AcminModel):
                for field in attr(model, '_meta.fields'):
                    choices = attr(field, "choices")
                    name = attr(field, "name")
                    if choices and name:
                        for value, title in choices:
                            f = Field.get_default_field(model, name)
                            if str(value) not in exists[f]:
                                news.append(Choice(field=f, value=str(value), title=title))
        if news:
            Choice.objects.bulk_create(news)


cache_lock = FileLock("choice_cache.lock")
cache_lock.release(force=True)

cache = collections.defaultdict(list)


def get_choices():
    if not cache:
        with cache_lock:
            for choice in Choice.objects.all():
                cache[choice.field].append(choice)

    return cache


class Choice(AcminModel):
    class Meta:
        ordering = ['field', "id"]
        verbose_name_plural = verbose_name = "选项"
        unique_together = [("field", "value")]

    field = models.ForeignKey(Field, on_delete=models.CASCADE, verbose_name="默认字段")
    value = models.CharField("值", max_length=100)
    title = models.CharField("标题", max_length=100)

    @classmethod
    def get_choices(cls, field):
        return get_choices()[field]

    def __str__(self):
        return f"{self.field.attribute},{self.value},{self.title}"
