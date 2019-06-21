# -*- coding: utf-8 -*-

from django.conf import settings
from django.contrib import admin
from django_admin import DeleteOnlyModelAdmin
from django_onerror.models import OnerrorReportInfo


class OnerrorReportInfoAdmin(DeleteOnlyModelAdmin, admin.ModelAdmin):
    list_display = ('lineNo', 'columnNo', 'scriptURI', 'errorMessage', 'stack', 'extra', 'href', 'ua', 'status', 'created_at', 'updated_at')
    search_fields = ('lineNo', 'columnNo', 'scriptURI', 'errorMessage', 'stack', 'extra', 'href', 'ua')


if not hasattr(settings, 'DJANGO_ONERROR_ADMIN_SITE_REGISTER') or settings.DJANGO_ONERROR_ADMIN_SITE_REGISTER:
    admin.site.register(OnerrorReportInfo, OnerrorReportInfoAdmin)
