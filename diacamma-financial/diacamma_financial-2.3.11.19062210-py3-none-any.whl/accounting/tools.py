# -*- coding: utf-8 -*-
'''
tools for accounting package

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@copyright: 2015 sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _

from lucterios.CORE.parameters import Params

from diacamma.accounting.system import get_accounting_system


def current_system_account():
    import sys
    current_module = sys.modules[__name__]
    if not hasattr(current_module, 'SYSTEM_ACCOUNT_CACHE'):
        setattr(current_module, 'SYSTEM_ACCOUNT_CACHE', get_accounting_system(Params.getvalue("accounting-system")))
    return current_module.SYSTEM_ACCOUNT_CACHE


def clear_system_account():
    import sys
    current_module = sys.modules[__name__]

    if hasattr(current_module, 'SYSTEM_ACCOUNT_CACHE'):
        del current_module.SYSTEM_ACCOUNT_CACHE


def get_amount_sum(val):
    if val['amount__sum'] is None:
        return 0
    else:
        return val['amount__sum']


def currency_round(amount):
    currency_decimal = Params.getvalue("accounting-devise-prec")
    try:
        return round(float(amount), currency_decimal)
    except Exception:
        return round(0.0, currency_decimal)


def correct_accounting_code(code):
    if current_system_account().has_minium_code_size():
        code_size = Params.getvalue("accounting-sizecode")
        while len(code) > code_size and code[-1] == '0':
            code = code[:-1]
        while len(code) < code_size:
            code += '0'
    return code


def format_devise(amount, mode):

    # mode 0 25.45 => 25,45€ / -25.45 =>

    # mode 1 25.45 => Credit 25,45€ / -25.45 => Debit 25,45€
    # mode 2 25.45 => {[font color="green"]}Credit 25,45€{[/font]}     /
    # -25.45 => {[font color="blue"]}Debit 25,45€{[/font]}

    # mode 3 25.45 => 25,45 / -25.45 => -25.45
    # mode 4 25.45 => 25,45€ / -25.45 => 25.45€
    # mode 5 25.45 => 25,45€ / -25.45 => -25.45€
    # mode 6 25.45 => {[font color="green"]}25,45€{[/font]}     /
    # -25.45 => {[font color="blue"]}25,45€{[/font]}
    from decimal import InvalidOperation
    result = ''
    currency_short = Params.getvalue("accounting-devise")
    currency_decimal = Params.getvalue("accounting-devise-prec")
    currency_format = "%%0.%df" % currency_decimal
    currency_epsilon = pow(10, -1 * currency_decimal - 1)
    try:
        if (amount is None) or (abs(amount) < currency_epsilon):
            amount = 0
    except InvalidOperation:
        return "???"
    if (abs(amount) >= currency_epsilon) or (mode in (1, 2, 6)):
        if amount >= 0:
            if mode in (2, 6):
                result = '{[font color="green"]}'
            if (mode == 1) or (mode == 2):
                result = '%s%s: ' % (result, _('Credit'))
        else:
            if mode in (2, 6):
                result = result + '{[font color="blue"]}'
            if (mode == 1) or (mode == 2):
                result = '%s%s: ' % (result, _('Debit'))
    if mode == 3:
        result = currency_format % amount
    elif mode == 0:
        if amount >= currency_epsilon:
            result = currency_format % abs(amount) + currency_short
    elif mode == 6:
        if abs(amount) >= currency_epsilon:
            result = result + currency_format % abs(amount) + currency_short
    else:
        if mode < 5:
            amount_text = currency_format % abs(amount)
        else:
            amount_text = currency_format % amount
        result = result + amount_text + currency_short
    if mode in (2, 6):
        result = result + '{[/font]}'
    return result
