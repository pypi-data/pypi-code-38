# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class VouchersConfig(AppConfig):
    name = 'aparnik.packages.shops.vouchers'
    verbose_name = _('Vouchers')
