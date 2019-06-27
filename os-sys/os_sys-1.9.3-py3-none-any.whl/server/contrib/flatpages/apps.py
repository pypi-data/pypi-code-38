from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class FlatPagesConfig(AppConfig):
    name = 'server.contrib.flatpages'
    verbose_name = _("Flat Pages")
