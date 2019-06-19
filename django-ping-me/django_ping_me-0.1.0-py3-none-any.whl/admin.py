from django.contrib import admin
from .models import Domain, Ping, PingSummary

admin.site.register(Domain)
admin.site.register(Ping)
admin.site.register(PingSummary)