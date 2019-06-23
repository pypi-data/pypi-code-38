# coding=utf-8

"""Admin classes for PageBlock."""

from django.contrib import admin

from page_block import models


@admin.register(models.PageBlock)
class PageBlockAdmin(admin.ModelAdmin):
    """Admin class for PageBlock."""

    fields = ['block_type']

    list_display = ['block_type']


@admin.register(models.PageBlockTranslation)
class PageTranslationAdmin(admin.ModelAdmin):
    """Admin class for PageBlock Translation."""

    list_display = [
        'page_block',
        'language',
        'default_translation',
    ]

    list_filter = [
        'page_block',
        'language',
        'default_translation',
    ]


@admin.register(models.PageBlockUrl)
class PageTranslationUrlAdmin(admin.ModelAdmin):
    """Admin class for PageBlock Translation."""

    list_display = [
        'page_block',
        'language',
        'default_translation',
    ]

    list_filter = [
        'page_block',
        'language',
        'default_translation',
    ]
