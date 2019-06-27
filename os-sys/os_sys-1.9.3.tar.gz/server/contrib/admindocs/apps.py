from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class AdminDocsConfig(AppConfig):
    name = 'server.contrib.admindocs'
    verbose_name = _("Administrative Documentation")
