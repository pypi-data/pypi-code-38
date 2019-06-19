# -*- coding: utf-8 -*-

from __future__ import unicode_literals

from aldryn_apphooks_config.app_base import CMSConfigApp
from cms.apphook_pool import apphook_pool
from django.utils.translation import ugettext_lazy as _

from .models import Dashboards_appConfig


class Dashboards_appApp(CMSConfigApp):
    name = _('Dashboards')
    app_name = 'dashboards_app'
    app_config = Dashboards_appConfig

    def get_urls(self, *args, **kwargs):
        return ['dashboards_app.urls']

    # NOTE: Please do not add a «menu» here, menu’s should only be added by at
    # the discretion of the operator.


apphook_pool.register(Dashboards_appApp)
