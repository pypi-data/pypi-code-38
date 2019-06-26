"""
URL patterns for ActivityPub

Note: some of them aren't implemented, and just return empty collections
"""
from django.conf.urls import include, url

from . import views

sub_patterns = [
    url(r"^following$", views.empty),
    url(r"^followers$", views.empty),
    url(r"^liked$", views.empty),
    url(r"^inbox$", views.inbox),
    url(r"^outbox$", views.outbox),
    url(r"^$", views.endpoint),
]
urlpatterns = [url(r"^(?P<path>.*)/", include(sub_patterns))]
