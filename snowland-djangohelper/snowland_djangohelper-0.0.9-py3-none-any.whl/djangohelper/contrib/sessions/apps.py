from djangohelper.apps import AppConfig
from djangohelper.utils.translation import gettext_lazy as _


class SessionsConfig(AppConfig):
    name = 'djangohelper.contrib.sessions'
    verbose_name = _("Sessions")
