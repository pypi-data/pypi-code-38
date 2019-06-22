from django.conf.urls import url
from mint import views


def get_urlconf(coordinator):
    return [
        url(r'^(?P<ctx>[a-z_]+)/(?P<idx>[a-zA-Z0-9]+)/(?P<action>[a-z_]+)/?$', views.with_id, {'coordinator': coordinator}),
        url(r'^(?P<ctx>[a-z_]+)/(?P<idx>[a-zA-Z0-9_]+)/?$', views.with_id, {'coordinator': coordinator}),
        url(r'^(?P<ctx>[a-z_]+)/?$', views.without_id, {'coordinator': coordinator}),
    ]