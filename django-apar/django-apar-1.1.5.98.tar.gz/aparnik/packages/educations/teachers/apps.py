# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TeachersConfig(AppConfig):
    name = 'aparnik.packages.educations.teachers'
    verbose_name = _('Teachers')
