from django.contrib import admin

from .admin_site import edc_reference_admin
from .models import Reference


@admin.register(Reference, site=edc_reference_admin)
class ReferenceAdmin(admin.ModelAdmin):

    list_display = ("identifier", "model", "report_datetime", "timepoint", "field_name")
    list_filter = ("model", "timepoint", "field_name")
    search_fields = ("identifier",)
