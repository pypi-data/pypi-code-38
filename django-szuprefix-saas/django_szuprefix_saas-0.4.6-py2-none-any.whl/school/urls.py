# -*- coding:utf-8 -*- 
__author__ = 'denishuang'
from django.conf.urls import url, include
from . import views
from django.contrib.auth.decorators import login_required

app_name = "school"
urlpatterns = [
    url(r'^school/', include([
        url('create/$', login_required(views.SchoolCreateView.as_view()), name='school-create'),
    ])),
    url(r'^student/', include([
        url('(?P<pk>\d+)/$', login_required(views.StudentDetailView.as_view()), name='student-detail'),
        url('^$', login_required(views.StudentListView.as_view()), name='student-list'),
    ]))
]
