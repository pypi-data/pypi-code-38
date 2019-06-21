from djangohelper.apps import AppConfig
from djangohelper.db.models.signals import post_migrate
from djangohelper.utils.translation import gettext_lazy as _

from .management import create_default_site


class SitesConfig(AppConfig):
    name = 'djangohelper.contrib.sites'
    verbose_name = _("Sites")

    def ready(self):
        post_migrate.connect(create_default_site, sender=self)
