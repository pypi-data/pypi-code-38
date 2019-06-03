from __future__ import absolute_import

from collections.abc import Callable

from django.conf import settings
from django.utils.module_loading import import_string

from pbx_admin.handlers import default_protected_error_handler


class Settings(object):
    """
    Shadow Django's settings with a little logic
    """

    @property
    def DUPLICATE_MESSAGES_HANDLER(self):
        handler = getattr(settings, 'PBX_ADMIN_DUPLICATE_MESSAGES_HANDLER',
                          None)
        if isinstance(handler, Callable) or handler is None:
            return handler
        handler = import_string(handler)
        return handler

    @property
    def PROTECTED_ERROR_HANDLER(self):
        handler = getattr(settings, 'PBX_ADMIN_PROTECTED_ERROR_HANDLER',
                          default_protected_error_handler)
        if isinstance(handler, Callable) or handler is None:
            return handler
        handler = import_string(handler)
        return handler

    @property
    def ITEMS_PER_PAGE(self):
        return getattr(settings, 'PBX_ADMIN_ITEMS_PER_PAGE', 50)


admin_settings = Settings()
