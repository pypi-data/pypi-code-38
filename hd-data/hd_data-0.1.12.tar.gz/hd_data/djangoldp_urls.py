"""hd_site URL Configuration"""

from django.conf.urls import url
from .views import FutureEventsViewset

urlpatterns = [
    url(r'^futureevents/', FutureEventsViewset.urls()),
]
