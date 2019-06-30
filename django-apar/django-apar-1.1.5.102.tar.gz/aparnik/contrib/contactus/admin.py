# -*- coding: utf-8 -*-


from django.conf import settings
from django.contrib import admin

from .models import ContactUs
from aparnik.contrib.basemodels.admin import BaseModelAdmin
# from socials.models import SocialNetwork

# Register your models here.


# class InlineSocialNetwork(admin.StackedInline):
#     extra = 0
#     model = SocialNetwork


class ContactUsAdmin(BaseModelAdmin):
    fields = [
        'first_name', 'last_name',
        'website', 'address', 'email', 'phone', 'title', 'content', 'is_active',
              ]
    list_display = ['website', 'phone', 'title', 'is_active']
    list_filter = ['website', 'is_active']
    search_fields = ['address', 'phone', ]
    exclude = []
    raw_id_fields = []
    # inlines = [InlineSocialNetwork]

    def __init__(self, *args, **kwargs):
        Klass = ContactUsAdmin
        Klass_parent = BaseModelAdmin

        super(Klass, self).__init__(*args, **kwargs)
        self.fields = Klass_parent.fields + self.fields
        self.list_display = Klass_parent.list_display + self.list_display
        self.list_filter = Klass_parent.list_filter + self.list_filter
        self.search_fields = Klass_parent.search_fields + self.search_fields
        self.exclude = Klass_parent.exclude + self.exclude

    class Meta:
        model = ContactUs


admin.site.register(ContactUs, ContactUsAdmin)
