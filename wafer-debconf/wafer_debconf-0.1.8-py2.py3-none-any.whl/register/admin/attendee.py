from django.contrib import admin
from django.utils.dateparse import parse_date

from register.admin.core import NotNullFilter
from register.models.attendee import Attendee
from register.dates import LEAVE_ON_OR_BEFORE, nights


class NotesNotNullFilter(NotNullFilter):
    title = "Notes"
    parameter_name = "notes"


class DateFilter(admin.SimpleListFilter):
    def lookups(self, request, model_admin):
        for day in nights(orga=True):
            yield day.isoformat(), day
        yield LEAVE_ON_OR_BEFORE.isoformat(), LEAVE_ON_OR_BEFORE
        yield 'null', 'None'

    def queryset(self, request, queryset):
        parameter = self.parameter_name
        value = self.value()
        if value is None:
            return queryset
        if value == 'null':
            parameter += '__isnull'
            value = True
        else:
            parameter += '__date'
            value = parse_date(value)
        return queryset.filter(**{parameter: value})


class ArrivalDateFilter(DateFilter):
    title = 'Arrival Day'
    parameter_name = 'arrival'


class DepartureDateFilter(DateFilter):
    title = 'Departure Day'
    parameter_name = 'departure'


class AttendeeAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'full_name', 'email', 'reconfirm', 'arrival', 'departure',
        'billable', 'paid',
    )
    list_filter = (
        'fee', ArrivalDateFilter, DepartureDateFilter, 'reconfirm',
        't_shirt_size', 'shoe_size', NotesNotNullFilter,
    )
    search_fields = ('user__username', 'user__first_name', 'user__last_name')
    readonly_fields = ('full_name', 'email')

    def full_name(self, instance):
        return instance.user.get_full_name()
    full_name.admin_order_field = 'user__last_name'

    def email(self, instance):
        return instance.user.email
    email.admin_order_field = 'user__email'


admin.site.register(Attendee, AttendeeAdmin)
