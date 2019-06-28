from django.conf.urls import url, include

from .views import ajax_login, ajax_logout

app_name = "ajax_access"

urlpatterns = [
    url(r"^ajax/", include([
        url(r"^login/?$", ajax_login, name="ajax-login"),
        url(r"^logout/?$", ajax_logout, name="ajax-logout"),
    ])),
]
