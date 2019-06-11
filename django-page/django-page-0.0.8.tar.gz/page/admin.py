from adminsortable2.admin import SortableInlineAdminMixin
from django.contrib import admin
from django.core.cache import cache
from reversion.admin import VersionAdmin

from page.models import Page, Pagelet, DownloadableFile, Post, PostCategory, Slide, Popup


class SlideInline(SortableInlineAdminMixin, admin.StackedInline):
    sortable = "order"
    model = Slide
    extra = 0

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()


class PopupInline(admin.StackedInline):
    model = Popup
    extra = 0


@admin.register(Page)
class PageAdmin(VersionAdmin):
    list_display = ['title', 'code', 'id', 'updated', 'created']
    inlines = [SlideInline, PopupInline]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()


@admin.register(Pagelet)
class PageletAdmin(VersionAdmin):
    list_display = ['title', 'code', 'id', 'updated', 'created']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()


@admin.register(DownloadableFile)
class DownloadableFileAdmin(VersionAdmin):
    list_display = ['name', 'file', ]

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()


@admin.register(Post)
class PostAdmin(VersionAdmin):
    list_display = ['title', 'active', 'topmost', 'created', 'cate']
    list_editable = ['active', 'topmost']
    list_filter = ['cate', 'active', 'topmost']

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()


@admin.register(PostCategory)
class PostCategoryAdmin(admin.ModelAdmin):

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        cache.clear()


