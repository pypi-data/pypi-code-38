from django.contrib import admin
import django_vox.admin

from . import models


class SubscriberAdmin(admin.ModelAdmin):
    actions = (django_vox.admin.notify,)


admin.site.register(models.Article)
admin.site.register(models.Subscriber, SubscriberAdmin)
admin.site.register(models.Comment)
