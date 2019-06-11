from django.conf.urls import url
from django.views.decorators.csrf import csrf_exempt

from rebotics_sdk.hook import views


app_name = 'rebotics_sdk.hook'

urlpatterns = [
    url(r'^webhook/$', csrf_exempt(views.WebhookHandlerViewSet.as_view()), name='webhook'),
]
