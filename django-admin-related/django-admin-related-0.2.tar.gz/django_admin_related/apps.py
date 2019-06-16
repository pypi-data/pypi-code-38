# -*- coding: utf-8 -*-
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DjangoAdminRelatedConfig(AppConfig): # Our app config class
    name = 'django_admin_related'
    verbose_name = _('Django Admin Related')