from django.contrib.auth.models import AbstractUser
from django.db import models

from .base import AcminModel
from .group import Group


class User(AbstractUser, AcminModel):
    class Meta:
        verbose_name_plural = verbose_name = "用户"

    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    title = models.CharField('名称', max_length=50, blank=False, null=False)

    def __str__(self):
        return self.title
