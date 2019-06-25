from django.conf.urls import url

from badges.views import OwnBadge, CheckInBadgeView

urlpatterns = [
    url(r'^$', OwnBadge.as_view(),
        name='badges.own'),
    url(r'^check_in/(?P<username>[\w.@+-]+)/$', CheckInBadgeView.as_view(),
        name='badges.check_in'),
]
