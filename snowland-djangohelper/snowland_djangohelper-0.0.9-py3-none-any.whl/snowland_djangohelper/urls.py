"""snowland_djangohelper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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

from djangohelper.developer.views import *
from django.conf.urls import url, include
from django.contrib import admin
from django.views import defaults
from django.views.static import serve

from . import settings

urlpatterns = [
    url('admin/', admin.site.urls),
    url(r'^new_application$', new_application),
    url(r'^change_key$', change_key),
]


handler400 = defaults.bad_request
handler403 = defaults.permission_denied
handler404 = defaults.page_not_found
handler500 = defaults.server_error
