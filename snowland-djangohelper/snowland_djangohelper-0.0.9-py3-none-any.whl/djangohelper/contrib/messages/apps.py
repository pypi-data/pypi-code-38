from djangohelper.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MessagesConfig(AppConfig):
    name = 'djangohelper.contrib.messages'
    verbose_name = _("Messages")
