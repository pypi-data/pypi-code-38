# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.db import models
# from . import choices
from django.contrib.auth.models import User
from django_szuprefix_saas.utils.modelutils import JSONField

class Matcher(models.Model):
    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, null=True, related_name="ehtml_contents")
    matches = JSONField(u"提取规则", max_length=64, null=True, blank=True, help_text=u"""使用xpath, 例子:{"标题":["//div[@class='shiti']"],]}""")
    baseurl = models.CharField(u"URL", max_length=256, db_index=True)

class Content(models.Model):
    class Meta:
        verbose_name_plural = verbose_name = u"内容"

    user = models.ForeignKey(User, verbose_name=User._meta.verbose_name, null=True, related_name="ehtml_contents")
    name = models.CharField(u"名字", max_length=64, db_index=True)
    html = models.TextField(u"HTML")

    def __unicode__(self):
        return self.name
