from django.db import models
from django.forms.widgets import PasswordInput
from django.utils.translation import ugettext_lazy as _


class PasswordField(models.CharField):
    def formfield(self, **kwargs):
        kwargs.update({'widget': PasswordInput})
        return super().formfield(**kwargs)


class Gateway(models.Model):
    CURRENCIES = ('CZK', 'EUR', 'USD')
    CURRENCY_BASE_UNITS = {
        'CZK': 100,
        'EUR': 100,
        'USD': 100,
    }
    LANGS = ('CS-CZ', 'SK-SK', 'EN-US', 'RU-RU', 'JA-JP')

    name = models.CharField(_('name'), max_length=64)
    slug = models.SlugField(_('slug'), max_length=64)
    merchant_id = models.CharField(_('merchant identifier'), max_length=64)
    shop_id = models.CharField(_('shop identifier'), max_length=64)
    secret_key = PasswordField(_('secret key'), max_length=64)
    default_currency = models.CharField(_('default currency'), max_length=3, choices=tuple(
        (currency, currency) for currency in CURRENCIES
    ))
    default_lang = models.CharField(_('default language'), max_length=5, choices=tuple(
        (lang, lang) for lang in LANGS
    ))

    def __str__(self):
        return self.name


class Payment(models.Model):
    NOT_REALIZED = 2
    REALIZED = 3
    STATES = {
        NOT_REALIZED: _('not realized'),
        REALIZED: _('successful'),
    }

    gateway = models.ForeignKey(Gateway, verbose_name=_('gateway'), on_delete=models.PROTECT, related_name='payments')
    created = models.DateTimeField(_('created'), auto_now_add=True)
    payment_id = models.CharField(_('payment identifier'), max_length=100)
    order_id = models.CharField(_('order identifier'), db_index=True, max_length=100)
    currency = models.CharField(_('currency'), max_length=3)
    amount = models.BigIntegerField(_('amount'), help_text=_('amount in the smallest (base) currency unit'))
    base_units = models.PositiveIntegerField(_('base units'), help_text=_('number of base units in currency'))
    status = models.PositiveSmallIntegerField(_('payment status'), choices=sorted(STATES.items()))
    status_description = models.TextField(_('payment status description'))

    class Meta:
        ordering = ('created',)
        unique_together = (('gateway', 'payment_id'),)
        verbose_name = _('payment')
        verbose_name_plural = _('payments')

    def __str__(self):
        return self.payment_id
