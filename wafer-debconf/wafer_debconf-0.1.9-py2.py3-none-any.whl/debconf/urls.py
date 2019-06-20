from django.conf.urls import url

from debconf.views import (
    DCScheduleArrived, DebConfScheduleView, IndexView, RobotsView
)

urlpatterns = [
    url(r'^attendees/admin/export/arrived/$', DCScheduleArrived.as_view()),
    url(r'^schedule/$', DebConfScheduleView.as_view(),
        name='wafer_full_schedule'),
    url(r'^robots.txt$', RobotsView.as_view()),
    url(r'^$', IndexView.as_view()),
]
