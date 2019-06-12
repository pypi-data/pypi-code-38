#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'
from django.conf.urls import include, url
from django.contrib.auth import views as auth_views

from . import views

app_name = "bee_django_user"

urlpatterns = [
    url(r'^test/$', views.test, name='test'),
    url(r'^$', views.UserList.as_view(), name='index'),

    url(r'^login/$', auth_views.LoginView.as_view(template_name='bee_django_user/user/login.html'), name='user_login'),
    url(r'^logout/$', auth_views.logout, {'next_page': '/user/login'}, name='user_logout'),
    url(r'^password/change/$', views.UserPasswordChangeView.as_view(), name='user_password_change'),
    url(r'^password/change/done/$', auth_views.PasswordChangeDoneView.as_view(
        template_name='bee_django_user/user/password_change_done.html'
    ), name='user_password_change_done'),
    url(r'^password/reset/(?P<pk>[0-9]+)/$', views.UserPasswordResetView.as_view(), name='user_password_reset'),

    # 学生
    url(r'^list/$', views.UserList.as_view(), name='user_list'),
    url(r'^detail/(?P<pk>[0-9]+)/$', views.UserDetail.as_view(), name='user_detail'),
    url(r'^create/$', views.UserCreate.as_view(), name='user_create'),
    url(r'^code/create/$', views.CodeUserCreate.as_view(), name='code_user_create'),
    url(r'^update/(?P<pk>[0-9]+)/$', views.UserUpdate.as_view(), name='user_update'),
    url(r'^group/update/(?P<pk>[0-9]+)/$', views.UserGroupUpdate.as_view(), name='user_group_update'),
    url(r'^sn/update/(?P<pk>[0-9]+)/$', views.UserSNUpdate.as_view(), name='user_sn_update'),
    # 组及权限
    url(r'^group/list/$', views.GroupList.as_view(), name='group_list'),
    url(r'^status/save/$', views.StatusSave.as_view(), name='status_save'),

    # 结课日期
    url(r'^leave/list/(?P<user_id>[0-9]+)/$', views.LeaveList.as_view(), name='leave_list'),
    url(r'^leave/detail/(?P<pk>[0-9]+)/$', views.LeaveDetail.as_view(), name='leave_detail'),
    url(r'^leave/add/(?P<user_id>[0-9]+)/$', views.LeaveCreate.as_view(), name='leave_add'),
    url(r'^leave/check/$', views.LeaveUpdateCheck.as_view(), name='leave_check'),
    url(r'^leave/cancel/(?P<pk>[0-9]+)/$', views.LeaveCancel.as_view(), name='leave_cancel'),
    url(r'^leave/delete/(?P<pk>[0-9]+)/$', views.LeaveDelete.as_view(), name='leave_delete'),

    # 班级
    url(r'^class/list/$', views.ClassList.as_view(), name='class_list'),
    url(r'^class/create/$', views.ClassCreate.as_view(), name='class_create'),
    url(r'^class/detail/(?P<pk>[0-9]+)/$', views.ClassDetail.as_view(), name='class_detail'),
    url(r'^class/update/(?P<pk>[0-9]+)/$', views.ClassUpdate.as_view(), name='class_update'),

]
