from server.apps import AppConfig
from server.utils.translation import gettext_lazy as _


class HumanizeConfig(AppConfig):
    name = 'server.contrib.humanize'
    verbose_name = _("Humanize")
