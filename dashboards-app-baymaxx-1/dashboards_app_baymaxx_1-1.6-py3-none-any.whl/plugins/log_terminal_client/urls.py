# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^check-log-client/$', log_checker),
    url(r'^delete-log-content-client/$', delete_log_content),
]
