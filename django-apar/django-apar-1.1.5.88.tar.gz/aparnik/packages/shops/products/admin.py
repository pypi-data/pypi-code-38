# -*- coding: utf-8 -*-


from django.contrib import admin
from aparnik.contrib.basemodels.admin import BaseModelAdmin, BaseModelTabularInline
from .models import Product, ProductProperty, ProductPropertyMembership


# Register your models here.
class ProductPropertyAdmin(BaseModelAdmin):
    fields = ['title', 'icon', ]
    list_display = ['title', ]
    search_fields = ['title', ]
    list_filter = []
    exclude = []
    raw_id_fields = ['icon']
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = ProductPropertyAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = ProductProperty


class ProductPropertyMembershipInline(BaseModelTabularInline):
    model = Product.properties.through
    fields = ['property', 'value']
    raw_id_fields = ('property',)
    extra = 1
    exclude = []

    def __init__(self, *args, **kwargs):
        Klass = ProductPropertyMembershipInline
        Klass_parent = BaseModelTabularInline

        super(Klass, self).__init__(*args, **kwargs)
        self.exclude = Klass_parent.exclude + self.exclude



class ProductAdmin(BaseModelAdmin):
    fields = ['title', 'further_details', 'price_fabric', 'slider_segment_obj', 'delivery_type',
              'is_free_field', 'discount_percent_value', 'discount_percent_expire',
              'is_discount_percent_expire_show',
              'aparnik_bon_return_value',
              'aparnik_bon_return_expire_value',
              'maximum_use_aparnik_bon_value',
              'has_permit_use_wallet_value',
              'currency',
              'is_tax',
              'is_draft',
              ]
    list_display = ['title', 'currency', 'price_fabric', 'is_free_field', 'discount_percent_value', 'is_draft',]
    search_fields = ['title', 'price_fabric', 'discount_percent_value']
    list_filter = ['is_free_field', 'is_draft',]
    exclude = []
    raw_id_fields = []
    inlines = [ProductPropertyMembershipInline]
    dynamic_raw_id_fields = ['slider_segment_obj', ]

    def __init__(self, *args, **kwargs):
        Klass = ProductAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields        
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Product


admin.site.register(Product, ProductAdmin)
admin.site.register(ProductProperty, ProductPropertyAdmin)
