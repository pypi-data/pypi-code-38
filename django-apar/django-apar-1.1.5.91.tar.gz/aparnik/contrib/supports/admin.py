# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.users.admin import get_update_at
from .models import Support
from aparnik.contrib.basemodels.admin import BaseModelAdmin
# Register your models here.


class SupportAdmin(BaseModelAdmin):
    fields = ['title', 'online', 'offline', 'phone', 'online_days', 'socials', 'is_active']
    exclude = []
    list_display = ['id', 'title', 'is_active', get_update_at, ]
    search_fields = ['title', ]
    list_filter = ['is_active', 'title']

    def __init__(self, *args, **kwargs):
        Klass = SupportAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields

    class Meta:
        model = Support


admin.site.register(Support, SupportAdmin)
