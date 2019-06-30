# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ManagementConfig(AppConfig):
    name = 'aparnik.contrib.managements'
    verbose_name = _('Managements')
