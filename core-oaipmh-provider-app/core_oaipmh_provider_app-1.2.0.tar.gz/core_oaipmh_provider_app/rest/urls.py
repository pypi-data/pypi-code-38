"""Url router for the REST API
"""
from django.conf.urls import url

from core_oaipmh_provider_app.rest.oai_provider_metadata_format import views as \
    oai_metadata_format_views
from core_oaipmh_provider_app.rest.oai_provider_set import views as oai_set_views
from core_oaipmh_provider_app.rest.oai_settings import views as oai_settings_views

urlpatterns = [
    url(r'^settings', oai_settings_views.Settings.as_view(),
        name='core_oaipmh_provider_app_rest_settings'),
    url(r'^check', oai_settings_views.Check.as_view(),
        name='core_oaipmh_provider_app_rest_check'),
    url(r'^metadata_format/$', oai_metadata_format_views.MetadataFormatsList.as_view(),
        name='core_oaipmh_provider_app_rest_metadata_format_list'),
    url(r'^metadata_format/(?P<metadata_format_id>\w+)/$',
        oai_metadata_format_views.MetadataFormatDetail.as_view(),
        name='core_oaipmh_provider_app_rest_metadata_format_detail'),
    url(r'^template_metadata_format$',
        oai_metadata_format_views.TemplateAsMetadataFormat.as_view(),
        name='core_oaipmh_provider_app_rest_template_metadata_format'),
    url(r'^template_metadata_format_xslt',
        oai_metadata_format_views.TemplateMetadataFormatXSLT.as_view(),
        name='core_oaipmh_provider_app_rest_template_metadata_format_xslt'),
    url(r'^set/(?P<set_id>\w+)/$', oai_set_views.SetDetail.as_view(),
        name='core_oaipmh_provider_app_rest_set'),
    url(r'^sets/$', oai_set_views.SetsList.as_view(),
        name='core_oaipmh_provider_app_rest_sets_list'),
]
