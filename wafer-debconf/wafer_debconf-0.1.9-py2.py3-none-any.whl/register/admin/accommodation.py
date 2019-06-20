import datetime

from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from register.admin.core import NotNullFilter
from register.dates import get_ranges_for_dates
from register.models.accommodation import Accomm


class RequirementsNotNullFilter(NotNullFilter):
    title = "Special Requirements"
    parameter_name = "requirements"


class AccommAdmin(admin.ModelAdmin):
    list_display = (
        'attendee', 'full_name', 'email',
        'dates', 'reconfirm', 'bursary', 'room'
    )
    list_editable = ('room',)
    list_filter = (
        'nights', RequirementsNotNullFilter,
        'attendee__reconfirm', 'attendee__user__bursary__accommodation_status',
    )
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

    def bursary(self, instance):
        return instance.attendee.user.bursary.accommodation_status
    bursary.short_description = 'Accomm bursary status'
    bursary.admin_order_field = 'attendee__user__bursary__accommodation_status'

    def dates(self, instance):
        to_show = []
        stays = get_ranges_for_dates(
            night.date for night in instance.nights.all()
        )
        for first_night, last_night in stays:
            last_morning = last_night + datetime.timedelta(days=1)
            num_nights = (last_morning - first_night).days
            to_show.append("%s eve. to %s morn. (%s nights)" % (
                first_night, last_morning, num_nights
            ))
        return '; '.join(to_show)


admin.site.register(Accomm, AccommAdmin)
