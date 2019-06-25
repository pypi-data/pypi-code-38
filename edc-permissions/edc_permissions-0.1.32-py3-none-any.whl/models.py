import sys

from django.conf import settings

if settings.APP_NAME == "edc_permissions" and (
    "test" in sys.argv or "runtests.py" in sys.argv
):
    from .tests.models import *  # noqa
