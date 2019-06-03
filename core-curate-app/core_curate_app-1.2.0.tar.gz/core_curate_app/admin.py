"""
Url router for the administration site
"""
from django.conf.urls import url
from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required

from core_curate_app.views.common import views as common_views

admin_urls = [
    url(r'^view-form/(?P<curate_data_structure_id>\w+)$', staff_member_required(common_views.FormView.as_view(
        administration=True,
        template='core_curate_app/admin/view_curate_data_structure.html')),
        name='core_curate_view_form')
]


urls = admin.site.get_urls()
admin.site.get_urls = lambda: admin_urls + urls
