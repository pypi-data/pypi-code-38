from django.contrib import admin

from . import models


class CertificationGroupAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'description', '_type',
        'design_id', 'accredible_id',
        'status', 'created_by', 'created',
    )
    list_filter = ('_type', 'status')
    search_fields = ('name', 'description')


class CertificationCredentialAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'group', 'accredible_id', 'accredible_url', 'issued_on',
        'status', 'created',
    )
    list_filter = ('status',)


admin.site.register(models.CertificationGroup, CertificationGroupAdmin)
admin.site.register(models.CertificationCredential, CertificationCredentialAdmin)
