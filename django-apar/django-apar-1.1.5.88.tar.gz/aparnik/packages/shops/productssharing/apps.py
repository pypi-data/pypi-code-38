# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ProductSharingConfig(AppConfig):
    name = 'aparnik.packages.shops.productssharing'
    verbose_name = _('Product Sharing')
