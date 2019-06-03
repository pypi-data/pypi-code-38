from django.conf.urls import url, include
from django.contrib import admin
from core_exporters_app import urls as core_exporters_app_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
] + core_exporters_app_urls.urlpatterns
