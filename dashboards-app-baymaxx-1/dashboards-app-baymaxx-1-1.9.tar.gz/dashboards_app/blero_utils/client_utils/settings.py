import sys
from django.conf import settings

SETTINGS_PREFIX = "BLERO"

for attr in dir(settings):
	if(attr.startswith(SETTINGS_PREFIX)):
		var_name = attr.split(SETTINGS_PREFIX)[1][1:]
		var_val = getattr(settings, attr)
		print("#######", var_name, var_val)
		setattr(sys.modules[__name__], var_name, var_val)

print("$$$$$$$$$$$$$$$$$$", dir(sys.modules[__name__]))

USER_TOKEN = getattr(settings, '_'.join([SETTINGS_PREFIX, 'USER_TOKEN']), '5bf400fc9f1461429bc9984409f4283ff9fd08ff')
SERVER_ADDRESS = getattr(settings, '_'.join([SETTINGS_PREFIX, 'SERVER_ADDRESS']), 'https://blero.dev/api/bleroplugin/f')