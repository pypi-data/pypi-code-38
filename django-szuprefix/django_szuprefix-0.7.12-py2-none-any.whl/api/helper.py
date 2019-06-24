# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals

from rest_framework.routers import DefaultRouter


class newRouter(DefaultRouter):
    URL_PATTERNS = []

    def get_urls(self):
        urls = super(newRouter, self).get_urls()
        from .urls import urlpatterns as api_urls
        # from ..auth.urls import urlpatterns as auth_urls
        urls = api_urls + self.URL_PATTERNS + urls  # auth_urls +
        return urls

    def add_urls(self, urls):
        self.URL_PATTERNS += urls


router = newRouter()


def register(package, resource, viewset, base_name=None):
    p = "%s/%s" % (package.split(".")[-1], resource)
    router.register(p, viewset, base_name=base_name)


def register_urlpatterns(package, urls):
    from django.conf.urls import include, url
    app_name = package.split(".")[-1]
    router.add_urls([url(r'^%s/' % app_name, include(urls))])
