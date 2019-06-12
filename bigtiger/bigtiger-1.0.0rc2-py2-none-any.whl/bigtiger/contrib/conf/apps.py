# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import SimpleLazyObject
from django.conf import settings

from .handlers import get_config


def get_online_config(self):
    if not hasattr(self, '_cached_online_config'):
        config = get_config()
        self._cached_online_config = config

    return self._cached_online_config


class OnlineConfig(AppConfig):
    name = 'bigtiger.contrib.conf'
    verbose_name = _("OnlineConf")

    def ready(self):
        online_config = SimpleLazyObject(lambda: get_online_config(self))
        setattr(settings, 'ONLINE', online_config)
