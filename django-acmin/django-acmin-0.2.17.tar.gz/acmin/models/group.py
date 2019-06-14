from django.db import models

from .base import AcminModel


class Group(AcminModel):
    class Meta:
        verbose_name_plural = verbose_name = "用户组"

    name = models.CharField('名称', max_length=50)

    def __str__(self):
        return self.name
