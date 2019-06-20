from django.conf.urls import url
from congo.conf import settings
from congo.maintenance import views as maintenance_views
from congo.maintenance import admin_views as maintenance_admin_views
from congo.maintenance import ajax_views as maintenance_ajax_views
from congo.communication import views as communication_views
from congo.communication import admin_views as communication_admin_views

urlpatterns = [
    # maintenance
    url(r'^reset-server/$', maintenance_views.reset_server, name = 'reset_server'),
    url(r'^r/(?P<content_type_id>[\d]+)/(?P<object_id>[\d]+)/$', maintenance_views.redirect, name = "redirect"),

    url(r'^admin/clear-cache/$', maintenance_admin_views.clear_cache, name = 'clear_cache'),

    # http errors
    url(r'^400/$', maintenance_views.http_error, {'error_no': 400}, name = "http_400"),
    url(r'^403/$', maintenance_views.http_error, {'error_no': 403}, name = "http_403"),
    url(r'^404/$', maintenance_views.http_error, {'error_no': 404}, name = "http_404"),
    url(r'^500/$', maintenance_views.http_error, {'error_no': 500}, name = "http_500"),
    url(r'^503/$', maintenance_views.http_error, {'error_no': 503}, name = "http_503"),

    # ajax
    url(r'^congo/maintenance/ajax/(?P<action>[\w\-]+)/$', maintenance_ajax_views.ajax, name = "maintenance_ajax"),
]

if settings.CONGO_EMAIL_MESSAGE_MODEL:
    # communication
    urlpatterns += [
        url(r'^admin/test-mail/$', communication_admin_views.test_mail, name = 'test_mail'),
        url(r'^preview-email/(?P<message_id>[\d]+)/$', communication_views.preview_email, name = "email_preview"),
    ]

