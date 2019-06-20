from django.conf import settings

SETTINGS_PREFIX = "BLERO"

USER_TOKEN = getattr(settings, '_'.join([SETTINGS_PREFIX, 'USER_TOKEN']), 'default_value')
SERVER_ADDRESS = getattr(settings, '_'.join([SETTINGS_PREFIX, 'SERVER_ADDRESS']), 'default_value')