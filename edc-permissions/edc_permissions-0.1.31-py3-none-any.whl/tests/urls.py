from edc_dashboard.views import AdministrationView
from django.urls.conf import path, include

urlpatterns = [
    path("accounts/", include("edc_auth.urls")),
    path("edc_dashboard/", include("edc_dashboard.urls")),
    path("edc_export/", include("edc_export.urls")),
    path("edc_lab/", include("edc_lab.urls")),
    path("edc_lab_dashboard/", include("edc_lab_dashboard.urls")),
    path("edc_pharmacy/", include("edc_pharmacy.urls")),
    path("edc_reference/", include("edc_reference.urls")),
    path("edc_permissions/", include("edc_permissions.urls")),
    path("administration/", AdministrationView.as_view(), name="administration_url"),
]
