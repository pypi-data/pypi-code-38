"""
Url router for the administration site
"""
from django.contrib import admin
from django.conf.urls import url, include
from core_exporters_app.views.admin import views as admin_views, ajax as admin_ajax

admin_urls = [
    url(r'^exporters/(?P<pk>[\w-]+)/edit/$', admin_ajax.EditExporterView.as_view(),
        name='core_exporters_app_exporters_edit'),
    url(r'^exporters/associated-templates', admin_ajax.associated_templates,
        name='core_exporters_app_exporters_associated_templates'),
    url(r'^exporters', admin_views.manage_exporters,
        name='core_exporters_app_exporters'),
    url(r'^xsl', include('core_exporters_app.exporters.xsl.urls')),
]

urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
