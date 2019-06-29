# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class PaymentConfig(AppConfig):
    name = 'aparnik.packages.shops.payments'
    verbose_name = _('payment')
