from django.conf.urls import url

from rebotics_sdk.notifications import views

urlpatterns = [
    url(r'^notifications/setWebhook/$', view=views.SetWebhookView.as_view(), name='set-webhook'),
]
