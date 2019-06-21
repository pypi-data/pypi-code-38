from djangohelper.apps import AppConfig
from djangohelper.utils.translation import gettext_lazy as _


class SyndicationConfig(AppConfig):
    name = 'djangohelper.contrib.syndication'
    verbose_name = _("Syndication")
