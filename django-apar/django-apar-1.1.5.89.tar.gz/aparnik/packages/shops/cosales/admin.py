# -*- coding: utf-8 -*-


from django.contrib import admin
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from aparnik.contrib.users.admin import get_user_search_fields

from .models import CoSale, CoSalePayment


# class CoSaleHistoryInline(admin.TabularInline):
#     exclude = ['visit_count', 'review_average', 'sort', 'tags', 'update_needed', 'is_show_only_for_super_user']
#     extra = 0
#     model = CoSaleHistory
#     fk_name = 'cosale_obj'


class CoSaleAdmin(BaseModelAdmin):
    fields = ['user_bought_obj', 'user_co_sale_obj', 'order_obj', 'is_active', 'price']
    list_display = ['user_bought_obj', 'user_co_sale_obj', 'order_obj', 'is_active', 'price']
    # inlines = [CoSaleHistoryInline]
    inlines = []
    list_filter = []
    search_fields = ['user_bought_obj__username', 'user_co_sale_obj__username', 'order_obj__id']
    exclude = []
    raw_id_fields = ['user_bought_obj', 'user_co_sale_obj', 'order_obj']
    dynamic_raw_id_fields = []
    readonly_fields = []

    def __init__(self, *args, **kwargs):
        Klass = CoSaleAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields


class CoSalePaymentAdmin(BaseModelAdmin):
    fields = ['price', 'user_bank_account_obj', 'tracking_number', 'status']
    list_display = ['price', 'user_bank_account_obj', 'tracking_number', 'status']
    inlines = []
    list_filter = ['status']
    search_fields = get_user_search_fields('user_bank_account_obj__user_obj') + []
    exclude = []
    raw_id_fields = ['user_bank_account_obj']
    dynamic_raw_id_fields = []
    readonly_fields = []

    def __init__(self, *args, **kwargs):
        Klass = CoSalePaymentAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields


admin.site.register(CoSale, CoSaleAdmin)
admin.site.register(CoSalePayment, CoSalePaymentAdmin)
