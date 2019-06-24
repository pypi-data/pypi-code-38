from django.contrib import admin

from ievv_opensource.ievv_sms.models import DebugSmsMessage


@admin.register(DebugSmsMessage)
class DebugSmsMessageAdmin(admin.ModelAdmin):
    list_per_page = 20

    list_display = [
        'phone_number',
        'message',
        'created_datetime',
    ]

    readonly_fields = [
        'phone_number',
        'message',
        'created_datetime',
    ]

    search_fields = [
        'phone_number',
        'message',
    ]

    def has_add_permission(self, request):
        return False
