from django.conf import settings
from django.contrib import admin
from django.urls import path
from django.views.generic.base import RedirectView
from django.urls.conf import include

app_name = "edc_permissions"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", RedirectView.as_view(url="/edc_permissions/admin/"), name="home_url"),
]
