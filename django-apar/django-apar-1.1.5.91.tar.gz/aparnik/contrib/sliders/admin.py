# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.users.admin import get_update_at
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from .models import Slider, SliderImage, SliderLink, SliderVideo, SliderBaseModel, SliderSocialNetwork


# Register your models here.
class SliderAdmin(BaseModelAdmin):
    fields = ['name', 'image', 'is_active']
    exclude = []
    dynamic_raw_id_fields = []
    # list_display = ['id', 'name', 'is_active', get_update_at, ]
    list_display = ['name', get_update_at, ]
    search_fields = ['name', ]
    # list_filter = ['is_active', 'is_home', 'is_library', 'created_at', ]
    list_filter = ['is_active', 'created_at', ]
    raw_id_fields = ['image']

    def __init__(self, *args, **kwargs):
        Klass = SliderAdmin
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
        model = Slider


class SliderImageAdmin(SliderAdmin):
    fields = []
    exclude = []
    dynamic_raw_id_fields = []
    list_display = []
    search_fields = []
    list_filter = []
    raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SliderImageAdmin
        Klass_parent = SliderAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = SliderImage


class SliderSocialNetworkAdmin(SliderAdmin):
    fields = ['social']
    list_display = []
    list_filter = []
    raw_id_fields = ['social']
    search_fields = ['social__title', 'social__link']
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SliderSocialNetworkAdmin
        Klass_parent = SliderAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = SliderSocialNetwork


class SliderLinkAdmin(SliderAdmin):
    fields = ['link']
    list_display = []
    list_filter = []
    raw_id_fields = []
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SliderLinkAdmin
        Klass_parent = SliderAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = SliderLink


class SliderVideoAdmin(SliderAdmin):
    fields = ['video']
    list_display = []
    list_filter = []
    raw_id_fields = ['video']
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SliderVideoAdmin
        Klass_parent = SliderAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = SliderVideo


class SliderBaseModelAdmin(SliderAdmin):
    fields = ['model']
    list_display = []
    list_filter = []
    raw_id_fields = ['model']
    search_fields = []
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SliderBaseModelAdmin
        Klass_parent = SliderAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = SliderBaseModel

    def get_form(self, request, obj=None, **kwargs):
        form = super(SliderBaseModelAdmin, self).get_form(request, obj, **kwargs)
        if is_app_installed('aparnik.packages.shops.products'):

            from aparnik.packages.shops.products.models import Product
            form.base_fields['model'].queryset = Product.objects.active()

        return form


if is_app_installed('aparnik.contrib.segments'):

    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import SliderSegment


    class SliderSegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        exclude = []
        raw_id_fields = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = SliderSegmentAdmin
            Klass_parent = SegmentAdmin

            super(Klass, self).__init__(*args, **kwargs)
            self.fields = Klass_parent.fields + self.fields
            self.list_display = Klass_parent.list_display + self.list_display
            self.list_filter = Klass_parent.list_filter + self.list_filter
            self.search_fields = Klass_parent.search_fields + self.search_fields
            self.exclude = Klass_parent.exclude + self.exclude
            self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
            self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

        class Meta:
            model = SliderSegment


    admin.site.register(SliderSegment, SliderSegmentAdmin)

admin.site.register(Slider, SliderAdmin)
admin.site.register(SliderImage, SliderImageAdmin)
admin.site.register(SliderSocialNetwork, SliderSocialNetworkAdmin)
admin.site.register(SliderLink, SliderLinkAdmin)
admin.site.register(SliderVideo, SliderVideoAdmin)
admin.site.register(SliderBaseModel, SliderBaseModelAdmin)
