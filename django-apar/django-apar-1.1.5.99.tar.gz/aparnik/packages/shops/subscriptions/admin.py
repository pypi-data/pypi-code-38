# -*- coding: utf-8 -*-


from django.contrib import admin


from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.packages.shops.products.admin import ProductAdmin

from .models import Subscription, SubscriptionOrder


# Register your models here.
class SubscriptionAdmin(ProductAdmin):
    fields = ['duration', 'description', 'type', 'products']
    list_display = ['duration']
    search_fields = ['duration']
    list_filter = ['duration']
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = ['products']

    def __init__(self, *args, **kwargs):
        Klass = SubscriptionAdmin
        Klass_parent = ProductAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields


class SubscriptionOrderAdmin(BaseModelAdmin):
    fields = ['subscription_obj', 'order_obj', 'expire_at']
    list_display = ['subscription_obj', 'order_obj', 'expire_at', get_update_at]
    search_fields = get_user_search_fields('order_obj__user') + ['subscription_obj', 'order_obj', ]
    list_filter = []
    exclude = []
    raw_id_fields = ['subscription_obj', 'order_obj']
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SubscriptionOrderAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields


admin.site.register(Subscription, SubscriptionAdmin)
admin.site.register(SubscriptionOrder, SubscriptionOrderAdmin)
