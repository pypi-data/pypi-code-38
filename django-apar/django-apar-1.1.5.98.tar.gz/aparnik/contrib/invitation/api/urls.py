

from django.conf.urls import url

from aparnik.contrib.invitation.api.views import InviteDetailAPIView, InviteListAPIView


app_name = 'invitation'

urlpatterns = [
    url(r'^$', InviteListAPIView.as_view(), name='list'),
    url(r'^(?P<id>\d+)/$', InviteDetailAPIView.as_view(), name='detail'),
]
