# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from bigtiger.contrib.admin.apis.auth_group import AuthGroupList, AuthGroupDetail
from bigtiger.contrib.admin.apis.auth_permission import AuthPermissionList
from bigtiger.contrib.admin.apis.auth_session import AuthSessionList, AuthSessionDetail
from bigtiger.contrib.admin.apis.auth_user_log import AuthUserLogList
from bigtiger.contrib.admin.apis.microapp_token import MicroAppTokenList
from bigtiger.contrib.admin.apis.sys_book import SysBookList
from bigtiger.contrib.admin.apis.sys_config import SysConfigList


urlpatterns = patterns(
    '',
    url(r'^auth_group/$', AuthGroupList.as_view()),
    url(r'^auth_group/(?P<pk>.*)/$', AuthGroupDetail.as_view()),

    url(r'^auth_permission/$', AuthPermissionList.as_view()),

    url(r'^auth_session/$', AuthSessionList.as_view()),
    url(r'^auth_session/pager/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'page_query'}),
    url(r'^auth_session/exists_modify/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'exists_modify'}),
    url(r'^auth_session/clear/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'clear'}),
    url(r'^auth_session/clear_expired/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'clear_expired'}),
    url(r'^auth_session/tran_delete/$', AuthSessionList.as_view(),
        {'MIME_TYPE': 'tran_delete'}),
    url(r'^auth_session/(?P<pk>.*)/$', AuthSessionDetail.as_view()),

    url(r'^auth_user_log/$', AuthUserLogList.as_view()),

    url(r'^microapp_token/connect/$', MicroAppTokenList.as_view(),
        {'MIME_TYPE': 'connect'}),
    url(r'^microapp_token/access_token/$', MicroAppTokenList.as_view(),
        {'MIME_TYPE': 'access_token'}),

    url(r'^sys_book/$', SysBookList.as_view()),
    url(r'^sys_book/class_code/$', SysBookList.as_view(),
        {'MIME_TYPE': 'get_list_class_code'}),

    url(r'^sys_config/$', SysConfigList.as_view()),
)
