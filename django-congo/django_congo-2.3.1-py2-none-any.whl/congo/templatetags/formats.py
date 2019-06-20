# -*- coding: utf-8 -*-
from decimal import Decimal, InvalidOperation
from django.utils.numberformat import format
from congo.utils.moneyed.classes import Money, get_currency
from congo.utils.moneyed.localization import format_money
from congo.utils.formats import number_format
from congo.utils.l10n import get_money_locale
from django.utils.formats import get_format as get_format_
from django.template import Library

register = Library()

@register.simple_tag
def get_format(format_type, lang = None, use_l10n = None):
    return get_format_(format_type, lang, use_l10n)

# decimal

@register.filter
def decimalformat(value):
    value = str(value).rstrip('0') or '0'
    return format(value, '.', 2)

@register.filter
def percentformat(value, decimal_pos = None):
    try:
        value = str(Decimal(value) * 100).rstrip('0') or 0
        return number_format(value, decimal_pos = decimal_pos, strip_decimal_part = True) + u"%"
    except InvalidOperation:
        return value

@register.filter
def ratingformat(value):
    return format(value, '.', 1)

# money

@register.filter
def moneyformat(value, currency = 'PLN', decimal_pos = 2, locale = None):
    locale = get_money_locale(locale)

    if isinstance(value, Money):
        pass
    else:
        value = Money(value, currency = get_currency(str(currency)))

    return format_money(value, decimal_places = decimal_pos, locale = locale)

@register.simple_tag
def money(value, currency = 'PLN', decimal_pos = 2, locale = None):
    return moneyformat(value, currency = currency, decimal_pos = decimal_pos, locale = locale)

# units

@register.filter
def sizeformat(value, convert_unit = True, decimal_pos = None):
    if convert_unit and value > 100:
        value = value / 100
        unit = 'm'
    else:
        unit = 'cm'

    return "%s %s" % (number_format(value, decimal_pos = decimal_pos, strip_decimal_part = True), unit)

@register.simple_tag(name = 'sizeformat')
def sizeformat_tag(*args, **kwargs):
    return sizeformat(*args, **kwargs)

@register.filter
def distanceformat(value, unit = 'km', decimal_pos = None):
    if float(str(value)) < 1 and unit == 'km':
        value = float(str(value)) * 1000.
        unit = 'm'

    return "%s %s" % (number_format(value, decimal_pos = decimal_pos, strip_decimal_part = True), unit)

register.simple_tag(distanceformat)

@register.filter
def dimensionformat(value, unit = 'm', decimal_pos = None):
    return "%s %s" % (number_format(value, decimal_pos = decimal_pos, strip_decimal_part = True), unit)

@register.filter
def capacityformat(value, convert_unit = True):
    if convert_unit and value > 1000:
        value = value / 1000
        unit = 'l'
    else:
        unit = 'ml'

    return "%s %s" % (number_format(value, decimal_pos = 2, strip_decimal_part = True), unit)

@register.filter
def weightformat(value, convert_unit = True):
    if convert_unit and value < 1:
        value = value * 1000
        unit = 'g'
    else:
        unit = 'kg'

    return "%s %s" % (number_format(value, decimal_pos = 2, strip_decimal_part = True), unit)

@register.filter
def voltageformat(value):
    return "%s V" % number_format(value, decimal_pos = 2, strip_decimal_part = True)

@register.filter
def amperageformat(value):
    return "%s A" % number_format(value, decimal_pos = 2, strip_decimal_part = True)

@register.filter
def powerformat(value):
    return "%s W" % number_format(value, decimal_pos = 2, strip_decimal_part = True)

# string

@register.filter
def urlformat(value):
    if value:
        if value.startswith('https://'):
            result = value.replace("https://", "")
        elif value.startswith('http://'):
            result = value.replace("http://", "")
        else:
            result = value
        return result

# @FG? nie podoba mi sie to - po co to?
@register.filter
def geturl(value):
    if value.startswith('https://'):
        pass
    elif value.startswith('http://'):
        pass
    else:
        return "%s%s" % ('http://', value)

@register.filter
def hourformat(value):
    if value:
        value = value.split(":")

        hours = int(value[0])
        minutes = int(value[1])

        if len(str(hours)) == 1:
            hours = "0%s" % hours

        if len(str(minutes)) == 1:
            minutes = "0%s" % minutes

        time = "%s:%s" % (hours, minutes)
        return time
