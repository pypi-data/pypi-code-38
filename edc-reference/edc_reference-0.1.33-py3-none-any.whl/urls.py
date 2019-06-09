from django.views.generic.base import RedirectView
from django.urls.conf import path

from .admin_site import edc_reference_admin

app_name = "edc_reference"

urlpatterns = [
    path("admin/", edc_reference_admin.urls),
    path("", RedirectView.as_view(url="/edc_reference/admin/"), name="home_url"),
]
