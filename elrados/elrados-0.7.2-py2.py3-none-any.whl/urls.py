"""Django definitions for the administrator site urls."""
from django.conf.urls import url

from elrados import utils

# pylint: disable=invalid-name
urlpatterns = [
    url(r'^api/elrados/release_owner/(?P<data_name>.*?)/?$',
        utils.set_field("owner"), name="remove_resource_owner"),
    url(r'^api/elrados/release_reserved/(?P<data_name>.*?)/?$',
        utils.set_field("reserved"), name="remove_resource_reserved"),
    url(r'^api/elrados/lock_resource/(?P<data_name>.*?)/?$',
        utils.lock_resource, name="lock_resource"),
    url(r'^/?$', "elrados.views.index"),
]
