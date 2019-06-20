import sys
from django.conf import settings

SETTINGS_PREFIX = "BLERO"

for attr in dir(settings):
	if(attr.startswith(SETTINGS_PREFIX)):
		# Ignore "BLERO_" from the settings attribute name
		var_name = attr.split(SETTINGS_PREFIX)[1][1:]
		var_val = getattr(settings, attr)

		# Set the new attribute for the current module
		setattr(sys.modules[__name__], var_name, var_val)