from django.conf.urls import url, include
from django.contrib import admin
from core_explore_keyword_app import urls as core_explore_keyword_app_urls

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
] + core_explore_keyword_app_urls.urlpatterns
