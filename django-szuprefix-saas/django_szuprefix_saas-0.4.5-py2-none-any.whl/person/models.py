# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_szuprefix_saas.saas.models import Party
from . import choices
from django.contrib.auth.models import User


class Person(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "个人"

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, null=True, related_name="persons")
    user = models.OneToOneField(User, verbose_name=User._meta.verbose_name, null=True, related_name="as_person")
    name = models.CharField("名字", max_length=64, db_index=True)
    gender = models.CharField("性别", max_length=1, choices=choices.CHOICES_GENDER, default=choices.GENDER_UNDEFINED)
    mobile = models.CharField("手机", max_length=64, db_index=True, null=True, blank=True)
    email = models.CharField("邮箱", max_length=64, db_index=True, null=True, blank=True)
    id_card = models.CharField("身份证", max_length=18, db_index=True, null=True, blank=True)
    birth_date = models.DateField("生日", null=True, blank=True)
    city = models.CharField("城市", max_length=128, null=True, blank=True, db_index=True)
    address = models.CharField("地址", max_length=256, null=True, blank=True)
    ethnic = models.CharField("民族", max_length=64, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    settings = GenericRelation("common.Setting")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.party = self.user.as_saas_worker.party
        return super(Person, self).save(**kwargs)

    def age(self):
        from django_szuprefix.utils import dateutils
        return self.birth_date and dateutils.get_age(self.birth_date)

    age.short_description = "年龄"
