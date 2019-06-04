from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from register.models.childcare import ChildCare


class ChildCareAdmin(admin.ModelAdmin):
    list_display = ('attendee', 'full_name', 'email', 'reconfirm',)
    list_filter = ('attendee__reconfirm',)
    search_fields = (
        'attendee__user__username', 'attendee__user__first_name',
        'attendee__user__last_name'
    )

    def full_name(self, instance):
        return instance.attendee.user.get_full_name()
    full_name.admin_order_field = 'attendee__user__last_name'

    def email(self, instance):
        return instance.attendee.user.email
    email.admin_order_field = 'attendee__user__email'

    def reconfirm(self, instance):
        return _boolean_icon(instance.attendee.reconfirm)
    reconfirm.short_description = 'Confirmed?'
    reconfirm.admin_order_field = 'attendee__reconfirm'


admin.site.register(ChildCare, ChildCareAdmin)
