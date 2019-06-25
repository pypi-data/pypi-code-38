# -*- coding: utf-8 -*-
'''
Describe report accounting viewer for Django

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

from django.db.models.aggregates import Sum
from django.utils import six

from diacamma.accounting.models import format_devise, EntryLineAccount, ChartsAccount, Budget, Third
from diacamma.accounting.tools import correct_accounting_code


def get_spaces(size):
    return ''.ljust(size, '-').replace('-', '&#160;')


def credit_debit_way(data_line):
    if 'account' in data_line.keys():
        account = ChartsAccount.objects.get(id=data_line['account'])
        return account.credit_debit_way()
    elif 'code' in data_line.keys():
        account_code = correct_accounting_code(data_line['code'])
        account = ChartsAccount.get_chart_account(account_code)
        return account.credit_debit_way()
    return 0


def get_totalaccount_for_query(query, sign_value=None, with_third=False):
    total = 0
    values = {}
    if with_third:
        fields = ['account', 'third']
    else:
        fields = ['account']
    for data_line in EntryLineAccount.objects.filter(query).order_by(*fields).values(*fields).annotate(data_sum=Sum('amount')):
        if abs(data_line['data_sum']) > 0.001:
            account = ChartsAccount.objects.get(id=data_line['account'])
            account_code = correct_accounting_code(account.code)
            if ('third' in data_line.keys()) and (data_line['third'] is not None):
                account_code = "%s#%s" % (account_code, data_line['third'])
                third = Third.objects.get(id=data_line['third'])
                account_title = "[%s %s]" % (account.code, six.text_type(third))
            else:
                account_title = account.get_name()
            amount = None
            if sign_value is None:
                amount = data_line['data_sum']
            elif isinstance(sign_value, bool):
                if sign_value:
                    amount = credit_debit_way(data_line) * data_line['data_sum']
                else:
                    amount = -1 * credit_debit_way(data_line) * data_line['data_sum']
            else:
                amount = sign_value * credit_debit_way(data_line) * data_line['data_sum']
                if (amount < 0):
                    amount = None
            if amount is not None:
                if account_code not in values.keys():
                    values[account_code] = [0, account_title]
                values[account_code][0] += amount
                total += amount
    return values, total


def get_totalbudget_for_query(query):
    total = 0
    values = {}
    for data_line in Budget.objects.filter(query).order_by('code').values('code').annotate(data_sum=Sum('amount')):
        if abs(data_line['data_sum']) > 0.001:
            account = ChartsAccount.get_chart_account(data_line['code'])
            account_code = account.code
            account_title = account.get_name()
            amount = data_line['data_sum']
            if account_code not in values.keys():
                values[account_code] = [0, account_title]
            values[account_code][0] += amount
            total += amount
    return values, total


def convert_query_to_account(query1, query2=None, query_budget=None, sign_value=None, with_third=False):
    def check_account(account_code, account_title):
        if account_code not in dict_account.keys():
            dict_account[account_code] = [account_title, None, None]
            if isinstance(query_budget, list):
                for _item in query_budget:
                    dict_account[account_code].append(None)
            else:
                dict_account[account_code].append(None)
    dict_account = {}
    values1, total1 = get_totalaccount_for_query(query1, sign_value, with_third)
    for account_code in values1.keys():
        check_account(account_code, values1[account_code][1])
        dict_account[account_code][1] = values1[account_code][0]
    if query2 is not None:
        values2, total2 = get_totalaccount_for_query(query2, sign_value, with_third)
        for account_code in values2.keys():
            check_account(account_code, values2[account_code][1])
            dict_account[account_code][2] = values2[account_code][0]
    else:
        total2 = 0
    if query_budget is not None:
        if isinstance(query_budget, list):
            query_budget_list = query_budget
        else:
            query_budget_list = [query_budget]
        total_b = []
        id_dict = 3
        for query_budget_item in query_budget_list:
            valuesb, total3 = get_totalbudget_for_query(query_budget_item)
            for account_code in valuesb.keys():
                check_account(account_code, valuesb[account_code][1])
                dict_account[account_code][id_dict] = valuesb[account_code][0]
            id_dict += 1
            total_b.append(total3)
        if isinstance(query_budget, list):
            total3 = total_b
        else:
            total3 = total_b[0]
    else:
        total3 = 0
    res = []
    keys = sorted(dict_account.keys())
    for key in keys:
        res.append(dict_account[key])
    return res, total1, total2, total3


def add_cell_in_grid(grid, line_idx, colname, value):
    grid.set_value("L%04d" % line_idx, colname, value)


def add_item_in_grid(grid, line_idx, side, data_item, formttext='%s'):
    add_cell_in_grid(grid, line_idx, side, formttext % data_item[0])
    add_cell_in_grid(grid, line_idx, side + '_n', formttext % format_devise(data_item[1], 5))
    if data_item[2] is not None:
        add_cell_in_grid(grid, line_idx, side + '_n_1', formttext % format_devise(data_item[2], 5))
    if data_item[3] is not None:
        add_cell_in_grid(grid, line_idx, side + '_b', formttext % format_devise(data_item[3], 5))


def fill_grid(grid, index_begin, side, data_line):
    line_idx = index_begin
    for data_item in data_line:
        add_item_in_grid(grid, line_idx, side, data_item)
        line_idx += 1
    return line_idx
