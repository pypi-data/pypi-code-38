# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FileConfig(AppConfig):
    name = 'aparnik.packages.shops.files'
    verbose_name = _('File')
