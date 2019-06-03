from django.conf.urls import url, include
from django.contrib import admin
from core_curate_app import urls as core_curate_app_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
] + core_curate_app_urls.urlpatterns
