# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BaseSegmentConfig(AppConfig):
    name = 'aparnik.contrib.segments'
    verbose_name = _('Base Segment')


