# -*- coding: utf-8 -*-

from django.conf.urls import patterns, url

from bigtiger.contrib.admin.views.auth_user import (
    AuthUserListView, AuthUserAddView, AuthUserEditView, 
    AuthUserDeleteView, AuthUserDetailView)

from bigtiger.contrib.admin.views.auth_group import (
    AuthGroupListView, AuthGroupDeleteView, AuthGroupAddView,
    AuthGroupEditView, AuthGroupDetailView)

from bigtiger.contrib.admin.views.auth_permission import (
    AuthPermissionListView, AuthPermissionDeleteView, AuthPermissionAddView,
    AuthPermissionEditView, AuthPermissionDetailView, AuthPermissionTreeView)

from bigtiger.contrib.admin.views.auth_user_log import AuthUserLogListView, AuthUserLogDetailView

from bigtiger.contrib.admin.views.auth_session import (
    AuthSessionListView, AuthSessionDeleteView, AuthSessionDetailView)

from bigtiger.contrib.admin.views.microapp_app import (
    MicroappAppListView, MicroappAppDeleteView, MicroappAppAddView,
    MicroappAppEditView, MicroappAppDetailView)

from bigtiger.contrib.admin.views.microapp_token import (
    MicroappTokenListView, MicroappTokenDeleteView, MicroappTokenAddView,
    MicroappTokenEditView, MicroappTokenDetailView)

from bigtiger.contrib.admin.views.sys_config import (
    SysConfigListView, SysConfigDeleteView, SysConfigAddView,
    SysConfigEditView, SysConfigDetailView)

from bigtiger.contrib.admin.views.sys_guest import (
    SysGuestListView, SysGuestDeleteView, SysGuestAddView,
    SysGuestEditView, SysGuestDetailView)

from bigtiger.contrib.admin.views.sys_cover import (
    SysCoverListView, SysCoverDeleteView, SysCoverAddView,
    SysCoverEditView, SysCoverDetailView)

from bigtiger.contrib.admin.views.sys_book import (
    SysBookListView, SysBookDeleteView, SysBookAddView,
    SysBookEditView, SysBookDetailView)

from bigtiger.contrib.admin.views.sys_update_log import (
    SysUpdateLogListView, SysUpdateLogDeleteView, SysUpdateLogAddView,
    SysUpdateLogEditView, SysUpdateLogDetailView)

from bigtiger.contrib.admin.views.sys_blacklist import (
    SysBlacklistListView, SysBlacklistDeleteView, SysBlacklistAddView,
    SysBlacklistEditView, SysBlacklistDetailView)


urlpatterns = patterns(
    'admin.views',

    url(r'^auth_user/$', AuthUserListView.as_view(), name='auth_user-list'),
    url(r'^auth_user/json/$', AuthUserListView.as_view(),
        {'MIME_TYPE': 'json'}, name='auth_user-json'),
    url(r'^auth_user/(?P<pk>.*)/detail/$',
        AuthUserDetailView.as_view(), name='auth_user-detail'),
    url(r'^auth_user/(?P<pk>.*)/delete/$',
        AuthUserDeleteView.as_view(), name='auth_user-delete'),
    url(r'^auth_user/add/$', AuthUserAddView.as_view(), name='auth_user-add'),
    url(r'^auth_user/(?P<pk>.*)/$',
        AuthUserEditView.as_view(), name='auth_user-edit'),

    url(r'^auth_group/$', AuthGroupListView.as_view(), name='auth_group-list'),
    url(r'^auth_group/json/$', AuthGroupListView.as_view(),
        {'MIME_TYPE': 'json'}, name='auth_group-json'),
    url(r'^auth_group/(?P<pk>.*)/detail/$',
        AuthGroupDetailView.as_view(), name='auth_group-detail'),
    url(r'^auth_group/(?P<pk>.*)/delete/$',
        AuthGroupDeleteView.as_view(), name='auth_group-delete'),
    url(r'^auth_group/add/$', AuthGroupAddView.as_view(), name='auth_group-add'),
    url(r'^auth_group/(?P<pk>.*)/$',
        AuthGroupEditView.as_view(), name='auth_group-edit'),

    url(r'^auth_permission/$', AuthPermissionListView.as_view(),
        name='auth_permission-list'),
    url(r'^auth_permission/json/$', AuthPermissionListView.as_view(),
        {'MIME_TYPE': 'json'}, name='auth_permission-json'),
    url(r'^auth_permission/tree/json/$', AuthPermissionTreeView.as_view(),
        {'MIME_TYPE': 'json'}, name='auth_permission-treejson'),
    url(r'^auth_permission/(?P<pk>.*)/detail/$',
        AuthPermissionDetailView.as_view(), name='auth_permission-detail'),
    url(r'^auth_permission/(?P<pk>.*)/delete/$',
        AuthPermissionDeleteView.as_view(), name='auth_permission-delete'),
    url(r'^auth_permission/add/$', AuthPermissionAddView.as_view(),
        name='auth_permission-add'),
    url(r'^auth_permission/(?P<pk>.*)/$',
        AuthPermissionEditView.as_view(), name='auth_permission-edit'),

    url(r'^auth_user_log/$', AuthUserLogListView.as_view(),
        name='auth_user_log-list'),
    url(r'^auth_user_log/json/$', AuthUserLogListView.as_view(),
        {'MIME_TYPE': 'json'}, name='auth_user_log-json'),
    url(r'^auth_user_log/(?P<pk>.*)/detail/$',
        AuthUserLogDetailView.as_view(), name='auth_user_log-detail'),

    url(r'^auth_session/$', AuthSessionListView.as_view(), name='auth_session-list'),
    url(r'^auth_session/json/$', AuthSessionListView.as_view(),
        {'MIME_TYPE': 'json'}, name='auth_session-json'),
    url(r'^auth_session/(?P<pk>.*)/detail/$',
        AuthSessionDetailView.as_view(), name='auth_session-detail'),
    url(r'^auth_session/(?P<pk>.*)/delete/$',
        AuthSessionDeleteView.as_view(), {'MIME_TYPE': 'delete'}, name='auth_session-delete'),
    url(r'^auth_session/clear_expired/$',
        AuthSessionDeleteView.as_view(), {'MIME_TYPE': 'clear_expired'}, name='auth_session-clear_expired'),

    url(r'^microapp_app/$', MicroappAppListView.as_view(), name='microapp_app-list'),
    url(r'^microapp_app/json/$', MicroappAppListView.as_view(),
        {'MIME_TYPE': 'json'}, name='microapp_app-json'),
    url(r'^microapp_app/(?P<pk>.*)/detail/$',
        MicroappAppDetailView.as_view(), name='microapp_app-detail'),
    url(r'^microapp_app/(?P<pk>.*)/delete/$',
        MicroappAppDeleteView.as_view(), name='microapp_app-delete'),
    url(r'^microapp_app/add/$', MicroappAppAddView.as_view(), name='microapp_app-add'),
    url(r'^microapp_app/(?P<pk>.*)/$',
        MicroappAppEditView.as_view(), name='microapp_app-edit'),

    url(r'^microapp_token/$', MicroappTokenListView.as_view(),
        name='microapp_token-list'),
    url(r'^microapp_token/json/$', MicroappTokenListView.as_view(),
        {'MIME_TYPE': 'json'}, name='microapp_token-json'),
    url(r'^microapp_token/(?P<pk>.*)/detail/$',
        MicroappTokenDetailView.as_view(), name='microapp_token-detail'),
    url(r'^microapp_token/(?P<pk>.*)/delete/$',
        MicroappTokenDeleteView.as_view(), name='microapp_token-delete'),
    url(r'^microapp_token/add/$', MicroappTokenAddView.as_view(),
        name='microapp_token-add'),
    url(r'^microapp_token/(?P<pk>.*)/$',
        MicroappTokenEditView.as_view(), name='microapp_token-edit'),

    url(r'^sys_config/$', SysConfigListView.as_view(), name='sys_config-list'),
    url(r'^sys_config/json/$', SysConfigListView.as_view(),
        {'MIME_TYPE': 'json'}, name='sys_config-json'),
    url(r'^sys_config/(?P<pk>.*)/detail/$',
        SysConfigDetailView.as_view(), name='sys_config-detail'),
    url(r'^sys_config/(?P<pk>.*)/delete/$',
        SysConfigDeleteView.as_view(), name='sys_config-delete'),
    url(r'^sys_config/add/$', SysConfigAddView.as_view(), name='sys_config-add'),
    url(r'^sys_config/(?P<pk>.*)/$',
        SysConfigEditView.as_view(), name='sys_config-edit'),

    url(r'^sys_guest/$', SysGuestListView.as_view(), name='sys_guest-list'),
    url(r'^sys_guest/json/$', SysGuestListView.as_view(),
        {'MIME_TYPE': 'json'}, name='sys_guest-json'),
    url(r'^sys_guest/(?P<pk>.*)/detail/$',
        SysGuestDetailView.as_view(), name='sys_guest-detail'),
    url(r'^sys_guest/(?P<pk>.*)/delete/$',
        SysGuestDeleteView.as_view(), name='sys_guest-delete'),
    url(r'^sys_guest/add/$', SysGuestAddView.as_view(), name='sys_guest-add'),
    url(r'^sys_guest/(?P<pk>.*)/$',
        SysGuestEditView.as_view(), name='sys_guest-edit'),

    url(r'^sys_cover/$', SysCoverListView.as_view(), name='sys_cover-list'),
    url(r'^sys_cover/json/$', SysCoverListView.as_view(),
        {'MIME_TYPE': 'json'}, name='sys_cover-json'),
    url(r'^sys_cover/(?P<pk>.*)/detail/$',
        SysCoverDetailView.as_view(), name='sys_cover-detail'),
    url(r'^sys_cover/(?P<pk>.*)/delete/$',
        SysCoverDeleteView.as_view(), name='sys_cover-delete'),
    url(r'^sys_cover/add/$', SysCoverAddView.as_view(), name='sys_cover-add'),
    url(r'^sys_cover/(?P<pk>.*)/$',
        SysCoverEditView.as_view(), name='sys_cover-edit'),

    url(r'^sys_book/$', SysBookListView.as_view(), name='sys_book-list'),
    url(r'^sys_book/json/$', SysBookListView.as_view(),
        {'MIME_TYPE': 'json'}, name='sys_book-json'),
    url(r'^sys_book/(?P<pk>.*)/detail/$',
        SysBookDetailView.as_view(), name='sys_book-detail'),
    url(r'^sys_book/(?P<pk>.*)/delete/$',
        SysBookDeleteView.as_view(), name='sys_book-delete'),
    url(r'^sys_book/add/$', SysBookAddView.as_view(), name='sys_book-add'),
    url(r'^sys_book/(?P<pk>.*)/$', SysBookEditView.as_view(), name='sys_book-edit'),

    url(r'^sys_update_log/$', SysUpdateLogListView.as_view(),
        name='sys_update_log-list'),
    url(r'^sys_update_log/json/$', SysUpdateLogListView.as_view(),
        {'MIME_TYPE': 'json'}, name='sys_update_log-json'),
    url(r'^sys_update_log/(?P<pk>.*)/detail/$',
        SysUpdateLogDetailView.as_view(), name='sys_update_log-detail'),
    url(r'^sys_update_log/(?P<pk>.*)/delete/$',
        SysUpdateLogDeleteView.as_view(), name='sys_update_log-delete'),
    url(r'^sys_update_log/add/$', SysUpdateLogAddView.as_view(),
        name='sys_update_log-add'),
    url(r'^sys_update_log/(?P<pk>.*)/$',
        SysUpdateLogEditView.as_view(), name='sys_update_log-edit'),

    url(r'^sys_blacklist/$', SysBlacklistListView.as_view(),
        name='sys_blacklist-list'),
    url(r'^sys_blacklist/json/$', SysBlacklistListView.as_view(),
        {'MIME_TYPE': 'json'}, name='sys_blacklist-json'),
    url(r'^sys_blacklist/(?P<pk>.*)/detail/$',
        SysBlacklistDetailView.as_view(), name='sys_blacklist-detail'),
    url(r'^sys_blacklist/(?P<pk>.*)/delete/$',
        SysBlacklistDeleteView.as_view(), name='sys_blacklist-delete'),
    url(r'^sys_blacklist/add/$', SysBlacklistAddView.as_view(),
        name='sys_blacklist-add'),
    url(r'^sys_blacklist/(?P<pk>.*)/$',
        SysBlacklistEditView.as_view(), name='sys_blacklist-edit'),
)
