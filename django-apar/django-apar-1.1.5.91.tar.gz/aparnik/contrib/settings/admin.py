# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from .models import Setting


# Register your models here.
class SettingAdmin(BaseModelAdmin):

    fields = ['title', 'key', 'value', 'value_type', 'package_name', 'function_name', 'is_show', 'is_variable_in_home', ]
    list_display = ['title', 'key', 'value', 'value_type', 'is_show', 'is_variable_in_home', get_update_at]
    search_fields = [get_update_at, 'key']
    list_filter = []
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    class Meta:
        model = Setting

    def __init__(self, *args, **kwargs):
        Klass = SettingAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    def get_queryset(self, request):
        qs = super(SettingAdmin, self).get_queryset(request)
        if not request.user.is_superuser:
            return qs.filter(is_show=True)
        return qs


admin.site.register(Setting, SettingAdmin)
