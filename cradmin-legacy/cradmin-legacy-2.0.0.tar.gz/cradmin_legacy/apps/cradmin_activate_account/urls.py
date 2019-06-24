from __future__ import unicode_literals

from django.conf.urls import url

from cradmin_legacy.apps.cradmin_activate_account.views.activate import ActivateAccountView

urlpatterns = [
    url(r'^activate/(?P<token>.+)',
        ActivateAccountView.as_view(),
        name="cradmin-activate-account-activate"),
]
