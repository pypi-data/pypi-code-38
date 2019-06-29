#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:denishuang

from __future__ import unicode_literals

from django.apps import AppConfig


class Config(AppConfig):
    name = 'django_szuprefix_saas.person'
    verbose_name = u'个人'

    def ready(self):
        super(Config, self).ready()
        from . import receivers