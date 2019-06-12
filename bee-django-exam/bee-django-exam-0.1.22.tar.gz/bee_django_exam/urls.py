#!/usr/bin/env python
# -*- coding:utf-8 -*-
__author__ = 'bee'

from django.conf.urls import include, url
from . import views
app_name = 'bee_django_exam'
urlpatterns = [
    url(r'^test$', views.test, name='test'),
    url(r'^$', views.UserExamRecordList.as_view(), name='index'),
    # ==Grade==
    url(r'^grade/list/$', views.GradeList.as_view(), name='grade_list'),
    url(r'^grade/detail/(?P<pk>[0-9]+)/$', views.GradeDetail.as_view(), name='grade_detail'),
    url(r'^grade/add/$', views.GradeCreate.as_view(), name='grade_add'),
    url(r'^grade/update/(?P<pk>[0-9]+)/$', views.GradeUpdate.as_view(), name='grade_update'),
    url(r'^grade/delete/(?P<pk>[0-9]+)/$', views.GradeDelete.as_view(), name='grade_delete'),
    url(r'^grade/cert/field/add/(?P<pk>[0-9]+)/$', views.GradeCertFieldCreate.as_view(), name='grade_cert_field_add'),
    url(r'^grade/cert/field/update/(?P<pk>[0-9]+)/$', views.GradeCertFieldUpdate.as_view(),
        name='grade_cert_field_update'),
    url(r'^grade/cert/field/delete/(?P<pk>[0-9]+)/$', views.GradeCertFieldDelete.as_view(),
        name='grade_cert_field_delete'),
    # 经过处理过的证书图片
    url(r'^grade/cert/modify/(?P<pk>[0-9]+)/$', views.GradeCertModify.as_view(), name='grade_cert_modify'),

    # ==Notice==
    url(r'^notice/list/$', views.NoticeList.as_view(), name='notice_list'),
    url(r'^notice/detail/(?P<pk>[0-9]+)/$', views.NoticeDetail.as_view(), name='notice_detail'),
    url(r'^notice/add/$', views.NoticeCreate.as_view(), name='notice_add'),
    url(r'^notice/update/(?P<pk>[0-9]+)/$', views.NoticeUpdate.as_view(), name='notice_update'),

    # ==User Exam Record==

    url(r'^user/notice/(?P<user_record_id>[0-9]+)/$', views.UserExamNotice.as_view(),name='user_exam_notice'),
    url(r'^user/record/done/$', views.UserExamRecordDone.as_view(), name='user_exam_record_done'),
    url(r'^user/record/list/(?P<user_id>[0-9]+)/$', views.UserExamRecordList.as_view(), name='user_exam_record_list'),
    url(r'^custom_user/record/list/(?P<user_id>[0-9]+)/$', views.CustomUserExamRecordList.as_view(), name='custom_user_exam_record_list'),
    url(r'^user/record/detail/(?P<pk>[0-9]+)/$', views.UserExamRecordDetail.as_view(), name='user_exam_record_detail'),
    url(r'^user/record/add/(?P<user_id>[0-9]+)/$', views.UserExamRecordCreate.as_view(), name='user_exam_record_add'),
    url(r'^user/record/update/(?P<pk>[0-9]+)/$', views.UserExamRecordUpdate.as_view(), name='user_exam_record_update'),
    url(r'^user/record/cert/create/(?P<record_id>[0-9]+)/$', views.UserCertCreate.as_view(),
        name='user_cert_create'),
    # url(r'^user/record/cert/upload/(?P<record_id>[0-9]+)/$', views.UserCertUpload.as_view(),
    #     name='user_cert_create'),
]
