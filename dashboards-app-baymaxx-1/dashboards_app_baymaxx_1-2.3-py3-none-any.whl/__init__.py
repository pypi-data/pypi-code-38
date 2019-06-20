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
