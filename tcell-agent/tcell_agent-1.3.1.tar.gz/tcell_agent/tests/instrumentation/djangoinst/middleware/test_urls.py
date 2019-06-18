# this is used by other middleware tests to set settings.ROOT_URLCONF

from django.conf.urls import include, url  # pylint: disable=unused-import
from django.contrib import admin  # pylint: disable=unused-import

urlpatterns = []

from django.contrib.staticfiles.urls import staticfiles_urlpatterns  # pylint: disable=unused-import
