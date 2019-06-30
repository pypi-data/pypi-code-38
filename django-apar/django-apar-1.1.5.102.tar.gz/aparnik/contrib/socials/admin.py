# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.users.admin import get_update_at
from aparnik.utils.utils import is_app_installed
from .models import SocialNetwork
from aparnik.contrib.basemodels.admin import BaseModelAdmin
# Register your models here.


class SocialNetworkAdmin(BaseModelAdmin):
    fields = ['title', 'link', 'icon', 'value', 'android_app_shortcut', 'ios_app_shortcut']
    list_display = ['title', 'link', 'icon', get_update_at]
    list_filter = ['created_at']
    search_fields = ['title']
    readonly_fields = []
    raw_id_fields = ['icon']
    exclude = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = SocialNetworkAdmin
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
        model = SocialNetwork


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import SocialNetworkSegment

    class SocialNetworkSegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        raw_id_fields = []
        exclude = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = SocialNetworkSegmentAdmin
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
            model = SocialNetworkSegment


    admin.site.register(SocialNetworkSegment, SocialNetworkSegmentAdmin)


admin.site.register(SocialNetwork, SocialNetworkAdmin)
