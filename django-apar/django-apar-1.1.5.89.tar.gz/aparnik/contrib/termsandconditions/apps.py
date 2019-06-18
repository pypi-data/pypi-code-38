# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class TermsAndConditionsConfig(AppConfig):
    name = 'aparnik.contrib.termsandconditions'
    verbose_name = _('Terms And Conditions')
