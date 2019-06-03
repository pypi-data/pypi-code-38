""" Url router for OAI-PMH provider application
"""
from django.conf.urls import url, include
from core_oaipmh_provider_app.views.user.views import OAIProviderView
from core_oaipmh_provider_app.views.user.views import get_xsd

urlpatterns = [
    url(r'^rest/', include('core_oaipmh_provider_app.rest.urls')),
    url(r'^(?i)XSD/(?P<title>.*)/(?:(?P<version_number>\d+)/)', get_xsd, name="core_oaipmh_provider_app_get_xsd"),
    url(r'^', OAIProviderView.as_view(), name="core_oaipmh_provider_app_server_index"),
]
