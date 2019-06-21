# -*- coding: utf-8 -*-


from django.contrib import admin
from django.conf import settings

from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from .models import Page


# Register your models here.
class SegmentSortInline(BaseModelTabularInline):
    model = Page.segment_pages.through
    fields = ('segment_obj', 'sort')
    raw_id_fields = ('segment_obj',)
    extra = 1
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = SegmentSortInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude




class PageAdmin(BaseModelAdmin):
    fields = ['title', 'english_title', 'is_show_in_home']
    list_display = ['title', get_update_at]
    search_fields = ['title', ]
    list_filter = ['created_at']
    raw_id_fields = []
    exclude = []
    dynamic_raw_id_fields = []
    inlines = [SegmentSortInline]

    def __init__(self, *args, **kwargs):
        Klass = PageAdmin
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
        model = Page
    # search_fields = ['email', 'article']
    # list_filter = ['email', 'article', 'created_at']
    # readonly_fields = []
    # actions = []


admin.site.register(Page, PageAdmin)
# admin.site.register(CategoryCourse, CategoryCourseAdmin)
# admin.site.register(CategoryLibrary, CategoryLibraryAdmin)
