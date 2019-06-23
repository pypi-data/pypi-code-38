# -*- coding: utf-8 -*-


from django.contrib import admin
from django.conf import settings
from jalali_date import datetime2jalali

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from .models import Category


# Register your models here.
def get_created_at(obj):
    return datetime2jalali(obj.created_at).strftime(settings.JALALI_FORMAT)


#
# class CategoryAdmin(admin.ModelAdmin):
#     # fields = ['title', 'description', 'image', 'parent_obj']
#     list_display = ['title', 'parent_obj', get_created_at]
#
#     # search_fields = ['email', 'article', 'created_at']
#     # list_filter = ['email', 'article', 'created_at']
#     # readonly_fields = []
#     # actions = []
#
#     class Meta:
#         Category
class CategoryAdmin(BaseModelAdmin):
    fields = ['title', 'description', 'image', 'parent_obj']
    list_display = ['title', 'parent_obj', get_created_at]
    search_fields = ['title', 'parent_obj__title']
    list_filter = ['parent_obj', 'created_at']
    raw_id_fields = ['image', 'parent_obj']
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = CategoryAdmin
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
        model = Category
    # search_fields = ['email', 'article']
    # list_filter = ['email', 'article', 'created_at']
    # readonly_fields = []
    # actions = []


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import CategorySegment

    class CategorySegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        raw_id_fields = []
        exclude = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = CategorySegmentAdmin
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
            model = CategorySegment


    admin.site.register(CategorySegment, CategorySegmentAdmin)

admin.site.register(Category, CategoryAdmin)
# admin.site.register(CategoryCourse, CategoryCourseAdmin)
# admin.site.register(CategoryLibrary, CategoryLibraryAdmin)
