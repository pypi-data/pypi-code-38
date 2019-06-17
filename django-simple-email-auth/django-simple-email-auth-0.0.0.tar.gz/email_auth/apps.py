from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class EmailAuthConfig(AppConfig):
    """
    Default configuration for the ``email_auth`` package.
    """

    name = "email_auth"
    verbose_name = _("Simple Email Authentication")
