# -*- coding: utf-8 -*-

from django.conf.urls import include, url
from django_onerror import views as err_views


urlpatterns = [
    url(r'^report', err_views.err_report, name='err_report'),
]
