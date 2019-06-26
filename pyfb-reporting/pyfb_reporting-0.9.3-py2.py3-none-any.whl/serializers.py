from . import models

from rest_framework import serializers


class CDRSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.CDR
        fields = (
            'pk',
            'customer_ip',
            'aleg_uuid',
            'bleg_uuid',
            'rtp_uuid',
            'caller_number',
            'callee_number',
            'chan_name',
            'start_stamp',
            'answered_stamp',
            'end_stamp',
            'duration', 
            'read_codec',
            'write_codec',
            'sip_code',
            'sip_reason',
            'cost_rate',
            'total_sell',
            'total_cost',
            'rate',
            'sip_charge_info',
            'sip_user_agent',
            'sip_rtp_rxstat',
            'sip_rtp_txstat',
            'kamailio_server',
            'hangup_disposition',
            'direction',
        )


class DimDateSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimDate
        fields = (
            'pk',
            'date',
            'day',
            'day_of_week',
            'hour',
            'month',
            'quarter',
            'year',
        )


class DimCustomerHangupcauseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimCustomerHangupcause
        fields = (
            'pk',
            'hangupcause',
            'total_calls',
            'direction',
        )


class DimCustomerSipHangupcauseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimCustomerSipHangupcause
        fields = (
            'pk',
            'sip_hangupcause',
            'total_calls',
            'direction',
        )


class DimProviderHangupcauseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimProviderHangupcause
        fields = (
            'pk',
            'hangupcause',
            'total_calls',
            'direction',
        )


class DimProviderSipHangupcauseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimProviderSipHangupcause
        fields = (
            'pk',
            'sip_hangupcause',
            'total_calls',
            'direction',
        )


class DimCustomerDestinationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimCustomerDestination
        fields = (
            'pk',
            'total_calls',
            'success_calls',
            'total_duration',
            'avg_duration',
            'max_duration',
            'min_duration',
            'total_sell',
            'total_cost',
            'direction',
        )


class DimProviderDestinationSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.DimProviderDestination
        fields = (
            'pk',
            'total_calls',
            'success_calls',
            'total_duration',
            'avg_duration',
            'max_duration',
            'min_duration',
            'total_sell',
            'total_cost',
            'direction',
        )
