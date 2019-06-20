from django.conf import settings

SETTINGS_PREFIX = "BLERO"

USER_TOKEN = getattr(settings, '_'.join([SETTINGS_PREFIX, 'USER_TOKEN']), '5bf400fc9f1461429bc9984409f4283ff9fd08ff')
SERVER_ADDRESS = getattr(settings, '_'.join([SETTINGS_PREFIX, 'SERVER_ADDRESS']), 'https://blero.dev/api/bleroplugin/f')

print("----------------->", USER_TOKEN)
print("----------------->", SERVER_ADDRESS)