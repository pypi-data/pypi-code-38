from django.conf import settings

DEBUG = getattr(settings, "DEBUG", False)

SETTINGS = getattr(settings, "RESTRICTED_PATHS", {})

PATHS = SETTINGS.get("PATHS", ())

VIEW = SETTINGS.get("VIEW", None)
