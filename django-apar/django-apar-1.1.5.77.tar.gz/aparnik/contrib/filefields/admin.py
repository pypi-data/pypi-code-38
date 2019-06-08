# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.settings import aparnik_settings

from .models import FileField


class FileFieldAdmin(BaseModelAdmin):

    fields = ['title', 'is_encrypt_needed']
    list_display = ['title', 'type', 'is_lock', 'is_encrypt_needed', 'seconds', 'file_size_readable']
    list_filter = ['type', 'is_lock', 'is_encrypt_needed']
    search_fields = ['title', 'type']
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    readonly_fields = ()

    def __init__(self, *args, **kwargs):
        Klass = FileFieldAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

        if aparnik_settings.AWS_ACTIVE:
            file_field_name = ['file_s3', 'size', 'type', 'password', 'iv']
        else:
            file_field_name = ['file_direct']

        self.fields = self.fields + file_field_name
        self.list_display = self.list_display + file_field_name

    class Meta:
        model = FileField


admin.site.register(FileField, FileFieldAdmin)