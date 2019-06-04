# -*- coding:utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from django.contrib.contenttypes.fields import GenericRelation

from . import models


class PartyAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'is_active', 'slug', 'create_time')


admin.site.register(models.Party, PartyAdmin)


class DepartmentAdmin(admin.ModelAdmin):
    list_display = ("name", "party", "path")
    raw_id_fields = ("party", "parent")
    list_filter = ("party",)
    search_fields = ("name",)
    readonly_fields = ("path",)


admin.site.register(models.Department, DepartmentAdmin)

def set_unusable_password(modeladmin, request, queryset):
    for worker in queryset.all():
        user = worker.user
        user.set_unusable_password()
        user.save()
set_unusable_password.short_description = "清除登录密码"


class WorkerAdmin(admin.ModelAdmin):
    list_display = ('name', 'number', 'party', 'position', 'is_active', 'create_time')
    raw_id_fields = ('party', 'departments', 'user')
    search_fields = ('name', 'number')
    actions = (set_unusable_password, )

admin.site.register(models.Worker, WorkerAdmin)
