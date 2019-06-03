from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from votebase.core.payments.models import Order, Information


class InformationInlines(admin.StackedInline):
    model = Information
    extra = 0


class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'REF', 'user', 'full_name', 'package', 'package_valid_to', 'state', 'created')
    list_display_links = ('id',)
    list_filter = ('package', 'state')
#    list_filter = ('is_confirmed', 'method_of_contact')
    ordering = ['-created',]
    search_fields = ['REF', 'user__username', 'user__email']
    inlines = (InformationInlines, )

    def first_name(self, obj):
        return obj.get_information().first_name

    def last_name(self, obj):
        return obj.get_information().last_name

    def full_name(self, obj):
        return self.first_name(obj) + ' ' + self.last_name(obj)


admin.site.register(Order, OrderAdmin)
