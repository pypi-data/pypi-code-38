import sys
from django.conf import settings

SETTINGS_PREFIX = "BLERO"

for attr in dir(settings):
	if(attr.startswith(SETTINGS_PREFIX)):
		var_name = attr.split(SETTINGS_PREFIX)[1][1:]
		var_val = getattr(settings, attr)
		setattr(sys.modules[__name__], var_name, var_val)

print("##########", USER_TOKEN, SERVER_ADDRESS)