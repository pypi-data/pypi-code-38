from django.conf.urls import url
from django.utils.translation import ugettext_lazy as _
from views import LoginView, RegisterView, ProfileView, PackageView,\
    PasswordView, LogoutView, RecoveryView, ActivateView, LoginAsDemoView, \
    LogoutAndRegisterView, APIKeysView

urlpatterns = [
    url(_(r'login/$'), LoginView.as_view(), name='accounts_login'),
    url(_(r'login/demo/$'), LoginAsDemoView.as_view(), name='accounts_login_demo'),
    url(_(r'logout-register/$'), LogoutAndRegisterView.as_view(), name='accounts_logout_register'),
    url(_(r'register/$'), RegisterView.as_view(), name='accounts_register'),
    url(_(r'profile/$'), ProfileView.as_view(), name='accounts_profile'),
    url(_(r'api-keys/$'), APIKeysView.as_view(), name='accounts_api_keys'),
    url(_(r'package/$'), PackageView.as_view(), name='accounts_package'),
    url(_(r'logout/$'), LogoutView.as_view(), name='accounts_logout'),
    url(_(r'password/$'), PasswordView.as_view(), name='accounts_password'),
    url(_(r'reset/$'), RecoveryView.as_view(), name='accounts_recovery'),
    url(_(r'^activate/(?P<activation_hash>\w+)/$'), ActivateView.as_view(), name='accounts_activate'),
    url(r'^$', ProfileView.as_view(), name='accounts'),
]
