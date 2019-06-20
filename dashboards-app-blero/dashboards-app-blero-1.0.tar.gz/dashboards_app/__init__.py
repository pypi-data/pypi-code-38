# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.conf import settings
import os

__version__ = '2.1.3'


default_app_config = 'dashboards_app.apps.AldrynDashboards_app'

if not os.path.exists(os.path.join(settings.BASE_DIR,'resources')):
	raise ImportError("resources dir not found!")

if not os.path.exists(os.path.join(settings.BASE_DIR, 'static/js/dashboards')):
	raise ImportError("static/js/dashboards dir not found!")

dashboards_dir = os.path.join(settings.BASE_DIR, 'resources/dashboards')
CELERY_IMPORTS = ['resources.dashboards.' + addr + '.FormFunctions' for addr in os.listdir(dashboards_dir) \
									if (not addr.startswith("__")) and os.path.isdir(os.path.join(dashboards_dir, addr))]
CELERY_RESULT_SERIALIZER = 'json'

# Set the attributes for settings module
setattr(settings, 'CELERY_IMPORTS', CELERY_IMPORTS)
setattr(settings, 'CELERY_RESULT_SERIALIZER', CELERY_RESULT_SERIALIZER)
