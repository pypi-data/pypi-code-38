"""Url routing
"""
from django.conf.urls import url

from core_parser_app.tools.modules.views import views as modules_views

urlpatterns = [
    url(r'^$', modules_views.index,
        name='core_parser_app_modules'),
    url(r'^resources', modules_views.load_resources_view,
        name='core_parser_app_modules_resources'),
]
