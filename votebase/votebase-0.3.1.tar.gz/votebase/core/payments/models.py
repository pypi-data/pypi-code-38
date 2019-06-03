from __future__ import division

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.timezone import now
from django.utils.translation import ugettext_lazy as _
from django_countries import CountryField

from votebase.core.accounts.models import Profile
from votebase.core.payments.app_settings import COMMERCE_STATES, \
    COMMERCE_STATE_NEW, COMMERCE_TAX, COMMERCE_VARIABLE_SYMBOL_PREFIX
from votebase.core.payments.managers import OrderQuerySet


User = get_user_model()


class Order(models.Model):
    user = models.ForeignKey(User, verbose_name=_(u'user'))
    package = models.CharField(_(u'package'), max_length=32,
        choices=Profile.PACKAGES, blank=False, null=False)
    package_valid_to = models.DateTimeField(_(u'package valid to'), default=now)
    total = models.FloatField(_(u'total'))
    state = models.CharField(
        _(u'state'),
        max_length=70, choices=COMMERCE_STATES, default=COMMERCE_STATE_NEW)
    REF = models.CharField(_(u"Merchant's payment identification"),
        max_length=10, blank=False, null=False, unique=True)
    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))
    objects = OrderQuerySet.as_manager()

    class Meta:
        app_label = 'payments'
        db_table = 'votebase_orders'
        verbose_name = _(u'order')
        verbose_name_plural = _(u'orders')
        ordering = ('-pk', )

    def __unicode__(self):
        return self.identifier()

    def save(self, **kwargs):
        self.modified = now()
        super(Order, self).save(**kwargs)
        self.REF = self.get_variable_symbol()
        super(Order, self).save(**kwargs)

    def identifier(self):
        return '#%(ident)s' % {
            'ident': str(self.pk).zfill(6)
        }

    def subtotal(self):
        return self.total / ((COMMERCE_TAX + 100) / 100)

    def tax(self):
        return self.total * (COMMERCE_TAX / 100)

    def get_information(self):
        return self.information_set.all()[0]

    def get_variable_symbol(self):
        return '%(year)s%(prefix)s%(pk)s' % {
            'year': str(now().year)[2:],
            'prefix': COMMERCE_VARIABLE_SYMBOL_PREFIX,
            'pk': str(self.pk).zfill(6)
        }


class Information(models.Model):
    order = models.ForeignKey(Order, verbose_name=_(u'order'))

    company_name = models.CharField(
        _(u'company'),
        max_length=255, default=None, blank=True, null=True)
    company_id = models.CharField(
        _(u'ID'), max_length=255, default=None, blank=True, null=True)
    company_tax_id = models.CharField(
        _(u'TAX ID'), max_length=255, default=None, blank=True, null=True)
    company_vat = models.CharField(
        _(u'VAT'), max_length=255, default=None, blank=True, null=True)

    first_name = models.CharField(u'first name', max_length=255)
    last_name = models.CharField(u'last name', max_length=255)
    street_and_number = models.CharField(
        _(u'street and no.'), max_length=255)
    city = models.CharField(_(u'city'), max_length=255)
    zip = models.CharField(_(u'ZIP'), max_length=255)
    country = CountryField()
    phone = models.CharField(
        _(u'phone'), max_length=255, default=None, blank=True, null=True)

    created = models.DateTimeField(_(u'created'), default=now)
    modified = models.DateTimeField(_(u'modified'))

    class Meta:
        app_label = 'payments'
        db_table = 'votebase_information'
        verbose_name = _(u'information')
        verbose_name_plural = _(u'information')
        ordering = ('-created', )

    def save(self, **kwargs):
        self.modified = now()
        super(Information, self).save(**kwargs)
