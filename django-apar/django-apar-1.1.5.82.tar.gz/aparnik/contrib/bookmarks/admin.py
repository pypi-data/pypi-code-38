# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from aparnik.contrib.users.admin import get_update_at, get_user_search_fields
from .models import Bookmark


# Register your models here.
class BookmarkAdmin(BaseModelAdmin):
    list_display = ['user_obj', get_update_at]
    search_fields = get_user_search_fields('user_obj') + []
    raw_id_fields = ['user_obj',]
    list_filter = ['created_at']
    fields = []
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = BookmarkAdmin
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
        model = Bookmark

    def get_form(self, request, obj=None, **kwargs):
        form = super(BookmarkAdmin, self).get_form(request, obj, **kwargs)
        if is_app_installed('aparnik.packages.shops.products'):
            from aparnik.packages.shops.products.models import Product
            form.base_fields['model_obj'].queryset = Product.objects.active()
        return form


admin.site.register(Bookmark, BookmarkAdmin)
