# -*- coding: utf-8 -*-


from django.contrib import admin
from django.conf import settings
from jalali_date import datetime2jalali

from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.invitation.models import Invite

# Register your models here.
class InviteAdmin(admin.ModelAdmin):
    fields = ['id', 'invite', 'invited_by', 'update_at']
    list_display = ['id', 'invite', 'invited_by', get_update_at]
    search_fields = ['invite', 'invited_by']
    list_filter = ['update_at']
    readonly_fields = ['invite', 'invited_by', 'update_at']

    class Meta:
        Invite

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False # this not works if has_add_permision is True
        return super(InviteAdmin, self).change_view(request, object_id, extra_context=extra_context)


admin.site.register(Invite, InviteAdmin)

