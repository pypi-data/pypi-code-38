# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django import apps
from django.conf import settings

from . import default_settings


class AppConfig(apps.AppConfig):
    name = 'rest_auth'

    def _is_my_setting(self, name):
        return name.startswith(default_settings.prefix)

    def ready(self):
        # enroll default settings to django.conf.settings
        for name in filter(self._is_my_setting, dir(default_settings)):
            if not hasattr(settings, name):
                setattr(settings, name, getattr(default_settings, name))
            else:  # pragma: no cover
                # NOTE if settings has `REST_AUTH_*`, do nothing.
                pass

        return super(AppConfig, self).ready()
