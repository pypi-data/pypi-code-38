# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PageConfig(AppConfig):
    name = 'page'
    verbose_name = _('컨텐츠 관리')

