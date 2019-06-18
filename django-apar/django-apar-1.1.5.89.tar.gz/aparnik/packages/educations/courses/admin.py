# -*- coding: utf-8 -*-


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.packages.shops.products.admin import ProductAdmin
from aparnik.packages.shops.files.admin import FileAdmin
from .models import Course, CourseFile, CourseSummary, BaseCourse


class CourseFileSortInline(admin.TabularInline):
    model = CourseFile
    fk_name = 'course_obj'
    fields = ['title', 'sort']
    extra = 1


class ParentFilter(admin.SimpleListFilter):
    title = _('Parent Filter')
    parameter_name = 'parent_filter'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(parent_obj__isnull=False)
        elif value == 'No':
            return queryset.filter(parent_obj__isnull=True)
        return queryset


class DependencyFilter(admin.SimpleListFilter):
    title = _('Dependency Filter')
    parameter_name = 'dependency_filter'

    def lookups(self, request, model_admin):
        return (
            ('Yes', 'Yes'),
            ('No', 'No'),
        )

    def queryset(self, request, queryset):
        value = self.value()
        if value == 'Yes':
            return queryset.filter(dependency_obj__isnull=False)
        elif value == 'No':
            return queryset.filter(dependency_obj__isnull=True)
        return queryset


# Register your models here.
class CourseSummaryAdmin(BaseModelAdmin):
    fields = []
    list_display = ['total_time', 'type', 'file_count', 'file_count_preview']
    search_fields = ['total_time', ]
    # raw_id_fields = ['course']
    list_filter = ['type', ]
    exclude = []
    dynamic_raw_id_fields = []
    raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = CourseSummaryAdmin
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
        model = CourseSummary


class BaseCourseAdmin(ProductAdmin):

    fields = ['description', ]
    list_display = []
    list_filter = []
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = []
    raw_id_fields = []
    inlines = []

    def __init__(self, *args, **kwargs):
        Klass = BaseCourseAdmin
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
        model = BaseCourse


class CourseAdmin(BaseCourseAdmin):
    fields = ['banner', 'cover', 'teacher_obj', 'category_obj', 'parent_obj', 'dependency_obj', 'publish_date', 'publish_month', 'publish_week', 'publish_day']
    list_display = ['parent_obj', 'category_obj', 'price_fabric', 'dependency_obj', 'publish_month', 'publish_week', 'publish_day',
                    get_update_at]

    search_fields = ['parent_obj__title', 'category_obj__title']
    list_filter = [ParentFilter, DependencyFilter,]# 'publish_month', 'publish_week', 'publish_day']
    raw_id_fields = []
    exclude = []
    dynamic_raw_id_fields = ['category_obj', 'parent_obj', 'dependency_obj', 'cover', 'banner']
    inlines = [CourseFileSortInline, ]

    def __init__(self, *args, **kwargs):
        Klass = CourseAdmin
        Klass_parent = BaseCourseAdmin

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
        model = Course

    def save_model(self, request, obj, form, change):
        super(CourseAdmin, self).save_model(request, obj, form, change)
        # must after super because first one parent save and set the default value for permission after that save model
        obj.update_needed = True
        obj.save()
        return obj


class CourseFileAdmin(FileAdmin):
    fields = ['course_obj']
    list_display = ['course_obj', 'price', get_update_at, ]
    search_fields = ['course_obj__title', ]
    list_filter = []
    raw_id_fields = ['course_obj', ]
    exclude = []
    dynamic_raw_id_fields = []        # exclude = ('password', 'iv',)
    inlines = []

    def __init__(self, *args, **kwargs):
        Klass = CourseFileAdmin
        Klass_parent = FileAdmin

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
        model = CourseFile

    def save_model(self, request, obj, form, change):
        super(CourseFileAdmin, self).save_model(request, obj, form, change)
        # must after super because first one parent save and set the default value for permission after that save model
        obj.update_needed = True
        obj.save()


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import CourseSegment

    class CourseSegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        raw_id_fields = []
        exclude = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = CourseSegmentAdmin
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
            model = CourseSegment

    admin.site.register(CourseSegment, CourseSegmentAdmin)

admin.site.register(Course, CourseAdmin)
admin.site.register(CourseFile, CourseFileAdmin)
