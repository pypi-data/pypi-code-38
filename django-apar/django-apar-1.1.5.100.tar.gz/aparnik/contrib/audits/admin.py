# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields
from .models import Audit


class AuditAdmin(BaseModelAdmin):
    fields = ['action', 'ip', 'user_obj', 'extra']
    list_display = ['action', 'ip', 'user_obj', 'created_at']
    search_fields = get_user_search_fields('user_obj') + ['ip', 'user_obj', 'extra', ]
    list_filter = ['action']
    raw_id_fields = ['user_obj']
    exclude = []
    dynamic_raw_id_fields = []        # exclude = ('password', 'iv',)
    inlines = []

    def __init__(self, *args, **kwargs):
        Klass = AuditAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields
        self.inlines = Klass_parent.inlines + self.inlines

    class Meta:
        model = Audit


admin.site.register(Audit, AuditAdmin)
