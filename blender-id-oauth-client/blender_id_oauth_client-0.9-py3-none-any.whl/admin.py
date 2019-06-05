from django.contrib import admin
from . import models


@admin.register(models.OAuthToken)
class OAuthTokenAdmin(admin.ModelAdmin):
    model = models.OAuthToken

    list_display = ('user', 'expires_at')
    list_filter = ('expires_at',)
