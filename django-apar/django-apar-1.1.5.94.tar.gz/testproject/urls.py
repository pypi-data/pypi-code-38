"""testproject URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from django.conf.urls.static import static
from django.conf import settings

from aparnik.contrib.suit.views import login
#
handler404 = 'aparnik.contrib.suit.views.handler404'
handler500 = 'aparnik.contrib.suit.views.handler500'

urlpatterns = [
    url(r'^admin/login', login),
    url(r'^admin/', admin.site.urls),
    url(r'^admin/dynamic_raw_id/', include('dynamic_raw_id.urls')),
    # app
    url(r'^api/v1/aparnik/', include('aparnik.urls.api', namespace='aparnik-api')),
    url(r'^aparnik/', include('aparnik.urls.urls', namespace='aparnik')),
    url(r'^directupload/', include('s3direct.urls')),
    url(r'^ckeditor/', include('ckeditor_uploader.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

from django.contrib.staticfiles.urls import staticfiles_urlpatterns
urlpatterns += staticfiles_urlpatterns()

import debug_toolbar

urlpatterns += url(r'^__debug__/', include(debug_toolbar.urls)),