from django.conf.urls import url, include

app_name = 'audits'

urlpatterns = [
    url(r'^admin/', include('aparnik.contrib.audits.api.admin.urls', namespace='admin')),
]