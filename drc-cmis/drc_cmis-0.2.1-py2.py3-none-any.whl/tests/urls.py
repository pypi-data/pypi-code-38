from django.contrib import admin
from django.urls import include, path
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('test-url/<version>/<uuid>', TemplateView.as_view(), name='enkelvoudiginformatieobjecten-detail'),
    path('test-url2/<version>/<uuid>', TemplateView.as_view(), name='objectinformatieobjecten-detail'),
    path('ref/', include('vng_api_common.notifications.urls')),
    path('cmis/', include('drc_cmis.urls', namespace="cmis")),
]
