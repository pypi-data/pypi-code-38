from django.conf import settings

SETTINGS_PREFIX = "BLERO"

for attr in dir(settings):
	if(attr.startswith(SETTINGS_PREFIX)):
		print("##############", attr, getattr(settings, attr))
		# var_name = attr.split(SETTINGS_PREFIX)[1][1:]
		# var_val = 
		# setattr(__file__, var_name)

USER_TOKEN = getattr(settings, '_'.join([SETTINGS_PREFIX, 'USER_TOKEN']), '5bf400fc9f1461429bc9984409f4283ff9fd08ff')
SERVER_ADDRESS = getattr(settings, '_'.join([SETTINGS_PREFIX, 'SERVER_ADDRESS']), 'https://blero.dev/api/bleroplugin/f')