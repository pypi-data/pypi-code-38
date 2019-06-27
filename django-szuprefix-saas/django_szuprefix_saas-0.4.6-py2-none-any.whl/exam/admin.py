from django.contrib import admin

from . import models

@admin.register(models.Paper)
class PaperAdmin(admin.ModelAdmin):
    list_display = ('title', 'party', 'is_active', 'create_time')
    raw_id_fields = ('party', 'user')
    search_fields = ("title",)
    readonly_fields = ('party',)


@admin.register(models.Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = ('paper', 'user', 'create_time')
    list_select_related = ['paper', 'user']
    raw_id_fields = ('party', 'user', 'paper')
    search_fields = ("paper__title",)
    # readonly_fields = ('party',)


@admin.register(models.Stat)
class StatAdmin(admin.ModelAdmin):
    list_display = ('paper',)
    raw_id_fields = ('party', 'paper')


@admin.register(models.Performance)
class PerformanceAdmin(admin.ModelAdmin):
    list_display = ('paper', 'user', 'create_time')
    list_select_related = ['paper', 'user']
    raw_id_fields = ('party', 'user', 'paper')
    search_fields = ("paper__title", "user__first_name")
    # readonly_fields = ('party',)
