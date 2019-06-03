"""Url router for the REST API
"""
from django.conf.urls import url

from core_composer_app.rest.bucket import views as bucket_views
from core_composer_app.rest.type_version_manager import views as type_version_manager_views
from core_main_app.rest.template import views as template_views
from core_main_app.rest.template_version_manager import views as template_version_manager_views

urlpatterns = [
    url(r'^type-version-manager/global/$',
        type_version_manager_views.GlobalTypeVersionManagerList.as_view(),
        name='core_composer_app_rest_type_version_manager_global_list'),

    url(r'^type-version-manager/user/$',
        type_version_manager_views.UserTypeVersionManagerList.as_view(),
        name='core_composer_app_rest_type_version_manager_user_list'),

    url(r'^type-version-manager/(?P<pk>\w+)/$',
        template_version_manager_views.TemplateVersionManagerDetail.as_view(),
        name='core_composer_app_rest_type_version_manager_detail'),

    url(r'^type-version-manager/(?P<pk>\w+)/disable/$',
        template_version_manager_views.DisableTemplateVersionManager.as_view(),
        name='core_composer_app_rest_type_version_manager_disable'),

    url(r'^type-version-manager/(?P<pk>\w+)/restore/$',
        template_version_manager_views.RestoreTemplateVersionManager.as_view(),
        name='core_composer_app_rest_type_version_manager_restore'),

    url(r'^type/version/(?P<pk>\w+)/current/$',
        template_version_manager_views.CurrentTemplateVersion.as_view(),
        name='core_composer_app_rest_type_version_current'),

    url(r'^type/version/(?P<pk>\w+)/disable/$',
        template_version_manager_views.DisableTemplateVersion.as_view(),
        name='core_composer_app_rest_type_version_disable'),

    url(r'^type/global/$',
        type_version_manager_views.GlobalTypeList.as_view(),
        name='core_composer_app_rest_global_type_list'),

    url(r'^type/$',
        type_version_manager_views.UserTypeList.as_view(),
        name='core_composer_app_rest_user_type_list'),

    url(r'^type/version/(?P<pk>\w+)/restore/$',
        template_version_manager_views.RestoreTemplateVersion.as_view(),
        name='core_composer_app_rest_type_version_restore'),

    url(r'^type/(?P<pk>\w+)/download/$', template_views.TemplateDownload.as_view(),
        name='core_composer_app_rest_type_download'),

    url(r'^type/(?P<pk>\w+)/$', template_views.TemplateDetail.as_view(),
        name='core_composer_app_rest_type_detail'),

    url(r'^bucket/$',
        bucket_views.BucketList.as_view(),
        name='core_composer_app_rest_bucket_list'),

    url(r'^bucket/(?P<pk>\w+)/$',
        bucket_views.BucketDetail.as_view(),
        name='core_composer_app_rest_bucket_detail'),

    url(r'^buckets/type-version-manager/(?P<pk>\w+)/$',
        bucket_views.TypeVersionManagerBuckets.as_view(),
        name='core_composer_app_rest_type_version_manger_buckets'),
]
