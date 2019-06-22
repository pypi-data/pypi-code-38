# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PageConfig(AppConfig):
    name = 'aparnik.contrib.pages'
    verbose_name = _('Page')
