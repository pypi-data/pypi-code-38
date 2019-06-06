from django.contrib import admin

from .models import Account, ChatProfile, OPClient

admin.site.register(ChatProfile)
admin.site.register(Account)
admin.site.register(OPClient)
