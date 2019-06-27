from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class SessionsConfig(AppConfig):
    name = 'server.contrib.sessions'
    verbose_name = _("Sessions")
