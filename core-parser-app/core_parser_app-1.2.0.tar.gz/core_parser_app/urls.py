""" Url router for the parser application
"""
from django.conf.urls import url, include
from core_parser_app.views.user import ajax as user_ajax
from core_parser_app.views.common import views as common_views, ajax as common_ajax

urlpatterns = [
    url(r'^data-structure-element/value', user_ajax.data_structure_element_value,
        name='core_parser_app_data_structure_element_value'),
    url(r'^template/modules/(?P<pk>\w+)',
        common_views.ManageModulesUserView.as_view(
            back_to_previous_url="core_main_app_manage_template_versions",
        ),
        name='core_parser_app_template_modules'),
    url(r'^template/module/delete', common_ajax.delete_module,
        name='core_parser_app_delete_template_module'),
    url(r'^template/module/insert', common_ajax.insert_module,
        name='core_parser_app_insert_template_module'),

    url(r'^modules/', include('core_parser_app.tools.modules.urls')),
]
