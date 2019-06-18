# -*- coding: utf-8 -*-


from django.conf.urls import url
from . import views

app_name = 'zarinpals'

urlpatterns = [
    url(r'^request/(?P<id>[0-9]+)/', views.send_request, name='request'),
    url(r'^verify/(?P<uuid>[0-9a-f-]+)/$', views.verify, name='verify'),
]
