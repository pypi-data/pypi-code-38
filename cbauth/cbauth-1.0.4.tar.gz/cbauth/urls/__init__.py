from django.conf import settings
from django.urls import path
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.views import (
    LoginView,
    LogoutView
)

urlpatterns = []


if getattr(settings, 'CB_INCLUDE_MAIN_VIEW', False):
    main_view = login_required(TemplateView.as_view(template_name="main.html"))
    urlpatterns += [
        path('', main_view, name='auth_main'),
    ]

if getattr(settings, 'CB_INCLUDE_TEMPLATE_VIEWS', False):
    from cbauth.urls.pages import urlpatterns as views_urls
    urlpatterns += views_urls


if getattr(settings, 'CB_INCLUDE_API_VIEWS', True):
    from cbauth.urls.api import urlpatterns as api_urls
    urlpatterns += api_urls
