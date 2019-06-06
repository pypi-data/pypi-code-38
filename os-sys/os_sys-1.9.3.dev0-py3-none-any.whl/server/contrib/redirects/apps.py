from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class RedirectsConfig(AppConfig):
    name = 'server.contrib.redirects'
    verbose_name = _("Redirects")
