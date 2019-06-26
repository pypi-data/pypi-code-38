"""
URL patterns for testing app.
"""
from django.conf.urls import url

from . import views

app_name = "tests"
urlpatterns = [
    url(r"^$", views.article_list, name="index"),
    url(r"^~(?P<user_id>[0-9]+)/$", views.user_detail, name="user"),
    url(r"^(?P<article_pk>\w+)/$", views.article_detail, name="article"),
    url(r"^\.(?P<sub_id>[0-9]+)/$", views.subscriber_detail, name="subscriber"),
    url(r"^subscribe$", views.subscribe, name="subscribe"),
    url(r"^(?P<article_pk>\w+)/comment$", views.comment, name="post-comment"),
]
