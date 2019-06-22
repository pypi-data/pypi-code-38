# -*- coding: utf-8 -*-


from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from aparnik.contrib.users.admin import get_update_at
from .models import ShortBlog


# Register your models here.
class ShortBlogAdmin(admin.ModelAdmin):
    fields = ['title', 'content']
    list_display = ['title', get_update_at]
    search_fields = ['title', 'content']
    readonly_fields = ['created_at', 'update_at']
    list_filter = ['created_at']
    # raw_id_fields = ['category', ]

    class Meta:
        ShortBlog

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(ShortBlogAdmin, self).change_view(request, object_id, extra_context=extra_context)


admin.site.register(ShortBlog, ShortBlogAdmin)

