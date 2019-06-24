# -*- coding: utf-8 -*-


from django.contrib import admin
from jalali_date.admin import ModelAdminJalaliMixin

from aparnik.contrib.users.admin import get_update_at
from .models import Bank
# Register your models here.


def get_payment(obj):
    return obj.payment.uuid


class BankAdmin(admin.ModelAdmin):
    list_display = ('status', 'authority_id', 'ref_id', get_payment, get_update_at)
    # list_display_links = ('username', 'first_name', 'last_name')
    # list_filter = ('is_staff', )
    # list_editable = ('username', 'mobile', )
    # search_fields = ('username', 'last_name', 'first_name')
    # readonly_fields = ( )
    # inlines = [DocumentFilesInline, ]

    actions = None

    class Meta:
        model = Bank

    # permission
    def has_delete_permission(self, request, obj=None):
        # Disable delete
        return False

    def has_add_permission(self, request):
        return True

    def change_view(self, request, object_id, form_url='', extra_context=None):
        ''' customize edit form '''
        extra_context = extra_context or {}
        extra_context['show_save_and_continue'] = False
        extra_context['show_save'] = False
        extra_context['show_save_and_add_another'] = False  # this not works if has_add_permision is True
        return super(BankAdmin, self).change_view(request, object_id, extra_context=extra_context)

admin.site.register(Bank, BankAdmin)
