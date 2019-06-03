"""
Url router for the administration views
"""
from django.contrib import admin
from django.conf.urls import url
from core_parser_app.views.admin import views as admin_views

admin_urls = [
    url(r'^template/modules/(?P<pk>\w+)',
        admin_views.ManageModulesAdminView.as_view(
            back_to_previous_url="admin:core_main_app_manage_template_versions",
        ),
        name='core_parser_app_template_modules'),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
