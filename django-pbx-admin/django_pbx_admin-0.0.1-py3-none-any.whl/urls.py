from django.conf import settings
from django.conf.urls import url
from django.contrib.auth import views as auth_views

from pbxapps.pbadmin.admins.base import site
from .views import views

app_name = 'pbx_admin'

urlpatterns = [
    # Auth
    url(r'^login/$',
        auth_views.LoginView.as_view(
            template_name='pbx_admin/login.html',
            extra_context={'title': f'PBX2 {settings.PRINTBOX_SITE_NAME}'}),
        name='login'),
    url(r'^logout/$',
        auth_views.LogoutView.as_view(
            template_name='pbx_admin/logged_out.html',
            extra_context={'title': f'PBX2 {settings.PRINTBOX_SITE_NAME}'}),
        name='logout'),

    # Other
    url(r'^$',
        views.IndexView.as_view(),
        name='index'),
    url(r'^exchange-rates/$',
        views.ExchangeRatesView.as_view(),
        name='exchange_rates'),
    url(r'^logo/$',
        views.LogoView.as_view(),
        name='logo_manager'),
    url(r'^assets-manager/$',
        views.AssetsManagerView.as_view(),
        name='assets_manager'),
]

urlpatterns += site.get_urls()
