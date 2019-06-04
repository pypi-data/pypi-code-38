# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

from django_szuprefix_saas.saas.models import Party
from django_szuprefix.utils import lbsutils

__author__ = 'denishuang'

from django.contrib.auth.models import User
from django.db import models


class Signin(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = "签到"
        ordering = ('-create_time',)

    party = models.ForeignKey(Party, verbose_name=Party._meta.verbose_name, related_name="signins", null=True, on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, related_name="signins",
                             on_delete=models.PROTECT)

    content_type = models.ForeignKey(ContentType, on_delete=models.PROTECT)
    object_id = models.PositiveIntegerField()
    context = GenericForeignKey('content_type', 'object_id')
    longitude = models.FloatField("经度")
    latitude = models.FloatField("纬度")
    city = models.CharField("城市", max_length=128, null=True, blank=True, db_index=True)
    address = models.CharField("地址", max_length=256, null=True, blank=True)
    create_time = models.DateTimeField("创建时间", auto_now_add=True, db_index=True)

    def __unicode__(self):
        return "%s %s 签到于 %s" % (self.create_time.isoformat(), self.user, self.place)

    def save(self, **kwargs):
        if self.party is None:
            self.party = self.user.as_saas_worker.party
        if self.city is None:
            self.city = " ".join(lbsutils.get_place_province_and_city(self.address))
        if self.context is None:
            self.context = self.user
        return super(Signin, self).save(**kwargs)
