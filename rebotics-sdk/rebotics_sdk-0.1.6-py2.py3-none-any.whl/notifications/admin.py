from django.contrib import admin

from rebotics_sdk.notifications.models import WebhookRouter, Message


@admin.register(WebhookRouter)
class WebhookRouterAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'user', 'created', 'url'
    ]


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'receiver_id', 'component', 'status', 'delivery_status'
    ]
