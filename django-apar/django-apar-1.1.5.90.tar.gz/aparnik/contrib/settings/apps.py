# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class SettingsConfig(AppConfig):
    name = 'aparnik.contrib.settings'
    verbose_name = _('settings')
