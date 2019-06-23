# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields
from .models import BankName, BankAccount


# Register your models here.
class BankNameAdmin(BaseModelAdmin):
    fields = ['title', 'is_active']
    list_display = ['title', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title']
    exclude = []
    raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = BankNameAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = BankName


class BankAccountAdmin(BaseModelAdmin):
    fields = ['user_obj', 'bank_name_obj', 'account_number', 'card_number', 'shaba_number', 'is_default', 'is_active']
    list_display = ['user_obj', 'bank_name_obj', 'account_number', 'is_default', 'is_active', 'card_number']
    list_filter = ['is_default', 'is_active']
    search_fields = get_user_search_fields('user_obj') + ['bank_name_obj__title', 'account_number', 'shaba_number', 'card_number']
    exclude = []
    raw_id_fields = ['user_obj', 'bank_name_obj']

    def __init__(self, *args, **kwargs):
        Klass = BankAccountAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = BankAccount


admin.site.register(BankName, BankNameAdmin)
admin.site.register(BankAccount, BankAccountAdmin)
