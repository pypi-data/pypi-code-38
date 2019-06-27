from server.apps import AppConfig
from server.contrib.staticfiles.checks import check_finders
from server.core import checks
from server.utils.translation import gettext_lazy as _


class StaticFilesConfig(AppConfig):
    name = 'server.contrib.staticfiles'
    verbose_name = _("Static Files")
    ignore_patterns = ['CVS', '.*', '*~']

    def ready(self):
        checks.register(check_finders, 'staticfiles')
