# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CoursesConfig(AppConfig):
    name = 'aparnik.packages.educations.courses'
    verbose_name = _('courses')
