# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields
from .models import UserAddress


# Register your models here.
class UserAddressAdmin(BaseModelAdmin):
    fields = ['user_obj', 'city_obj', 'address', 'postal_code', 'phone', 'is_default', 'is_active']
    list_display = ['user_obj', 'city_obj', 'phone', 'address']
    list_filter = ['is_default', 'is_active']
    search_fields = get_user_search_fields('user_obj') + ['city_obj__title', 'address', 'phone', 'postal_code']
    exclude = []
    raw_id_fields = ['user_obj', 'city_obj']

    def __init__(self, *args, **kwargs):
        Klass = UserAddressAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = UserAddress


admin.site.register(UserAddress, UserAddressAdmin)
