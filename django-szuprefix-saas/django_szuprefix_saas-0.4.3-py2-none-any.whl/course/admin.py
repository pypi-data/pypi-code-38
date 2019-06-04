from django.contrib import admin

from . import models


@admin.register(models.Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'is_active', 'category', 'create_time')
    raw_id_fields = ('party','category')
    search_fields = ("name",)
    readonly_fields = ('party',)


@admin.register(models.Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'create_time')
    raw_id_fields = ('party',)
    search_fields = ("name",)
    readonly_fields = ('party',)


@admin.register(models.Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('name','create_time')
    raw_id_fields = ('party', 'course')
