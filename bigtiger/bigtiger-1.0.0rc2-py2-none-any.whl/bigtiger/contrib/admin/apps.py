from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class AdminConfig(AppConfig):
    name = 'bigtiger.contrib.admin'
    verbose_name = _("Admin")
