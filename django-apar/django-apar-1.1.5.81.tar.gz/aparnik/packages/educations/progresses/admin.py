# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.packages.educations.progresses.models import Progresses, ProgressSummary
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields


# Register your models here.
class ProgressesAdmin(BaseModelAdmin):
    list_display = ['user_obj', 'file_obj', 'status', 'is_published']
    list_filter = ['status', 'created_at']
    search_fields = get_user_search_fields('user_obj') + ['file_obj__title']
    raw_id_fields = ['user_obj', 'file_obj']
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = ProgressesAdmin
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
        model = Progresses


class ProgressesSummaryAdmin(BaseModelAdmin):
    list_display = ['user_obj', 'percentage', 'model']
    list_filter = []
    search_fields = get_user_search_fields('user_obj') + ['user_obj__title']
    raw_id_fields = ['user_obj', ]
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = ProgressesSummaryAdmin
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
        model = ProgressSummary


admin.site.register(Progresses, ProgressesAdmin)
admin.site.register(ProgressSummary, ProgressesSummaryAdmin)
