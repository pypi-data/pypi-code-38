# -*- coding: utf-8 -*-


from django.contrib import admin

from aparnik.contrib.basemodels.admin import BaseModelAdmin
from .models import Province, City, Shahrak, Town


# Register your models here.
class ProvinceAdmin(BaseModelAdmin):
    fields = ['title']
    list_display = ['title']
    list_filter = []
    search_fields = ['title']
    exclude = []
    raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = ProvinceAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Province


class CityAdmin(BaseModelAdmin):
    fields = ['title', 'province']
    list_display = ['title', 'province']
    list_filter = ['province']
    search_fields = ['title', 'province__title']
    exclude = []
    raw_id_fields = ['province']

    def __init__(self, *args, **kwargs):
        Klass = CityAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = City


class ShahrakAdmin(BaseModelAdmin):
    fields = ['title', 'province']
    list_display = ['title', 'province']
    list_filter = ['province']
    search_fields = ['title', 'province__title']
    exclude = []
    raw_id_fields = ['province']

    def __init__(self, *args, **kwargs):
        Klass = ShahrakAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Shahrak


class TownAdmin(BaseModelAdmin):
    fields = ['title', 'city']
    list_display = ['title', 'city']
    list_filter = []
    search_fields = ['title', 'city__title']
    exclude = []
    raw_id_fields = ['city']

    def __init__(self, *args, **kwargs):
        Klass = TownAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Town


admin.site.register(Province, ProvinceAdmin)
admin.site.register(City, CityAdmin)
admin.site.register(Shahrak, ShahrakAdmin)
admin.site.register(Town, TownAdmin)
