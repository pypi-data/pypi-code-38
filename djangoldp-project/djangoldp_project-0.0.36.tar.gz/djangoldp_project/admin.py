from django.contrib import admin
from guardian.admin import GuardedModelAdmin
from .models import Project, Member, Customer, BusinessProvider


class TeamInline(admin.TabularInline):
    model = Member
    extra = 0


class ProjectAdmin(GuardedModelAdmin):
    inlines = [TeamInline]


admin.site.register(Project, ProjectAdmin)
admin.site.register(Member)
admin.site.register(Customer)
admin.site.register(BusinessProvider)
