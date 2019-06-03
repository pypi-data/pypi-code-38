""" Url router for the curate application
"""
from django.conf.urls import url
from django.core.urlresolvers import reverse_lazy

import core_curate_app.permissions.rights as rights
import core_curate_app.views.user.ajax as user_ajax
import core_curate_app.views.user.views as user_views
import core_curate_registry_app.views.user.views as user_registry_views
import core_curate_registry_app.views.user.ajax as user_registry_ajax
from core_curate_app.views.common import views as common_views
from core_main_app.utils.decorators import permission_required

urlpatterns = [
    url(r'^$', user_registry_views.index,
        name='core_curate_index'),
    url(r'^start_curate$', user_registry_ajax.start_curate,
        name='core_curate_start'),
    url(r'^start_curate/(?P<role>\w+)/$', user_registry_views.start_curate,
        name='core_curate_start_from_role'),
    url(r'^enter-data/(?P<curate_data_structure_id>\w+)$', user_registry_views.EnterDataRegistryView.as_view(),
        name='core_curate_enter_data'),
    # FIXME: url to allow reopening a form with unsaved changes (may be temporary until curate workflow redesign)
    url(r'^enter-data/(?P<curate_data_structure_id>\w+)/(?P<reload_unsaved_changes>\w+)$',
        user_registry_views.EnterDataRegistryView.as_view(),
        name='core_curate_enter_data'),
    url(r'^view-data/(?P<curate_data_structure_id>\w+)$', user_views.view_data,
        name='core_curate_view_data'),
    url(r'^download-xml/(?P<curate_data_structure_id>\w+)$', user_views.download_current_xml,
        name='core_curate_download_xml'),
    url(r'^download-xsd/(?P<curate_data_structure_id>\w+)$', user_views.download_xsd,
        name='core_curate_download_xsd'),
    url(r'^generate-choice/(?P<curate_data_structure_id>\w+)$', user_ajax.generate_choice,
        name='core_curate_generate_choice'),
    url(r'^generate-element/(?P<curate_data_structure_id>\w+)$', user_ajax.generate_element,
        name='core_curate_generate_element'),
    url(r'^remove-element$', user_ajax.remove_element,
        name='core_curate_remove_element'),
    url(r'^clear-fields$', user_ajax.clear_fields,
        name='core_curate_clear_fields'),
    url(r'^cancel-changes$', user_ajax.cancel_changes,
        name='core_curate_cancel_changes'),
    url(r'^cancel-form$', user_ajax.cancel_form,
        name='core_curate_cancel_form'),
    url(r'^save-form$', user_ajax.save_form,
        name='core_curate_save_form'),
    url(r'^save-data$', user_ajax.save_data,
        name='core_curate_save_data'),
    url(r'^validate-form$', user_ajax.validate_form,
        name='core_curate_validate_form'),
    url(r'^view-form/(?P<curate_data_structure_id>\w+)$',
        permission_required(content_type=rights.curate_content_type,
                            permission=rights.curate_access,
                            login_url=reverse_lazy("core_main_app_login"))(common_views.FormView.as_view()),
        name='core_curate_view_form')
]
