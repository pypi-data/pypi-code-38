"""Url router for the administration site
"""
from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.core.urlresolvers import reverse_lazy

from core_composer_app.views.admin import views as admin_views, ajax as admin_ajax
from core_composer_app.views.admin.ajax import EditBucketView
from core_main_app.views.common.ajax import EditTemplateVersionManagerView

parser_url = []
if 'core_parser_app' in settings.INSTALLED_APPS:
    from core_parser_app.views.admin import views as admin_parser_views
    parser_url = [
        url(r'^type/modules/(?P<pk>\w+)',
            admin_parser_views.ManageModulesAdminView.as_view(
                back_to_previous_url="admin:core_composer_app_manage_type_versions"
            ),
            name='core_composer_app_type_modules'),
    ]

admin_urls = [
    url(r'^types$', admin_views.manage_types,
        name='core_composer_app_types'),
    url(r'^type/(?P<pk>[\w-]+)/edit/$',
        EditTemplateVersionManagerView.as_view(success_url=reverse_lazy(
            "admin:core_composer_app_types")),
        name='core_composer_app_edit_type'),
    url(r'^type/upload$', admin_views.upload_type,
        name='core_composer_app_upload_type'),
    url(r'^type/upload/(?P<version_manager_id>\w+)', admin_views.upload_type_version,
        name='core_composer_app_upload_type_version'),
    url(r'^type/versions/(?P<version_manager_id>\w+)', admin_views.manage_type_versions,
        name='core_composer_app_manage_type_versions'),
    url(r'^type/buckets/(?P<version_manager_id>\w+)', admin_views.manage_type_buckets,
        name='core_composer_app_type_buckets'),
    url(r'^buckets$', admin_views.manage_buckets,
        name='core_composer_app_buckets'),
    url(r'^bucket/upload$', admin_views.upload_bucket,
        name='core_composer_app_upload_bucket'),
    url(r'^bucket/delete$', admin_ajax.delete_bucket,
        name='core_composer_app_delete_bucket'),
    url(r'^type/resolve-dependencies', admin_ajax.resolve_dependencies,
        name='core_composer_app_resolve_dependencies'),
    url(r'^bucket/(?P<pk>[\w-]+)/edit/$',
        EditBucketView.as_view(),
        name='core_composer_app_edit_bucket'),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls + parser_url
