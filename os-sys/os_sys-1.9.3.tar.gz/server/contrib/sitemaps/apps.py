from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class SiteMapsConfig(AppConfig):
    name = 'server.contrib.sitemaps'
    verbose_name = _("Site Maps")
