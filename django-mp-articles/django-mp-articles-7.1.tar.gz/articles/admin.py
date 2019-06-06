
from django.contrib import admin

from modeltranslation.admin import TranslationAdmin

from articles.models import Article, ArticleTag, ArticleType


class ArticleAdmin(TranslationAdmin):

    list_display = ['title', 'type', 'created', 'is_comments_enabled']

    list_filter = ['type', 'created', 'is_comments_enabled']

    filter_horizontal = ['tags']


class ArticleTagAdmin(TranslationAdmin):

    list_display = ['text']
    search_fields = ['text']


class ArticleTypeAdmin(TranslationAdmin):

    list_display = ['name']
    search_fields = ['name']


admin.site.register(Article, ArticleAdmin)
admin.site.register(ArticleTag, ArticleTagAdmin)
admin.site.register(ArticleType, ArticleTypeAdmin)
