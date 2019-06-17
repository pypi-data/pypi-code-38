# -*- coding: utf-8 -*-

from django.urls import reverse
from django.db import models
from django.utils.translation import ugettext_lazy as _

from pyfb_direction.models import Destination
from pyfb_endpoint.models import CustomerEndpoint, ProviderEndpoint
from pyfb_kamailio.models import RtpEngine
from pyfb_routing.models import RoutingGroup
from pyfb_rating.models import CustomerRatecard, ProviderRatecard
from pyfb_company.models import Customer, Provider


# choices
CALLS_TYPE_CHOICES = (
    ('pstn', _(u"Outbound calls")),
    ('did', _(u"DID - Inbound calls")),
    ('pstn2did', _(u"Outbound calls to internal DID")),
    ('emergency', _(u"Emergency calls"))
)


class CDR(models.Model):

    # Fields
    customer_ip = models.CharField(_(u"customer IP address"), max_length=100, null=True, help_text=_(u"Customer IP address."))
    aleg_uuid = models.CharField(_(u"a leg call-ID"), max_length=100, null=True)
    bleg_uuid = models.CharField(_(u"b leg call-ID"), null=True, default="", max_length=100)
    rtp_uuid = models.CharField(_(u"media call-ID"), max_length=100, null=True)
    caller_number = models.CharField(_(u"caller ID num"), max_length=100, null=True)
    callee_number = models.CharField(_(u"Dest. number"), max_length=100, null=True)
    chan_name = models.CharField(_(u"channel name"), max_length=100, null=True)
    start_stamp = models.DateTimeField(_(u"start time"), null=True, db_index=True)
    answered_stamp = models.DateTimeField(_(u"answered time"), null=True)
    end_stamp = models.DateTimeField(_(u"hangup time"), null=True)
    duration = models.IntegerField(_(u"global duration"), null=True)
    effectiv_duration = models.IntegerField(_(u"total duration"), null=True, help_text=_(u"Global call duration since call has been received by the switch in ms."))
    effective_duration = models.IntegerField(_(u"effective duration"), null=True, help_text=_(u"real call duration in s."))
    billsec = models.IntegerField(_(u"billed duration"), null=True, help_text=_(u"billed call duration in s."))
    read_codec = models.CharField(_(u"read codec"), max_length=20, null=True)
    write_codec = models.CharField(_(u"write codec"), max_length=20, null=True)
    sip_code = models.CharField(_(u"hangup SIP code"), max_length=3, null=True, db_index=True)
    sip_reason = models.TextField(_(u"hangup SIP reason"), max_length=255, null=True)
    cost_rate = models.DecimalField(_(u'buy rate'), max_digits=11, decimal_places=5, default="0", null=True)
    total_sell = models.DecimalField(_(u'total sell'), max_digits=11, decimal_places=5, default="0", null=True)
    total_cost = models.DecimalField(_(u'total cost'), max_digits=11, decimal_places=5, default="0", null=True)
    rate = models.DecimalField(_(u'sell rate'), max_digits=11, decimal_places=5, null=True)
    init_block = models.DecimalField(_(u'Connection fee'), max_digits=11, decimal_places=5, null=True)
    block_min_duration = models.IntegerField(_(u'increment'), null=True)
    sip_charge_info = models.CharField( _(u'charge info'), null=True, max_length=100, help_text=_(u"Contents of the P-Charge-Info header for billing purpose."))
    sip_user_agent = models.CharField(_(u'sip user agent'), null=True, max_length=100)
    sip_rtp_rxstat = models.CharField(_(u'sip rtp rx stat'), null=True, max_length=30)
    sip_rtp_txstat = models.CharField(_(u'sip rtp tx stat'), null=True, max_length=30)
    kamailio_server = models.IntegerField(_(u"SIP server"), default=1)
    hangup_disposition = models.CharField(_(u"hangup disposition"), null=True, default="", max_length=100)
    sip_hangup_cause = models.CharField(_(u"SIP hangup cause"), null=True, default="", max_length=100)
    direction = models.CharField(_(u"Type of call"), max_length=10, null=True, blank=True, help_text=_(u"""Type of calls."""))

    # Relationship Fields
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        verbose_name=_(u"customer"),
        null=True,
        related_name="customer_related"
    )
    provider_endpoint = models.ForeignKey(
        ProviderEndpoint,
        on_delete=models.CASCADE,
        related_name="cdrs",
        verbose_name=_(u"provider endpoint"),
        null=True
    )
    lcr_carrier_id = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        verbose_name=_(u"provider"),
        null=True,
        related_name="carrier_related"
    )
    ratecard_id = models.ForeignKey(
        CustomerRatecard,
        on_delete=models.CASCADE,
        related_name="cdrs",
        null=True,
        verbose_name=_(u"ratecard")
    )
    lcr_group_id = models.ForeignKey(
        RoutingGroup,
        on_delete=models.CASCADE,
        related_name="cdrs",
        null=True,
        verbose_name=_(u"routing group")
    )
    caller_destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="cdrs",
        verbose_name=_(u"caller destination"),
        blank=True,
        null=True
    )
    callee_destintaion = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="cdrs_2",
        verbose_name=_(u"calle destination"),
        blank=True,
        null=True
    )
    customer_endpoint = models.ForeignKey(
        CustomerEndpoint,
        on_delete=models.CASCADE,
        related_name="cdrs",
        verbose_name=_(u"customer endpoint"),
        null=True
    )
    media_server = models.ForeignKey(
        RtpEngine,
        on_delete=models.CASCADE,
        related_name="cdrs",
        verbose_name=_(u"Media server name"),
        null=True
    )

    class Meta:
        db_table = 'pyfb_reporting_cdr'
        ordering = ('-start_stamp',)
        verbose_name = _(u'cdr')
        verbose_name_plural = _(u'cdrs')

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_cdr_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_cdr_update', args=(self.pk,))


class DimDate(models.Model):

    # Fields
    date = models.DateTimeField()
    day = models.CharField(_(u'day'), max_length=2)
    day_of_week = models.CharField(_(u'day of the week'), max_length=30)
    hour = models.CharField(_(u'hour'), max_length=2, null=True, blank=True)
    month = models.CharField(_(u'month'), max_length=2)
    quarter = models.CharField(_(u'quarter'), max_length=2)
    year = models.CharField(_(u'year'), max_length=4)


    class Meta:
        db_table = 'pyfb_reporting_dim_date'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimdate_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimdate_update', args=(self.pk,))


class DimCustomerHangupcause(models.Model):

    # Fields
    hangupcause = models.CharField(_(u'hangupcause'), max_length=100, null=True, blank=True)
    total_calls = models.IntegerField(_(u"total calls"))
    direction = models.CharField(_(u"Type of call"), max_length=10, help_text=_(u"""Type of calls."""))

    # Relationship Fields
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="dimcustomerhangupcauses",
        verbose_name=_(u"customer")
    )
    date = models.ForeignKey(
        DimDate,
        on_delete=models.CASCADE,
        related_name="dimcustomerhangupcauses",
        verbose_name=_(u"date")
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="dimcustomerhangupcauses", 
    )

    class Meta:
        db_table = 'pyfb_reporting_dim_cust_hc'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimcustomerhangupcause_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimcustomerhangupcause_update', args=(self.pk,))


class DimCustomerSipHangupcause(models.Model):

    # Fields
    sip_hangupcause = models.CharField(_(u'sip hangupcause'), max_length=100, null=True, blank=True)
    total_calls = models.IntegerField(_(u"total calls"))
    direction = models.CharField(_(u"Type of call"), max_length=10, choices=CALLS_TYPE_CHOICES, default="pstn", help_text=_(u"""Type of calls."""))

    # Relationship Fields
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="dimcustomersiphangupcauses",
        verbose_name=_(u"customer")
    )
    date = models.ForeignKey(
        DimDate,
        on_delete=models.CASCADE,
        related_name="dimcustomersiphangupcauses",
        verbose_name=_(u"date")
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="dimcustomersiphangupcauses", 
    )

    class Meta:
        db_table = 'pyfb_reporting_dim_cust_sip_hc'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimcustomersiphangupcause_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimcustomersiphangupcause_update', args=(self.pk,))


class DimProviderHangupcause(models.Model):

    # Fields
    hangupcause = models.CharField(_(u'hangupcause'), max_length=100, null=True, blank=True)
    total_calls = models.IntegerField(_(u"total calls"))
    direction = models.CharField(_(u"Type of call"), max_length=10, choices=CALLS_TYPE_CHOICES, default="pstn", help_text=_(u"""Type of calls."""))

    # Relationship Fields
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="dimproviderhangupcauses",
        verbose_name=_(u"provider")
    )
    date = models.ForeignKey(
        DimDate,
        on_delete=models.CASCADE,
        related_name="dimproviderhangupcauses",
        verbose_name=_(u"date")
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="dimproviderhangupcauses", 
    )

    class Meta:
        db_table = 'pyfb_reporting_dim_prov_hc'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimproviderhangupcause_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimproviderhangupcause_update', args=(self.pk,))


class DimProviderSipHangupcause(models.Model):

    # Fields
    sip_hangupcause = models.CharField(_(u'sip hangupcause'), max_length=100, null=True, blank=True)
    total_calls = models.IntegerField(_(u"total calls"))
    direction = models.CharField(_(u"Type of call"), max_length=10, choices=CALLS_TYPE_CHOICES, default="pstn", help_text=_(u"""Type of calls."""))

    # Relationship Fields
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="dimprovidersiphangupcauses",
        verbose_name=_(u"provider")
    )
    date = models.ForeignKey(
        DimDate,
        on_delete=models.CASCADE,
        related_name="dimprovidersiphangupcauses",
        verbose_name=_(u"date")
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="dimprovidersiphangupcauses", 
    )

    class Meta:
        db_table = 'pyfb_reporting_dim_prov_sip_hc'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimprovidersiphangupcause_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimprovidersiphangupcause_update', args=(self.pk,))


class DimCustomerDestination(models.Model):

    # Fields
    total_calls = models.IntegerField(_(u"total calls"), default=0)
    success_calls = models.IntegerField(_(u"success calls"), default=0)
    total_duration = models.IntegerField(_(u"total duration"), default=0)
    avg_duration = models.IntegerField(_(u"average duration"), default=0)
    max_duration = models.IntegerField(_(u"max duration"), default=0)
    min_duration = models.IntegerField(_(u"min duration"), default=0)
    total_sell = models.DecimalField(_(u'total sell'), max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(_(u'total cost'), max_digits=12, decimal_places=2)
    direction = models.CharField(_(u"Type of call"), max_length=10, choices=CALLS_TYPE_CHOICES, default="pstn", help_text=_(u"""Type of calls."""))

    # Relationship Fields
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="dimcustomerdestinations",
        verbose_name=_(u"customer")
    )
    date = models.ForeignKey(
        DimDate,
        on_delete=models.CASCADE,
        related_name="dimcustomerdestinations",
        verbose_name=_(u"date")
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="dimcustomerdestinations", 
    )

    class Meta:
        db_table = 'pyfb_reporting_dim_cust_dest'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimcustomerdestination_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimcustomerdestination_update', args=(self.pk,))


class DimProviderDestination(models.Model):

    # Fields
    total_calls = models.IntegerField(_(u"total calls"), default=0)
    success_calls = models.IntegerField(_(u"success calls"), default=0)
    total_duration = models.IntegerField(_(u"total duration"), default=0)
    avg_duration = models.IntegerField(_(u"average duration"), default=0)
    max_duration = models.IntegerField(_(u"max duration"), default=0)
    min_duration = models.IntegerField(_(u"min duration"), default=0)
    total_sell = models.DecimalField(_(u'total sell'), max_digits=12, decimal_places=2)
    total_cost = models.DecimalField(_(u'total cost'), max_digits=12, decimal_places=2)
    direction = models.CharField(_(u"Type of call"), max_length=10, choices=CALLS_TYPE_CHOICES, default="pstn", help_text=_(u"""Type of calls."""))

    # Relationship Fields
    provider = models.ForeignKey(
        Provider,
        on_delete=models.CASCADE,
        related_name="dimproviderdestinations",
        verbose_name=_(u"provider")
    )
    date = models.ForeignKey(
        DimDate,
        on_delete=models.CASCADE,
        related_name="dimproviderdestinations",
        verbose_name=_(u"date")
    )
    destination = models.ForeignKey(
        Destination,
        on_delete=models.CASCADE,
        related_name="dimproviderdestinations", 
    )

    class Meta:
        db_table = 'pyfb_reporting_dim_prov_dest'
        ordering = ('-date',)

    def __str__(self):
        return u'%s' % self.pk

    def get_absolute_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimproviderdestination_detail', args=(self.pk,))


    def get_update_url(self):
        return reverse('pyfb-reporting:pyfb_reporting_dimproviderdestination_update', args=(self.pk,))


