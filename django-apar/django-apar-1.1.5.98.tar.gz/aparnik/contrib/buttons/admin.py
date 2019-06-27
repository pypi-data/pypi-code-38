# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.utils.utils import is_app_installed
from aparnik.contrib.basemodels.admin import BaseModelAdmin
from .models import Button


class ButtonAdmin(BaseModelAdmin):
    fields = ['title', 'icon', 'background_color', 'icon_color', 'title_color', 'model_obj']
    list_display = ['title', 'model_obj']
    search_fields = ['title']
    list_filter = []
    raw_id_fields = ['model_obj', 'icon']
    exclude = []
    dynamic_raw_id_fields = []        # exclude = ('password', 'iv',)
    inlines = []

    def __init__(self, *args, **kwargs):
        Klass = ButtonAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields
        self.inlines = Klass_parent.inlines + self.inlines

    class Meta:
        model = Button


if is_app_installed('aparnik.contrib.segments'):
    from aparnik.contrib.segments.admin import SegmentAdmin
    from .models import ButtonSegment

    class ButtonSegmentAdmin(SegmentAdmin):
        fields = []
        list_display = []
        search_fields = []
        list_filter = []
        raw_id_fields = []
        exclude = []
        dynamic_raw_id_fields = []

        def __init__(self, *args, **kwargs):
            Klass = ButtonSegmentAdmin
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
            model = ButtonSegment


    admin.site.register(ButtonSegment, ButtonSegmentAdmin)


admin.site.register(Button, ButtonAdmin)
