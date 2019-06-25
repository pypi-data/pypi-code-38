from django.contrib import admin

from front_desk.models import CheckIn


class CheckInAdmin(admin.ModelAdmin):
    list_display = (
        'attendee', 'full_name', 'email', 'swag', 'nametag',
        'room_key', 'returned_key', 'checked_out',
    )
    list_filter = (
        'swag', 't_shirt', 'shoes', 'nametag', 'room_key', 'returned_key',
        'checked_out',
    )
    search_fields = (
        'attendee__user__username', 'attendee__user__first_name',
        'attendee__user__last_name', 'key_card',
    )

    def full_name(self, instance):
        return instance.attendee.user.get_full_name()
    full_name.admin_order_field = 'attendee__user__last_name'

    def email(self, instance):
        return instance.attendee.user.email
    email.admin_order_field = 'attendee__user__email'


admin.site.register(CheckIn, CheckInAdmin)
