# -*- coding: utf-8 -*-


from django.conf import settings
from django.contrib import admin

from .models import Information
from aparnik.contrib.basemodels.admin import BaseModelAdmin
# from socials.models import SocialNetwork

# Register your models here.


# class InlineSocialNetwork(admin.StackedInline):
#     extra = 0
#     model = SocialNetwork


class InformationAdmin(BaseModelAdmin):
    fields = ['website', 'address', 'email', 'phone', 'about_us', 'image', 'is_active', 'socials',
              'short_blogs', 'slider_segment_obj']
    list_display = ['website', 'phone', 'about_us', 'is_active']
    list_filter = ['website', 'is_active']
    search_fields = ['address', 'phone', 'about_us', 'website']
    exclude = []
    raw_id_fields = ['slider_segment_obj']
    # inlines = [InlineSocialNetwork]

    def __init__(self, *args, **kwargs):
        Klass = InformationAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude
        self.raw_id_fields = Klass_parent.raw_id_fields + self.raw_id_fields

    class Meta:
        model = Information


admin.site.register(Information, InformationAdmin)
