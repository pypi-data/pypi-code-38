from djangohelper.apps import AppConfig
from djangohelper.contrib.staticfiles.checks import check_finders
from djangohelper.core import checks
from djangohelper.utils.translation import gettext_lazy as _


class StaticFilesConfig(AppConfig):
    name = 'djangohelper.contrib.staticfiles'
    verbose_name = _("Static Files")
    ignore_patterns = ['CVS', '.*', '*~']

    def ready(self):
        checks.register(check_finders, 'staticfiles')
