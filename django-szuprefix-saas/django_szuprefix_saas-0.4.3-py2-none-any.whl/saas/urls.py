# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django.conf.urls import url, include
from django.contrib.auth.decorators import login_required
from . import views

app_name = "saas"
urlpatterns = [
    url(r'^party/', include([
        url('create/$', login_required(views.PartyCreateView.as_view()), name='party-create'),
    ])),
    url(r'^worker/', include([
        url('create/$', login_required(views.WorkerCreateView.as_view()), name='worker-create'),
    ]))
]
