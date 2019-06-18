#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:denishuang

from __future__ import unicode_literals

from django.utils.module_loading import autodiscover_modules

from django.apps import AppConfig
from rest_framework import serializers

class Config(AppConfig):
    name = 'django_szuprefix.api'
    label = 'api'
    verbose_name = 'api'

    def ready(self):
        super(Config, self).ready()
        from django_szuprefix.utils import modelutils
        serializers.ModelSerializer.serializer_field_mapping.update({modelutils.JSONField: serializers.JSONField})
        self.autodiscover()


    def autodiscover(self):
        # print "autodiscover"
        autodiscover_modules('apis')

