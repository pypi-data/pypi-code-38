import sys

from django.conf import settings

from .subject_screening import SubjectScreening

# if settings.APP_NAME == 'ambition_screening' and 'makemigrations' not in sys.argv:
#     from ..tests import models
