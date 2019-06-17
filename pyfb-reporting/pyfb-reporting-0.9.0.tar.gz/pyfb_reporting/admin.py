# -*- coding: utf-8 -*-
from django.contrib import admin
from django import forms

from django.utils.translation import ugettext_lazy as _

from .models import CDR, DimDate, DimCustomerHangupcause, DimCustomerSipHangupcause, DimProviderHangupcause, DimProviderSipHangupcause, DimCustomerDestination, DimProviderDestination

""" class CDRAdminForm(forms.ModelForm):

    class Meta:
        model = CDR
        fields = '__all__'
 """

class CDRAdmin(admin.ModelAdmin):
    # form = CDRAdminForm
    list_display = ['customer_ip', 'aleg_uuid', 'bleg_uuid', 'rtp_uuid', 'caller_number', 'callee_number', 'chan_name', 'start_stamp', 'answered_stamp', 'end_stamp', 'duration', 'effectiv_duration', 'effective_duration', 'billsec', 'read_codec', 'write_codec', 'sip_code', 'sip_reason', 'cost_rate', 'total_sell', 'total_cost', 'rate', 'init_block', 'block_min_duration', 'sip_charge_info', 'sip_user_agent', 'sip_rtp_rxstat', 'sip_rtp_txstat', 'kamailio_server', 'hangup_disposition', 'sip_hangup_cause', 'direction']
    readonly_fields = ['customer_ip', 'aleg_uuid', 'bleg_uuid', 'rtp_uuid', 'caller_number', 'callee_number', 'chan_name', 'start_stamp', 'answered_stamp', 'end_stamp', 'duration', 'effectiv_duration', 'effective_duration', 'billsec', 'read_codec', 'write_codec', 'sip_code', 'sip_reason', 'cost_rate', 'total_sell', 'total_cost', 'rate', 'init_block', 'block_min_duration', 'sip_charge_info', 'sip_user_agent', 'sip_rtp_rxstat', 'sip_rtp_txstat', 'kamailio_server', 'hangup_disposition', 'sip_hangup_cause', 'direction']

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
