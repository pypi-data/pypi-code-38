# -*- coding:utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from . import models, helper


class SchoolAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)
    # readonly_fields = ('party',)


admin.site.register(models.School, SchoolAdmin)


class SessionAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school",)
    search_fields = ("school__name",)
    readonly_fields = ('party',)


admin.site.register(models.Session, SessionAdmin)


class CollegeAdmin(admin.ModelAdmin):
    list_display = ("name", 'code')
    raw_id_fields = ("party", "school")
    search_fields = ("school__name", "name")
    readonly_fields = ('party',)


admin.site.register(models.College, CollegeAdmin)


class MajorAdmin(admin.ModelAdmin):
    list_display = ("name", 'code')
    raw_id_fields = ("party", "school")
    search_fields = ("school__name", "name")
    readonly_fields = ('party',)


admin.site.register(models.Major, MajorAdmin)


class GradeAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school",)
    search_fields = ("school__name",)
    readonly_fields = ('party',)


admin.site.register(models.Grade, GradeAdmin)


class ClazzAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school", "entrance_session", "graduate_session", "primary_teacher", "grade")
    search_fields = ("school__name", "name")
    readonly_fields = ('party',)


admin.site.register(models.Clazz, ClazzAdmin)


def unbind_student(modeladmin, request, queryset):
    for student in queryset.all():
        helper.unbind(student)


unbind_student.short_description = u"解除绑定"


class StudentAdmin(admin.ModelAdmin):
    list_display = ('school', "name", 'number', 'clazz', 'create_time')
    list_select_related = ('school', 'clazz')
    raw_id_fields = ("school", "entrance_session", "graduate_session", "grade", 'party', 'school', 'user', 'clazz')
    search_fields = ("school__name", 'name', 'number')
    readonly_fields = ('party',)
    actions = [unbind_student]


admin.site.register(models.Student, StudentAdmin)


class TeacherAdmin(admin.ModelAdmin):
    list_display = ('school', "name")
    raw_id_fields = ("school", 'party', 'user')
    search_fields = ("school__name", 'name')
    readonly_fields = ('party',)


admin.site.register(models.Teacher, TeacherAdmin)


class ClazzCourseAdmin(admin.ModelAdmin):
    list_display = ("clazz", "course", "teacher")
    list_select_related = ("clazz", "course", "teacher")
    search_fields = ('clazz__name', "course__name")
    raw_id_fields = ('clazz', 'course', 'teacher')
    # readonly_fields = ('party',)


admin.site.register(models.ClazzCourse, ClazzCourseAdmin)
