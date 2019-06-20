from django.conf.urls import url, include

from .views import *

urlpatterns = [
    url(r'^create_task/', create_task),  # task tracker url
    url(r'^delete_task/', delete_task),  # task tracker url
    url(r'^save_task/', save_task),  # task tracker url
    url(r'^complete_task/', complete_task),  # task tracker url
    url(r'^filter_outstanding/', filter_outstanding),  # task tracker url`
]
