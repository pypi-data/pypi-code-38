# -*- coding: utf-8 -*-


from django.contrib import admin
from jalali_date.admin import ModelAdminJalaliMixin
from aparnik.utils.utils import is_app_installed
from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.packages.shops.files.admin import FileAdmin
from .models import Book, Publisher, WriterTranslator


# Register your models here.
class WriterTranslatorAdmin(BaseModelAdmin):
    list_display = ['first_name', 'last_name', get_update_at, ]
    search_fields = ['id', 'first_name', 'last_name', ]
    list_filter = ['created_at', ]
    fields = ['first_name', 'last_name']
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = WriterTranslatorAdmin
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
        model = WriterTranslator


class PublisherAdmin(BaseModelAdmin):
    list_display = ['title', get_update_at, ]
    search_fields = ['title', ]
    list_filter = ['created_at', ]
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []
    fields = ['title']

    def __init__(self, *args, **kwargs):
        Klass = PublisherAdmin
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
        model = Publisher


class BookAdmin(FileAdmin):
    fields = ['sample_book', 'published_date', 'category_obj', 'publisher_obj', 'writers_obj', 'translators_obj', ]
    list_display = [get_update_at, ]
    search_fields = []
    list_filter = ['created_at', ]
    raw_id_fields = ['category_obj', 'publisher_obj', 'sample_book']
    exclude = []
    dynamic_raw_id_fields = []    

    def __init__(self, *args, **kwargs):
        Klass = BookAdmin
        Klass_parent = FileAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields        
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Book


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import BookSegment

    class BookSegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        raw_id_fields = []
        exclude = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = BookSegmentAdmin
            Klass_parent = SegmentAdmin

            super(Klass, self).__init__(*args, **kwargs)
            self.fields = Klass_parent.fields + self.fields
            self.list_display = Klass_parent.list_display + self.list_display
            self.list_filter = Klass_parent.list_filter + self.list_filter
            self.search_fields = Klass_parent.search_fields + self.search_fields
            self.exclude = Klass_parent.exclude + self.exclude
            self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
            self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

        class Meta:
            model = BookSegment


    admin.site.register(BookSegment, BookSegmentAdmin)

admin.site.register(Book, BookAdmin)
admin.site.register(WriterTranslator, WriterTranslatorAdmin)
admin.site.register(Publisher, PublisherAdmin)

