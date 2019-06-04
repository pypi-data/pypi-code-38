# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models

from django_szuprefix_saas.saas.models import Party
from django.contrib.auth.models import User


class Company(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "公司"
    party = models.OneToOneField(Party, verbose_name=Party._meta.verbose_name,
                                     related_name="as_company")
    name = models.CharField("名称", max_length=128)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    settings = GenericRelation("common.Setting")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        self.name = self.party.name
        return super(Company, self).save(**kwargs)


class Staff(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "成员"

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="company_staffs")
    user = models.OneToOneField(User, verbose_name=User._meta.verbose_name, null=True, related_name="as_company_staff")
    name = models.CharField("名字", max_length=64, db_index=True)
    position = models.CharField("职位", max_length=64, null=True, blank=True)
    number = models.CharField("工号", max_length=64, null=True, blank=True)
    sign_date = models.DateField("入职日期", null=True, blank=True)
    work_start_date = models.DateField("上岗日期", null=True, blank=True)
    regular_start_date = models.DateField("转正日期", null=True, blank=True)
    quit_date = models.DateField("离职日期", null=True, blank=True)
    settings = GenericRelation("common.Setting")
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        worker = self.user.as_saas_worker
        self.name = worker.name
        return super(Staff, self).save(**kwargs)