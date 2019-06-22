# -*- coding: utf-8 -*-


from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from .models import Order, OrderItem


# Rcegister your models here.
class OrderItemInline(BaseModelTabularInline):
    model = OrderItem
    raw_id_fields = ['product_obj']
    fk_name = 'order_obj'
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = OrderItemInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude


# class OrderItemAdmin(BaseModelAdmin):
#     list_display = ['order_obj', 'product', 'price', 'quantity']
#     raw_id_fields = ['order_obj']
#     search_fields = ['order_obj__id', 'product_obj__title']
#     fields = ['__all__']
#     inlines = [OrderItemInline]
#     list_filter = ['status', 'created_at']
#     exclude = []
#     dynamic_raw_id_fields = []
#
#     def __init__(self, *args, **kwargs):
#         Klass = OrderItemAdmin
#         Klass_parent = BaseModelAdmin
#
#         super(Klass, self).__init__(*args, **kwargs)
#         self.fields = Klass_parent.fields + self.fields
#         self.list_display = Klass_parent.list_display + self.list_display
#         self.list_filter = Klass_parent.list_filter + self.list_filter
#         self.search_fields = Klass_parent.search_fields + self.search_fields
#         self.exclude = Klass_parent.exclude + self.exclude
#         self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
#         self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields
#
#     class Meta:
#         OrderItem

def invoice_link(obj):
    return format_html(
        '<a href="{0}" target="blank" class="button">Invoice</a>',
        obj.get_pay_uri()
    )


invoice_link.short_description = "Invoice"


class OrderAdmin(BaseModelAdmin):
    # list_display = ['id', 'first_name', 'last_name', 'email',
    #                 'address', 'postal_code', 'city', 'paid',
    #                 'created', 'updated']
    # list_filter = ['paid', 'created', 'updated']
    fields = ['user', 'status', 'address_obj']
    list_display = ['user', 'coupon', 'uuid', invoice_link, 'status', 'is_sync_with_websites', get_update_at]
    inlines = [OrderItemInline]
    list_filter = ['status', 'created_at', 'is_sync_with_websites']
    search_fields = get_user_search_fields('user') + ['coupon__code', 'uuid']
    exclude = []
    raw_id_fields = ['user', 'coupon', 'address_obj']
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = OrderAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields


admin.site.register(Order, OrderAdmin)
# admin.site.register(OrderItem, OrderItemAdmin)