# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class FileFieldsConfig(AppConfig):
    name = 'aparnik.contrib.filefields'
    label = 'filefields'
    verbose_name = _('File Fields')


