"""
Url router for the administration site
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from core_dashboard_common_app import constants as dashboard_constants
from core_dashboard_common_app.views.common import views as common_views
from core_dashboard_registry_app.views.common import views as registry_common_views

admin_urls = [
    # Admin
    url(r'^records$', staff_member_required(registry_common_views.DashboardRegistryRecords.as_view(
            allow_change_workspace_if_public=False,
            administration=True,
            template=dashboard_constants.ADMIN_DASHBOARD_TEMPLATE)),
        name='core_dashboard_records'),
    url(r'^forms$', staff_member_required(registry_common_views.DashboardRegistryForms.as_view(
            document=dashboard_constants.FUNCTIONAL_OBJECT_ENUM.FORM,
            administration=True,
            template=dashboard_constants.ADMIN_DASHBOARD_TEMPLATE)),
        name='core_dashboard_forms'),
    url(r'^workspaces$', staff_member_required(common_views.DashboardWorkspaces.as_view(
            administration=True,
            template=dashboard_constants.ADMIN_DASHBOARD_TEMPLATE)),
        name='core_dashboard_workspaces'),
    url(r'^workspace-list-records/(?P<workspace_id>\w+)$',
        staff_member_required(registry_common_views.DashboardRegistryWorkspaceRecords.as_view(
            administration=True,
            template=dashboard_constants.ADMIN_DASHBOARD_TEMPLATE)),
        name='core_dashboard_workspace_list_data'),
]


urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
