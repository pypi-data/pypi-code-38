# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_user_search_fields
from .models import ProductSharing


# Register your models here.
class ProductSharingAdmin(BaseModelAdmin):
    fields = ['user_obj', 'user_product_share_with_obj', 'product_obj', 'is_active', ]
    list_display = ['user_obj', 'user_product_share_with_obj', 'product_obj', 'is_active', ]
    search_fields = get_user_search_fields('user_obj') + get_user_search_fields(
        'user_product_share_with_obj') + \
                    ['product_obj__title', ]
    list_filter = ['is_active']
    exclude = []
    raw_id_fields = ['product_obj']
    dynamic_raw_id_fields = ['user_obj', 'user_product_share_with_obj']

    def __init__(self, *args, **kwargs):
        Klass = ProductSharingAdmin
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
        model = ProductSharing


admin.site.register(ProductSharing, ProductSharingAdmin)
# admin.site.register(ProductSharing)