# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ContactUsConfig(AppConfig):
    name = 'aparnik.contrib.contactus'
    verbose_name = _('Contact us')
