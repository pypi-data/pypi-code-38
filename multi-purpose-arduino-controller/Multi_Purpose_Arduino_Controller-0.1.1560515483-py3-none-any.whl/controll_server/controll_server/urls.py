"""digitalization_server URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

#
#if manage.py is called directly
from multi_purpose_arduino_controller.controll_server.manage import logger

if len(__name__.split(".")) == 2:
    from templatetags.installed_apps import get_apps
else:
    from ..templatetags.installed_apps import get_apps
from . import views

urlpatterns = [path("admin/", admin.site.urls), path("", views.index, name="index")]


for app in get_apps():
    try:
        if hasattr(app, "baseurl"):
            print(app.label)
            urlpatterns.append(
                path(
                    app.baseurl + "/",
                    include(
                        ("%s.urls" % app.module_path, app.label), namespace=app.label
                    ),
                )
            )
            print(app.label)

    except ModuleNotFoundError as e:
        logger.exception(e)
        pass