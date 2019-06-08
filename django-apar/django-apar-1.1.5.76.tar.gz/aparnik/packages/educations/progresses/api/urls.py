# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url
from .views import ProgressSetAPIView

urlpatterns = [
    # url(r'^$', ProgressListAPIView.as_view(), name='list'),
    url(r'^(?P<file_id>[\w-]+)/set/$', ProgressSetAPIView.as_view(), name='set'),
    # url(r'^(?P<progress_id>[\w-]+)/update', ProgressUpdateAPIView.as_view(), name='update'),
]
