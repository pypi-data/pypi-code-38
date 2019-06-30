# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from .models import Ticket, TicketConversation
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
# Register your models here.


class TicketConversationInline(BaseModelTabularInline):
    model = TicketConversation
    fields = ['content', 'user_obj', 'files_obj']
    raw_id_fields = ['user_obj']
    dynamic_raw_id_fields = ['files_obj']
    fk_name = 'ticket_obj'
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = TicketConversationInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


class TicketAdmin(BaseModelAdmin):
    fields = ['user_obj', 'title', 'priority', 'status', 'department']
    list_display = ['user_obj', 'title', 'priority', 'status', 'department', 'uuid', get_update_at]
    inlines = [TicketConversationInline]
    list_filter = ['priority', 'status', 'department', 'created_at']
    search_fields = get_user_search_fields('user_obj') + ['uuid']
    exclude = []
    raw_id_fields = ['user_obj']
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = TicketAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Ticket


admin.site.register(Ticket, TicketAdmin)
