# -*- coding: utf-8 -*-


from django import forms
from django.forms.models import BaseInlineFormSet
from django.contrib import admin
from django.apps import apps

from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from .models import BaseSegment


class SegmentSortInline(BaseModelTabularInline):
    model = BaseSegment.model_obj.through
    fields = ('model_obj', 'sort')
    extra = 1
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = SegmentSortInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude

    # def get_field_queryset(self, db, db_field, request):
    #     if db_field == 'model_obj':
    #         return
    def formfield_for_foreignkey(self, db_field, request=None, **kwargs):
        """enable ordering drop-down alphabetically"""
        if db_field.name == 'model_obj':
            try:
                sp = self.parent_model._meta.label.split('.')
                app_label = sp[0]
                class_name = sp[1].replace('Segment', '')
                Model = apps.get_model(app_label, class_name)
                kwargs['queryset'] = Model.objects.active()
            except Exception:
                pass
        return super(SegmentSortInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class PageSortInline(BaseModelTabularInline):
    model = BaseSegment.pages.through
    fields = ('page_obj', 'sort')
    raw_id_fields = ('page_obj',)
    extra = 1
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = PageSortInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude



class SegmentAdmin(BaseModelAdmin):
    # fields = ['title', 'model_obj', 'is_active', 'is_home', 'is_library', 'sort', ]
    fields = ['title', ]
    list_display = ['title', get_update_at, ]
    search_fields = ['id', 'model_obj__id', 'title', ]
    # list_filter = ['is_active', 'is_home', 'is_library', 'created_at', ]
    list_filter = ['is_active', 'created_at', ]
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    inlines = (PageSortInline, SegmentSortInline)

    def __init__(self, *args, **kwargs):
        Klass = SegmentAdmin
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
        model = BaseSegment

    # def get_formsets_with_inlines(self, request, obj=None):
    #     for inline in self.get_inline_instances(request, obj):
    #         if isinstance(inline, SegmentSortInline):
    #             from aparnik.packages.educations.courses.models import Course
    #             if hasattr(inline.form.base_fields, 'model_obj'):
    #                 inline.form.base_fields['model_obj'].queryset = Course.objects.all()
    #         yield inline.get_formset(request, obj), inline

    # def get_formsets_with_inlines(self, request, obj=None):
    #     for inline in self.get_inline_instances(request, obj):
    #         # hide MyInline in the add view
    #         formset = None
    #         if isinstance(inline, SegmentSortInline):
    #             try:
    #                 sp = type(self).Meta.model._meta.label.split('.')
    #                 app_label = sp[0]
    #                 class_name = sp[1].replace('Segment', '')
    #                 Model = apps.get_model(app_label, class_name)
    #                 formset = inline.get_formset(request, obj, model_querysey=Model.objects.active())
    #             except Exception:
    #                 pass
    #         if not formset:
    #             formset = inline.get_formset(request, obj)
    #         yield formset, inline


admin.site.register(BaseSegment, SegmentAdmin)
# admin.site.register(SegmentReview, SegmentReviewAdmin)
# admin.site.register(SegmentCourse, SegmentCourseAdmin)
# admin.site.register(SegmentLibrary, SegmentLibraryAdmin)
