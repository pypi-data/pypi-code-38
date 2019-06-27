from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class SyndicationConfig(AppConfig):
    name = 'server.contrib.syndication'
    verbose_name = _("Syndication")
