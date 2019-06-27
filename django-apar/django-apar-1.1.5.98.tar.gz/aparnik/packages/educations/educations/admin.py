# -*- coding: utf-8 -*-


from django.contrib import admin

from jalali_date import datetime2jalali

from aparnik.settings import aparnik_settings
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelStackedInline
from aparnik.contrib.users.admin import get_user_search_fields
from .models import BaseEducation, Education, Degree, FieldSubject, Institute, CityInstitute


# Register your models here.
class BaseEducationInline(BaseModelStackedInline):
    model = BaseEducation
    extra = 1
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = BaseEducationInline
        Klass_parent = BaseModelStackedInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


    def get_queryset(self, request):
        return BaseEducation.objects.all()


#
class CityInline(BaseModelStackedInline):
    model = CityInstitute
    fk_name = 'Institute'
    extra = 1
    max_num = 1
    exclude = []
    raw_id_fields = ['city']
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = CityInline
        Klass_parent = BaseModelStackedInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


def get_receive_date(obj):
    if obj.receive_date:
        return datetime2jalali(obj.receive_date).strftime(aparnik_settings.JALALI_FORMAT)
    return obj.receive_date


class EducationAdmin(BaseModelAdmin):
    fields = ['user_obj', 'degree_obj', 'institute_obj', 'field_subject_obj']
    list_display = ['user_obj', 'degree_obj', get_receive_date]
    list_filter = []
    search_fields = get_user_search_fields('user_obj')
    exclude = []
    dynamic_raw_id_fields = []
    raw_id_fields = ['user_obj', 'degree_obj', 'institute_obj', 'field_subject_obj']

    def __init__(self, *args, **kwargs):
        Klass = EducationAdmin
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
        model = Education


class DegreeAdmin(BaseModelAdmin):
    fields = []
    list_display = ['name']
    list_filter = []
    search_fields = []
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = DegreeAdmin
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
        model = Degree


class FieldSubjectAdmin(BaseModelAdmin):
    fields = []
    list_display = ['name']
    list_filter = []
    search_fields = []
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = FieldSubjectAdmin
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
        model = FieldSubject


class InstituteAdmin(BaseModelAdmin):
    fields = []
    list_display = ['name']
    list_filter = []
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = ['cities']
    raw_id_fields = []
    inlines = [
        CityInline,
    ]

    def __init__(self, *args, **kwargs):
        Klass = InstituteAdmin
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
        model = Institute


admin.site.register(Education, EducationAdmin)
admin.site.register(Degree, DegreeAdmin)
admin.site.register(FieldSubject, FieldSubjectAdmin)
admin.site.register(Institute, InstituteAdmin)
