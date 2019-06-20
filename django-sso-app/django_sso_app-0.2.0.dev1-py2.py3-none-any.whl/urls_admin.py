from django.conf.urls import url
from django.views.generic.base import RedirectView

from django_sso_app.views import SsoAdminAuthUser

urlpatterns = [
    url(r"^auth/user/$", SsoAdminAuthUser.as_view(), name="sso_admin_auth_user"),
    url(r"^auth/user/", RedirectView.as_view(url=None, permanent=True)),
]
