# -*- coding: utf-8 -*-


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from jalali_date.admin import ModelAdminJalaliMixin
from jalali_date import datetime2jalali

from aparnik.settings import aparnik_settings
from aparnik.contrib.users import admin as aparnik_admin
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelStackedInline
from aparnik.contrib.users.admin import get_user_search_fields
from .models import Teacher, Dossier

# Register your models here.


def get_start_date(obj):
    if obj.start_date:
        return datetime2jalali(obj.start_date).strftime(aparnik_settings.JALALI_FORMAT)
    return obj.start_date


def get_finish_date(obj):
    if obj.finish_date:
        return datetime2jalali(obj.finish_date).strftime(aparnik_settings.JALALI_FORMAT)
    return obj.finish_date


def get_first_name(obj):
    return obj.user_obj.first_name


def get_last_name(obj):
    return obj.user_obj.last_name


get_start_date.short_description = _('Start Date')
get_start_date.admin_order_field = 'start_date'

get_last_name.short_description = _('Last Name')
get_last_name.admin_order_field = 'user_obj__last_name'

get_first_name.short_description = _('First Name')
get_first_name.admin_order_field = 'user_obj__first_name'


class DossierInline(ModelAdminJalaliMixin, BaseModelStackedInline):
    model = Dossier
    extra = 1
    fk_name = 'teacher_obj'
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = DossierInline
        Klass_parent = BaseModelStackedInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude



class TeacherAdmin(BaseModelAdmin):
    fields = ['user_obj', 'slider_segment_obj', 'biography', 'start_date']
    list_display = ['user_obj', get_first_name, get_last_name, get_start_date, aparnik_admin.get_update_at]
    list_filter = []
    search_fields = get_user_search_fields('user_obj') + []
    exclude = []
    dynamic_raw_id_fields = ['slider_segment_obj']
    inlines = [
        DossierInline,
    ]
    raw_id_fields = ['user_obj', ]

    def __init__(self, *args, **kwargs):
        Klass = TeacherAdmin
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
        model = Teacher


admin.site.register(Teacher, TeacherAdmin)
