from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from . import models


class GeobaseAdmin(MPTTModelAdmin):
    mptt_level_indent = 20
    list_display = ('ru', 'type')


admin.site.register(models.Geobase, GeobaseAdmin)
