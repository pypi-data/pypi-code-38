from django.contrib import admin

from register.models.queue import Queue, QueueSlot

admin.site.register(Queue)
admin.site.register(QueueSlot)
