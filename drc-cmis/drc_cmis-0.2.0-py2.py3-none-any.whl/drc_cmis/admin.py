from django.contrib import admin

from solo.admin import SingletonModelAdmin

from .models import CMISConfig, CMISFolderLocation


@admin.register(CMISConfig)
class CMISConfigAdmin(SingletonModelAdmin):
    filter_horizontal = ['locations']


@admin.register(CMISFolderLocation)
class CMISFolderLocationAdmin(admin.ModelAdmin):
    pass
