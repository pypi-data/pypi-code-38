from django.urls.conf import path
from ambition_dashboard.views import AeHomeView

from .admin_site import ambition_ae_admin

app_name = "ambition_ae"

urlpatterns = [
    path("admin/", ambition_ae_admin.urls),
    path("", AeHomeView.as_view(), name="home_url"),
]
