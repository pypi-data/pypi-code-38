# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class CouponsConfig(AppConfig):
    name = 'aparnik.packages.shops.coupons'
    verbose_name = _('coupons')

