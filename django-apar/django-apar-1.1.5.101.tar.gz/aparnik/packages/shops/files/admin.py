# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.packages.shops.products.admin import ProductAdmin
from .models import File
# from questionsanswer.models import QA, Like


class FileAdmin(ProductAdmin):

    fields = ['description', 'file_obj', 'banner', 'cover', 'publish_date']
    list_display = []
    list_filter = []
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = []
    inlines = []
    raw_id_fields = ['file_obj', 'cover', 'banner']

    def __init__(self, *args, **kwargs):
        Klass = FileAdmin
        Klass_parent = ProductAdmin

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
        model = File


admin.site.register(File, FileAdmin)
