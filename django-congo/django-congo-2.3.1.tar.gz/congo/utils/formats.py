# -*- coding: utf-8 -*-
from django.utils.formats import number_format as _number_format, get_format

def number_format(value, decimal_pos = None, use_l10n = None, force_grouping = False, strip_decimal_part = False):
    number = _number_format(value, decimal_pos, use_l10n, force_grouping)
    if decimal_pos and strip_decimal_part:
        number = number.rstrip('0').rstrip(get_format('DECIMAL_SEPARATOR'))
    return number
