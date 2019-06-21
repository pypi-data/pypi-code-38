from djangohelper.apps import AppConfig
from djangohelper.utils.translation import gettext_lazy as _


class SiteMapsConfig(AppConfig):
    name = 'djangohelper.contrib.sitemaps'
    verbose_name = _("Site Maps")
