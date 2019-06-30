# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AuditsConfig(AppConfig):
    name = 'aparnik.contrib.audits'
    verbose_name = _('Audits')
