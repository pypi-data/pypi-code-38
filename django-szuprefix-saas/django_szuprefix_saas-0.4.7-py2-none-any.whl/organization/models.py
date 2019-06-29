# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericRelation
from django.db import models
from django_szuprefix_saas.saas.models import Party


class Organization(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "组织机构"

    party = models.OneToOneField(Party, verbose_name=Party._meta.verbose_name, related_name="as_organization")
    name = models.CharField("名称", max_length=128)
    brief_name = models.CharField("简称", max_length=128, blank=True)
    oibc = models.CharField("组织机构代码", max_length=10, null=True, blank=True)
    usci = models.CharField("统一社会信用代码", max_length=18, null=True, blank=True)
    logo = models.ImageField("logo", null=True, blank=True)
    establish_date = models.DateField("创立日期", null=True, blank=True)
    address = models.CharField("地址",  max_length=256, null=True, blank=True)
    website = models.CharField("网站",  max_length=256, null=True, blank=True)
    remark = models.CharField("备注", max_length=256, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True)
    modify_time = models.DateTimeField("修改时间", auto_now=True)
    settings = GenericRelation("common.Setting")

    def __unicode__(self):
        return self.name

    def save(self, **kwargs):
        if not self.name:
            self.name = self.party.name
        if not self.brief_name:
            self.brief_name = self.name
        return super(Organization, self).save(**kwargs)

