# -*- coding: utf-8 -*-

from django.conf.urls import patterns, include, url

from rest_framework.urlpatterns import format_suffix_patterns

from bigtiger.contrib.admin.sae.auth_session import AuthSessionList, AuthSessionDetail
from bigtiger.contrib.admin.sae.auth_user import AuthUserList, AuthUserDetail


urlpatterns = patterns(
    '',
    url(r'^session/$', AuthSessionList.as_view()),
    url(r'^session/pager/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'page_query'}),
    url(r'^session/exists_modify/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'exists_modify'}),
    url(r'^session/clear/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'clear'}),
    url(r'^session/clear_expired/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'clear_expired'}),
    url(r'^session/tran_delete/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'tran_delete'}),
    url(r'^session/(?P<pk>.*)/$', AuthSessionDetail.as_view()),

    url(r'^user/$', AuthUserList.as_view()),
    url(r'^user/authenticate/$', AuthUserList.as_view(),
        {'MIME_TYPE': 'authenticate'}),
    url(r'^user/(?P<pk>.*)/modify_pwd/$',
        AuthUserDetail.as_view(), {'MIME_TYPE': 'modify_pwd'}),
    url(r'^user/(?P<pk>.*)/permissions/$',
        AuthUserDetail.as_view(), {'MIME_TYPE': 'get_user_permissions'}),
    url(r'^user/(?P<pk>.*)/$', AuthUserDetail.as_view()),
)
