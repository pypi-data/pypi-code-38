# -*- coding: utf-8 -*-


from django.contrib import admin

from .models import TermsAndConditions
from aparnik.contrib.basemodels.admin import BaseModelAdmin
# from socials.models import SocialNetwork

# Register your models here.


# class InlineSocialNetwork(admin.StackedInline):
#     extra = 0
#     model = SocialNetwork


class TermsAndConditionsAdmin(BaseModelAdmin):
    fields = ['short_blogs', 'is_active', ]
    list_display = ['is_active', ]
    # inlines = [InlineSocialNetwork]
    list_filter = ['is_active', 'created_at']
    search_fields = []
    exclude = []
    raw_id_fields = []
    dynamic_raw_id_fields = []

    def __init__(self, *args, **kwargs):
        Klass = TermsAndConditionsAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.dynamic_raw_id_fields = Klass_parent.dynamic_raw_id_fields + self.dynamic_raw_id_fields

    class Meta:
        model = TermsAndConditions


admin.site.register(TermsAndConditions, TermsAndConditionsAdmin)
