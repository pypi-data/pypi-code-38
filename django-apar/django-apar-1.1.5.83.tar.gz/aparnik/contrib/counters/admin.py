# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields

from .models import Counter


# Register your models here.
class CounterAdmin(BaseModelAdmin):
    fields = ['user_obj', 'model_obj', 'action']
    list_display = ['user_obj', 'model_obj', 'action', get_update_at]
    list_filter = ['action', ]
    search_fields = get_user_search_fields('user_obj') + ['model_obj__id']
    exclude = []
    raw_id_fields = ['user_obj', 'model_obj']
    dynamic_raw_id_fields = []
    readonly_fields = ['update_at']

    def __init__(self, *args, **kwargs):
        Klass = CounterAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Counter


admin.site.register(Counter, CounterAdmin)
