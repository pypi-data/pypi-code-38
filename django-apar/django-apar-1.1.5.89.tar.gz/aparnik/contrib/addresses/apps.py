# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AddressesConfig(AppConfig):
    name = 'aparnik.contrib.addresses'
    verbose_name = _('Addresses')
