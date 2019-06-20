from congo.conf import settings
from congo.maintenance import views as maintenance_views
from congo.maintenance import admin_views as maintenance_admin_views
from congo.communication import views as communication_views
from congo.communication import admin_views as communication_admin_views
from django.urls.conf import path, include

congo_patterns = [
    # admin
    path('admin/clear-cache/', maintenance_admin_views.clear_cache, name = 'clear_cache'),
    path('admin/test-mail/', communication_admin_views.test_mail, name = 'test_mail'),

    # maintenance
    path('r/<int:content_type_id>/<int:object_id>/', maintenance_views.redirect, name = "redirect"),

    # http errors
    path('error/400/', maintenance_views.bad_request, name = "http_400"),
    path('error/401/', maintenance_views.unauthorized, name = "http_401"),
    path('error/403/', maintenance_views.permission_denied, name = "http_403"),
    path('error/404/', maintenance_views.page_not_found, name = "http_404"),
    path('error/500/', maintenance_views.server_error, name = "http_500"),
    path('error/503/', maintenance_views.service_unavailable, name = "http_503"),

    path('error/400/test/', maintenance_views.http_error_test, {'error_no': 400}, name = "http_400_test"),
    path('error/403/test/', maintenance_views.http_error_test, {'error_no': 403}, name = "http_403_test"),
    path('error/404/test/', maintenance_views.http_error_test, {'error_no': 404}, name = "http_404_test"),
    path('error/500/test/', maintenance_views.http_error_test, {'error_no': 500}, name = "http_500_test"),
]

if settings.CONGO_EMAIL_MESSAGE_MODEL:
    # communication
    congo_patterns += [
        path('email/<int:message_id>/', communication_views.email_preview, name = "email_preview"),
        path('unsubscribe/<int:object_id>/<str:token>/', communication_views.unsubscribe, name = "email_unsubscribe"),
    ]

urlpatterns = [
    # you can now use eg. {% url "congo:email_preview" %}
    path('', include((congo_patterns, 'congo'))),
]
