# -*- coding: utf-8 -*-
from django.conf.urls import url, include

from .rocit.urls import urlpatterns as rocit_urls

urlpatterns = [
    url(r'^', include(rocit_urls)),
]
