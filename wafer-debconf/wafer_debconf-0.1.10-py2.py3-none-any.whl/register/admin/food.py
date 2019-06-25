from django.contrib import admin
from django.contrib.admin.templatetags.admin_list import _boolean_icon

from register.admin.core import NotNullFilter
from register.models.food import Food


class SpecialDietNotNullFilter(NotNullFilter):
    title = "Special Diet"
    parameter_name = "special_diet"


class FoodAdmin(admin.ModelAdmin):
    list_display = (
        'attendee', 'full_name', 'email', 'diet', 'reconfirm', 'bursary'
    )
    list_filter = (
        'attendee__reconfirm', 'meals', 'diet',
        SpecialDietNotNullFilter,
        'attendee__user__bursary__food_status',
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

    def bursary(self, instance):
        return instance.attendee.user.bursary.food_status
    bursary.short_description = 'Food bursary status'
    bursary.admin_order_field = 'attendee__user__bursary__food_status'

    def reconfirm(self, instance):
        return _boolean_icon(instance.attendee.reconfirm)
    reconfirm.short_description = 'Confirmed?'
    reconfirm.admin_order_field = 'attendee__reconfirm'


admin.site.register(Food, FoodAdmin)
