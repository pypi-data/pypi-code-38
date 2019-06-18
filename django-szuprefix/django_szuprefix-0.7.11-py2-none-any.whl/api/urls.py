from django.conf.urls import url
from django_szuprefix.utils.views import csrf_token

urlpatterns = [
    url(r'^csrf_token/$', csrf_token, name='csrf_token')
]

