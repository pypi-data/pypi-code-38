from django.contrib import admin
from djangohelper.contrib.developer.models import (
ApplicationChangeList, Application, KeyStore
)
# Register your models here.

admin.site.register(Application)
admin.site.register(ApplicationChangeList)
admin.site.register(KeyStore)
