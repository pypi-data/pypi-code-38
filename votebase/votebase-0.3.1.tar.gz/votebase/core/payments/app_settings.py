# -*- coding: utf-8

from django.conf import settings
from django.utils.translation import ugettext_lazy as _

COMMERCE_URL = getattr(settings, 'COMMERCE_URL', 'http://www.example.com')
COMMERCE_CURRENCY = getattr(settings, 'COMMERCE_CURRENCY', u'?.?')
COMMERCE_TAX = getattr(settings, 'COMMERCE_TAX', 20)
COMMERCE_EMAIL_FROM = getattr(settings, 'COMMERCE_EMAIL_FROM', 'info@example.com')

COMMERCE_ID = getattr(settings, 'COMMERCE_ID', '46 706 291')
COMMERCE_TAX_ID = getattr(settings, 'COMMERCE_TAX_ID', '2023537813')
COMMERCE_VAT = getattr(settings, 'COMMERCE_VAT', 'SK2023537813')

COMMERCE_VARIABLE_SYMBOL_PREFIX = getattr(settings, 'COMMERCE_VARIABLE_SYMBOL_PREFIX', '00')

# States
COMMERCE_STATE_NEW = 'NEW'
COMMERCE_STATE_CANCELED = 'CANCELED'
COMMERCE_STATE_ERROR = 'ERROR'
COMMERCE_STATE_PENDING = 'PENDING'
COMMERCE_STATE_FINISHED = 'FINISHED'


STATES = (
    (COMMERCE_STATE_NEW, _(u'New order')),
    (COMMERCE_STATE_CANCELED, _(u'Canceled')),
    (COMMERCE_STATE_ERROR, _(u'Error')),
    (COMMERCE_STATE_PENDING, _(u'Pending')),
    (COMMERCE_STATE_FINISHED, _(u'Finished')),
    )
COMMERCE_STATES = getattr(settings, 'COMMERCE_STATES', STATES)