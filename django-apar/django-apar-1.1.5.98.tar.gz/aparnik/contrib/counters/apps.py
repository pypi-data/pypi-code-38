# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CountersConfig(AppConfig):
    name = 'aparnik.contrib.counters'
    verbose_name = _('Counters')
