from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class LogConfig(AppConfig):
    name = 'bigtiger.contrib.log'
    verbose_name = _("Log")

    def ready(self):
        import bigtiger.contrib.log.handlers
