# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class UsersConfig(AppConfig):
    name = 'aparnik.contrib.users'
    label = 'aparnik_users'
    verbose_name = _('Users')
