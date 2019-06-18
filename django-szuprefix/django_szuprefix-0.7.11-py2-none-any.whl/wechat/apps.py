# -*- coding:utf-8 -*-
from django.apps import AppConfig
from django.conf import settings

__author__ = 'denishuang'


class Config(AppConfig):
    name = "django_szuprefix.wechat"
    verbose_name = u"微信"

    def ready(self):
        super(Config, self).ready()
        from . import receivers


MP = settings.WECHAT.get("MP", {})
