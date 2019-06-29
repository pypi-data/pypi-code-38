#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:denishuang

from __future__ import unicode_literals

from django.apps import AppConfig


class Config(AppConfig):
    name = 'django_szuprefix.company'
    verbose_name = u'公司'

    def ready(self):
        super(Config, self).ready()
        # from . import receivers