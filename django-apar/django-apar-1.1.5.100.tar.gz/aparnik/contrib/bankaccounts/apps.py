# -*- coding: utf-8 -*-


from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class BankAccountConfig(AppConfig):
    name = 'aparnik.contrib.bankaccounts'
    verbose_name = _('Bank Accounts')
