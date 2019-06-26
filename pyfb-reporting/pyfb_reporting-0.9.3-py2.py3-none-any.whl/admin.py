# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe

from django.utils.translation import ugettext_lazy as _

import json

from pygments import highlight
from pygments.lexers import JsonLexer
from pygments.formatters import HtmlFormatter

from .models import CDR, DimDate, DimCustomerHangupcause, DimCustomerSipHangupcause, DimProviderHangupcause, DimProviderSipHangupcause, DimCustomerDestination, DimProviderDestination


class CDRAdmin(admin.ModelAdmin):
    list_display = ['aleg_uuid', 'customer', 'direction', 'caller_number', 'callee_number', 'start_stamp', 'end_stamp', 'duration', 'sip_rtp_rxstat', 'sip_code', 'hangup_disposition']
    search_fields = ('caller_number', 'callee_number', '^customer__company__name')
    ordering = ('-start_stamp',)

    fieldsets = (
        (_(u'General'), {
            'fields': (('customer', 'customer_endpoint'),
                       ('start_stamp', 'direction'),
                       ('callee_number', 'callee_destination'),
                       ('caller_number', 'caller_destination'),
                       'duration')
        }),
        (_(u'Route json details'), {
            'classes': ('collapse',),
            'fields': ('route_prettified',)
        }),
        (_(u'Advanced date / duration infos'), {
            'fields': (('answered_stamp', 'end_stamp'))
        }),
        (_(u'Financial infos'), {
            'fields': (('total_cost', 'cost_rate'),
                       ('total_sell', 'rate'))
        }),
        (_(u'Routing infos'), {
            'fields': (('ratecard_id', 'lcr_group_id'),
                       ('lcr_carrier_id', 'provider_endpoint'))
        }),
        (_(u'Call detailed infos'), {
            'fields': (('sip_rtp_rxstat', 'sip_rtp_txstat'),
                       ('sip_code', 'sip_reason', 'hangup_disposition'),
                       ('read_codec', 'write_codec'),
                       'sip_charge_info',
                       ('customer_ip', 'sip_user_agent'),
                       'aleg_uuid',
                       'bleg_uuid',
                       'rtp_uuid',
                       ('kamailio_server', 'media_server'))
        }),
    )

    actions = None
    has_add_permission = False
    has_delete_permission = False
    log_change = False
    message_user = False
    save_model = False
    show_full_result_count = False
    view_on_site = False

    readonly_fields = ('customer_ip', 'aleg_uuid', 'bleg_uuid', 'rtp_uuid', 'caller_number', 'callee_number', 'start_stamp', 'answered_stamp', 'end_stamp', 'duration', 'read_codec', 'write_codec', 'sip_code', 'sip_reason', 'cost_rate', 'total_sell', 'total_cost', 'rate', 'sip_charge_info', 'sip_user_agent', 'sip_rtp_rxstat', 'sip_rtp_txstat', 'kamailio_server', 'hangup_disposition', 'direction', 'customer', 'provider_endpoint', 'lcr_carrier_id', 'ratecard_id', 'lcr_group_id', 'caller_destination', 'callee_destination', 'customer_endpoint', 'media_server', 'route_prettified',)
    exclude = ('route_json',)

    def route_prettified(self, instance):
        """Function to display pretty version of our data"""

        # Convert the data to sorted, indented JSON
        response = json.dumps(instance.route_json, sort_keys=True, indent=2)

        # Truncate the data. Alter as needed
        response = response[:5000]

        # Get the Pygments formatter
        formatter = HtmlFormatter(style='colorful')

        # Highlight the data
        response = highlight(response, JsonLexer(), formatter)

        # Get the stylesheet
        style = "<style>" + formatter.get_style_defs() + "</style><br>"

        # Safe the output
        return mark_safe(style + response)

    route_prettified.short_description = 'route json'

    # def get_readonly_fields(self, request, obj=None):
    #     return [f.name for f in obj._meta.fields]

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request):
        return False

admin.site.register(CDR, CDRAdmin)


""" class DimDateAdminForm(forms.ModelForm):

    class Meta:
        model = DimDate
        fields = '__all__' """


class DimDateAdmin(admin.ModelAdmin):
    # form = DimDateAdminForm
    list_display = ['date', 'day', 'day_of_week', 'hour', 'month', 'quarter', 'year']
    readonly_fields = ['date', 'day', 'day_of_week', 'hour', 'month', 'quarter', 'year']

admin.site.register(DimDate, DimDateAdmin)


""" class DimCustomerHangupcauseAdminForm(forms.ModelForm):

    class Meta:
        model = DimCustomerHangupcause
        fields = '__all__' """


class DimCustomerHangupcauseAdmin(admin.ModelAdmin):
    # form = DimCustomerHangupcauseAdminForm
    list_display = ['hangupcause', 'total_calls', 'direction']
    readonly_fields = ['hangupcause', 'total_calls', 'direction']

admin.site.register(DimCustomerHangupcause, DimCustomerHangupcauseAdmin)


# class DimCustomerSipHangupcauseAdminForm(forms.ModelForm):

#     class Meta:
#         model = DimCustomerSipHangupcause
#         fields = '__all__'
