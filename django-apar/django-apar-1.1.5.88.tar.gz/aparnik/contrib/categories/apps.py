# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CategoryConfig(AppConfig):
    name = 'aparnik.contrib.categories'
    verbose_name = _('Categories')
