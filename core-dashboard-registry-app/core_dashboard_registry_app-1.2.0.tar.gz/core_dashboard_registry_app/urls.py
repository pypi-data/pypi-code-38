"""
    Url router for the user dashboard
"""
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy

from core_dashboard_common_app import constants as dashboard_constants
from core_dashboard_common_app.views.common import ajax, views as common_views
from core_dashboard_common_app.views.common.views import UserDashboardPasswordChangeFormView
from core_dashboard_registry_app.views.common import ajax as registry_common_ajax
from core_dashboard_registry_app.views.common import views as registry_common_views

urlpatterns = [
    # Common
    url(r'^$', registry_common_views.home, name='core_dashboard_home'),
    url(r'^my-profile$', common_views.my_profile, name='core_dashboard_profile'),
    url(r'^my-profile/edit$', common_views.my_profile_edit, name='core_dashboard_profile_edit'),
    url(r'^my-profile/change-password', UserDashboardPasswordChangeFormView.as_view(
        template_name='core_dashboard_common_app/my_profile_change_password.html', success_url='/'),
        name='core_dashboard_profile_change_password'),

    url(r'^delete-document', ajax.delete_document, name='core_dashboard_delete_document'),
    url(r'^change-owner', ajax.change_owner_document, name='core_dashboard_change_owner_document'),
    url(r'^edit-record', ajax.edit_record, name='core_dashboard_edit_record'),

    # User
    url(r'^records$', login_required(registry_common_views.DashboardRegistryRecords.as_view(
        document=dashboard_constants.FUNCTIONAL_OBJECT_ENUM.RECORD,
        data_template='core_dashboard_registry_app/list/my_dashboard_my_records_table_pagination.html',
        allow_change_workspace_if_public=False,
    ), login_url=reverse_lazy("core_main_app_login")), name='core_dashboard_records'),
    url(r'^switch-status-record', registry_common_ajax.switch_data_status,
        name='core_dashboard_switch_status_record'),
    url(r'^forms$', login_required(registry_common_views.DashboardRegistryForms.as_view(
        document=dashboard_constants.FUNCTIONAL_OBJECT_ENUM.FORM
    ), login_url=reverse_lazy("core_main_app_login")), name='core_dashboard_forms'),
    url(r'^workspaces$', login_required(common_views.DashboardWorkspaces.as_view(
    ), login_url=reverse_lazy("core_main_app_login")), name='core_dashboard_workspaces'),
    url(r'^workspace-list-records/(?P<workspace_id>\w+)$',
        login_required(registry_common_views.DashboardRegistryWorkspaceRecords.as_view(
            data_template='core_dashboard_registry_app/list/my_dashboard_my_records_table_pagination.html'),
            login_url=reverse_lazy("core_main_app_login")), name='core_dashboard_workspace_list_data'),

    url(r'^publish-resource', registry_common_ajax.publish, name='core_dashboard_publish_resource_registry'),
]
