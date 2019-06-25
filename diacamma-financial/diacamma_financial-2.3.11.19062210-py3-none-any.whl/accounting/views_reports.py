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
import sys
from datetime import date, datetime

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from django.db.models.aggregates import Sum
from django.utils import six, formats

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, CLOSE_NO, FORMTYPE_REFRESH, WrapAction, convert_date, ActionsManage, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerCustom
from lucterios.framework.xfercomponents import XferCompImage, XferCompSelect, XferCompLabelForm, XferCompGrid, XferCompEdit, XferCompCheck
from lucterios.framework.xferadvance import TITLE_PRINT, TITLE_CLOSE
from lucterios.framework.models import get_value_converted
from lucterios.contacts.models import LegalEntity
from lucterios.CORE.xferprint import XferPrintAction

from diacamma.accounting.models import FiscalYear, format_devise, EntryLineAccount, ChartsAccount, CostAccounting, Third
from diacamma.accounting.tools import correct_accounting_code, current_system_account
from diacamma.accounting.tools_reports import get_spaces, convert_query_to_account,\
    add_cell_in_grid, fill_grid, add_item_in_grid
from lucterios.CORE.parameters import Params
import re


class FiscalYearReport(XferContainerCustom):
    icon = "accountingReport.png"
    model = FiscalYear
    field_id = 'year'
    add_filtering = False
    force_date_filter = False

    def __init__(self, **kwargs):
        XferContainerCustom.__init__(self, **kwargs)
        self.filter = None
        self.lastfilter = None
        self.budgetfilter_left = None
        self.budgetfilter_right = None
        self.total_summary_left = (0, 0, 0)
        self.total_summary_right = (0, 0, 0)
        self.result = (0, 0, 0)
        self.line_offset = 0

    def fillresponse(self):
        self.fill_header()
        self.calcul_table()
        self.fill_body()
        self.fill_buttons()

    def define_gridheader(self):
        pass

    def fill_filterheader(self):
        pass

    def fill_filterCode(self):
        if self.add_filtering:
            filtercode = self.getparam('filtercode', Params.getvalue("accounting-code-report-filter"))
            edt = XferCompEdit('filtercode')
            edt.set_value(filtercode)
            edt.is_default = True
            edt.description = _("Accounting code starting with")
            edt.set_location(1, 3, 3)
            edt.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            self.add_component(edt)
            if filtercode != '':
                self.filter &= Q(account__code__startswith=filtercode)

    def fill_header(self):
        self.item = FiscalYear.get_current(self.getparam("year"))
        new_begin = convert_date(self.getparam("begin"), self.item.begin)
        new_end = convert_date(self.getparam("end"), self.item.end)
        if (new_begin >= self.item.begin) and (new_end <= self.item.end):
            self.item.begin = new_begin
            self.item.end = new_end
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)

        select_year = XferCompSelect(self.field_id)
        select_year.set_location(1, 0, 5)
        select_year.set_select_query(FiscalYear.objects.all())
        select_year.set_value(self.item.id)
        select_year.set_needed(True)
        select_year.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(select_year)
        self.filter = Q(entry__year=self.item)
        if self.force_date_filter or self.item.status != 2:
            self.fill_from_model(1, 1, False, ['begin'])
            self.fill_from_model(3, 1, False, ['end'])
            begin_filter = self.get_components('begin')
            begin_filter.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            end_filter = self.get_components('end')
            end_filter.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
            self.filter &= Q(entry__date_value__gte=self.item.begin)
            self.filter &= Q(entry__date_value__lte=self.item.end)
        self.fill_filterCode()
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.total_result_text)
        lbl.set_location(0, 6, 6)
        self.add_component(lbl)
        self.fill_filterheader()
        self.define_gridheader()

    def add_total_in_grid(self, total_in_left, total1_left, total2_left, totalb_left, total1_right, total2_right, totalb_right, line_idx):
        self.result = (0.0, 0.0, 0.0)
        if (total2_left is None) or (total2_right is None):
            self.total_summary_left = (max(total1_left, total1_right), None, max(totalb_left, totalb_right))
            self.total_summary_right = (max(total1_left, total1_right), None, max(totalb_left, totalb_right))
        else:
            self.total_summary_left = (total1_left, total2_left, totalb_left)
            self.total_summary_right = (total1_right, total2_right, totalb_right)
        line_idx += 1
        add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left', '')
        line_idx += 1
        add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total'))
        add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(total1_left, 5))
        if self.lastfilter is not None:
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(total2_left, 5))
        if self.budgetfilter_left is not None:
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(totalb_left, 5))
        add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total'))
        add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(total1_right, 5))
        if self.lastfilter is not None:
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(total2_right, 5))
        if self.budgetfilter_right is not None:
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(totalb_right, 5))
        if (abs(total1_left - total1_right) > 0.0001) or ((total2_left is not None) and (total2_right is not None) and (abs(total2_left - total2_right) > 0.0001)):
            line_idx += 1
            if total_in_left:
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (profit)'))
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (deficit)'))
            else:
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (deficit)'))
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right', get_spaces(5) + "{[i]}%s{[/i]}" % _('result (profit)'))
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right_n', '')
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right_n_1', '')
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right_b', '')
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left_n', '')
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left_n_1', '')
            add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left_b', '')
            result_n = total1_right - total1_left
            if (total2_left is not None) and (total2_right is not None):
                result_n_1 = total2_right - total2_left
            else:
                result_n_1 = 0.0
            if (totalb_left is not None) and (totalb_right is not None):
                result_b = totalb_right - totalb_left
            else:
                result_b = 0.0
            self.result = (result_n, result_n_1, result_b)
            if total_in_left:
                if result_n > 0:
                    pos_n = 'left_n'
                else:
                    pos_n = 'right_n'
                if result_n_1 > 0:
                    pos_n_1 = 'left_n_1'
                else:
                    pos_n_1 = 'right_n_1'
                if result_b > 0:
                    pos_b = 'left_b'
                else:
                    pos_b = 'right_b'
            else:
                result_n = -1 * result_n
                result_n_1 = -1 * result_n_1
                if result_n > 0:
                    pos_n = 'right_n'
                else:
                    pos_n = 'left_n'
                if result_n_1 > 0:
                    pos_n_1 = 'right_n_1'
                else:
                    pos_n_1 = 'left_n_1'
                if result_b > 0:
                    pos_b = 'right_b'
                else:
                    pos_b = 'left_b'
            add_cell_in_grid(self.grid, self.line_offset + line_idx, pos_n, format_devise(abs(result_n), 5))
            if (totalb_left is not None) and (abs(result_b) > 0.0001):
                add_cell_in_grid(self.grid, self.line_offset + line_idx, pos_b, format_devise(abs(result_b), 5))
            else:
                pos_b = ""
            if (self.lastfilter is not None) and (abs(result_n_1) > 0.0001):
                add_cell_in_grid(self.grid, self.line_offset + line_idx, pos_n_1, format_devise(abs(result_n_1), 5))
            else:
                pos_n_1 = ""
            if (pos_n != 'left_n') and (pos_n_1 != 'left_n_1') and (pos_b != 'left_b'):
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'left', '')
            if (pos_n != 'right_n') and (pos_n_1 != 'right_n_1') and (pos_b != 'right_b'):
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'right', '')
        return line_idx

    def _add_left_right_accounting(self, left_filter, rigth_filter, total_in_left):
        data_line_left, total1_left, total2_left, totalb_left = convert_query_to_account(
            self.filter & left_filter, self.lastfilter & left_filter if self.lastfilter is not None else None, self.budgetfilter_left)
        data_line_right, total1_right, total2_right, totalb_right = convert_query_to_account(
            self.filter & rigth_filter, self.lastfilter & rigth_filter if self.lastfilter is not None else None, self.budgetfilter_right)
        line_idx = 0
        for line_idx in range(max(len(data_line_left), len(data_line_right))):
            if line_idx < len(data_line_left):
                add_item_in_grid(self.grid, self.line_offset + line_idx, 'left', data_line_left[line_idx])
            if line_idx < len(data_line_right):
                add_item_in_grid(self.grid, self.line_offset + line_idx, 'right', data_line_right[line_idx])
        return self.add_total_in_grid(total_in_left, total1_left, total2_left, totalb_left, total1_right, total2_right, totalb_right, line_idx)

    def calcul_table(self):
        pass

    def fill_body(self):
        self.grid.no_pager = True
        self.grid.set_location(0, 10, 6)
        self.add_component(self.grid)

    def fill_buttons(self):
        self.add_action(FiscalYearReportPrint.get_action(TITLE_PRINT, "images/print.png"),
                        close=CLOSE_NO, params={'classname': self.__class__.__name__})
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show balance sheet for current fiscal year'))
class FiscalYearBalanceSheet(FiscalYearReport):
    caption = _("Balance sheet")

    def fill_filterheader(self):
        if self.item.last_fiscalyear is not None:
            self.lastfilter = Q(entry__year=self.item.last_fiscalyear)
            lbl = XferCompLabelForm('sep_last')
            lbl.set_value("{[br/]}{[br/]}")
            lbl.set_location(2, 11, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('lbllast_year')
            lbl.set_value_as_name(self.item.last_fiscalyear.get_identify())
            lbl.set_location(1, 12)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_year')
            lbl.set_value(six.text_type(self.item.last_fiscalyear))
            lbl.set_location(2, 12, 4)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_result')
            lbl.set_value(self.item.last_fiscalyear.total_result_text)
            lbl.set_location(2, 13, 4)
            self.add_component(lbl)

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('left', _('Assets'))
        self.grid.add_header('left_n', self.item.get_identify())
        if self.lastfilter is not None:
            self.grid.add_header(
                'left_n_1', self.item.last_fiscalyear.get_identify())
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Liabilities'))
        self.grid.add_header('right_n', self.item.get_identify())
        if self.lastfilter is not None:
            self.grid.add_header(
                'right_n_1', self.item.last_fiscalyear.get_identify())

    def calcul_table(self):
        current_system_account().fill_fiscalyear_balancesheet(self.grid, self.filter, self.lastfilter)


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show income statement for current fiscal year'))
class FiscalYearIncomeStatement(FiscalYearReport):
    caption = _("Income statement")

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('left', _('Expense'))
        self.grid.add_header('left_n', self.item.get_identify())
        self.grid.add_header('left_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header('left_n_1', self.item.last_fiscalyear.get_identify())
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Revenue'))
        self.grid.add_header('right_n', self.item.get_identify())
        self.grid.add_header('right_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header('right_n_1', self.item.last_fiscalyear.get_identify())

    def fill_filterheader(self):
        if self.item.last_fiscalyear is not None:
            self.lastfilter = Q(entry__year=self.item.last_fiscalyear)
            lbl = XferCompLabelForm('sep_last')
            lbl.set_value("{[br/]}{[br/]}")
            lbl.set_location(2, 11, 3)
            self.add_component(lbl)
            lbl = XferCompLabelForm('lbllast_year')
            lbl.set_value_as_name(self.item.last_fiscalyear.get_identify())
            lbl.set_location(1, 12)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_year')
            lbl.set_value(six.text_type(self.item.last_fiscalyear))
            lbl.set_location(2, 12, 4)
            self.add_component(lbl)
            lbl = XferCompLabelForm('last_result')
            lbl.set_value(self.item.last_fiscalyear.total_result_text)
            lbl.set_location(2, 13, 4)
            self.add_component(lbl)

    def show_annexe(self, line_idx, budgetfilter):
        add_cell_in_grid(self.grid, self.line_offset + line_idx + 1, 'left', '')
        other_filter = Q(account__code__regex=current_system_account().get_annexe_mask())
        budget_other = Q(code__regex=current_system_account().get_annexe_mask())
        data_line_left, anx_total1_left, anx_total2_left, anx_totalb_left = convert_query_to_account(self.filter & other_filter,
                                                                                                     self.lastfilter & other_filter if self.lastfilter is not None else None,
                                                                                                     budgetfilter & budget_other,
                                                                                                     sign_value=-1)
        data_line_right, anx_total1_right, anx_total2_right, anx_totalb_right = convert_query_to_account(self.filter & other_filter,
                                                                                                         self.lastfilter & other_filter if self.lastfilter is not None else None,
                                                                                                         budgetfilter & budget_other,
                                                                                                         sign_value=1)
        if (len(data_line_left) > 0) or (len(data_line_right) > 0):
            add_cell_in_grid(self.grid, self.line_offset + line_idx + 1, 'left', get_spaces(20) + "{[i]}%s{[/i]}" % _('annexe'))
            add_cell_in_grid(self.grid, self.line_offset + line_idx + 1, 'right', get_spaces(20) + "{[i]}%s{[/i]}" % _('annexe'))
            left_line_idx = fill_grid(self.grid, self.line_offset + line_idx + 2, 'left', data_line_left)
            right_line_idx = fill_grid(self.grid, self.line_offset + line_idx + 2, 'right', data_line_right)
            max_line_idx = max(left_line_idx, right_line_idx)
            total1_left, total2_left, totalb_left = self.total_summary_left
            total1_right, total2_right, totalb_right = self.total_summary_right
            add_cell_in_grid(self.grid, max_line_idx, 'left', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total with annexe'))
            total1_left += anx_total1_left
            add_cell_in_grid(self.grid, max_line_idx, 'left_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total1_left, total1_right), 5))
            if self.lastfilter is not None:
                total2_left += anx_total2_left
                add_cell_in_grid(self.grid, max_line_idx, 'left_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total2_left, total2_right), 5))
            if self.budgetfilter_left is not None:
                totalb_left += anx_totalb_left
                add_cell_in_grid(self.grid, max_line_idx, 'left_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(totalb_left, totalb_right), 5))
            add_cell_in_grid(self.grid, max_line_idx, 'right', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('total with annexe'))
            total1_right += anx_total1_right
            add_cell_in_grid(self.grid, max_line_idx, 'right_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total1_left, total1_right), 5))
            if self.lastfilter is not None:
                total2_right += anx_total2_right
                add_cell_in_grid(self.grid, max_line_idx, 'right_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(total2_left, total2_right), 5))
            if self.budgetfilter_right is not None:
                totalb_right += anx_totalb_right
                add_cell_in_grid(self.grid, max_line_idx, 'right_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(max(totalb_left, totalb_right), 5))
            add_cell_in_grid(self.grid, max_line_idx + 1, 'left', '')
            add_cell_in_grid(self.grid, max_line_idx + 1, 'right', '')
        else:
            max_line_idx = self.line_offset - 1
        return max_line_idx + 1 - self.line_offset

    def calcul_table(self):
        self.budgetfilter_right = Q(year=self.item) & Q(code__regex=current_system_account().get_revenue_mask())
        self.budgetfilter_left = Q(year=self.item) & Q(code__regex=current_system_account().get_expence_mask())
        line_idx = self._add_left_right_accounting(Q(account__type_of_account=4), Q(account__type_of_account=3), True)
        self.show_annexe(line_idx, Q(year=self.item))


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show ledger for current fiscal year'))
class FiscalYearLedger(FiscalYearReport):
    caption = _("Ledger")
    add_filtering = True
    force_date_filter = True

    def __init__(self, **kwargs):
        FiscalYearReport.__init__(self, **kwargs)
        self.last_account = None
        self.last_third = None
        self.last_total = [0.0, 0.0]
        self.line_idx = 1

    def fill_filterCode(self):
        row = self.get_max_row() + 1
        self.only_nonull = self.getparam('only_nolink', False)
        edt = XferCompCheck('only_nolink')
        edt.set_value(self.only_nonull)
        edt.set_location(1, row)
        edt.description = _("Only entry without link")
        edt.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(edt)
        if self.only_nonull:
            self.filter &= Q(link__isnull=True) & Q(third__isnull=False)
            if self.getparam('filtercode', '') == '':
                third_mask = current_system_account().get_third_mask()
                while re.match("[0-9a-zA-Z]", third_mask[0]) is None:
                    third_mask = third_mask[1:]
                num_letter = 0
                while re.match("[0-9a-zA-Z]", third_mask[num_letter]) is not None:
                    num_letter += 1
                third_mask = third_mask[:num_letter]
                self.params['filtercode'] = third_mask
        FiscalYearReport.fill_filterCode(self)

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('entry.num', _('numeros'))
        self.grid.add_header('entry.date_entry', _('date entry'))
        self.grid.add_header('entry.date_value', _('date value'))
        self.grid.add_header('entry.designation', _('name'))
        self.grid.add_header('link', _('link'))
        self.grid.add_header('debit', _('debit'))
        self.grid.add_header('credit', _('credit'))

    def _add_total_account(self):
        if self.last_account is not None:
            add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'entry.designation', get_spaces(30) + "{[i]}%s{[/i]}" % _('total'))
            if self.last_account.credit_debit_way() == -1:
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'debit', "{[i]}%s{[/i]}" % format_devise(self.last_total[0], 4))
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'credit', "{[i]}%s{[/i]}" % format_devise(self.last_total[1], 4))
            else:
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'debit', "{[i]}%s{[/i]}" % format_devise(self.last_total[1], 4))
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'credit', "{[i]}%s{[/i]}" % format_devise(self.last_total[0], 4))
            self.line_idx += 1
            last_total = self.last_total[0] - self.last_total[1]
            add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'entry.designation', get_spaces(30) + "{[u]}{[i]}%s{[/i]}{[/u]}" % _('balance'))
            add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'debit', "{[u]}{[i]}%s{[/i]}{[/u]}" %
                             format_devise(max((0, -1 * self.last_account.credit_debit_way() * last_total)), 0))
            add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'credit', "{[u]}{[i]}%s{[/i]}{[/u]}" %
                             format_devise(max((0, self.last_account.credit_debit_way() * last_total)), 0 if abs(last_total) > 0.0001 else 4))
            self.line_idx += 1
            add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'entry.designation', '{[br/]}')
            self.line_idx += 1
            self.last_total = [0.0, 0.0]

    def calcul_table(self):
        self.line_idx = 1
        self.last_account = None
        self.last_third = None
        self.last_total = [0.0, 0.0]
        for line in EntryLineAccount.objects.filter(self.filter).distinct().order_by('account__code', 'third', 'entry__date_value'):
            if self.last_account != line.account:
                self._add_total_account()
                self.last_account = line.account
                self.last_third = None
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'entry.designation', get_spaces(15) + "{[u]}{[b]}%s{[/b]}{[/u]}" % six.text_type(self.last_account))
                self.line_idx += 1
            if self.last_third != line.third:
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, 'entry.designation', get_spaces(8) + "{[b]}%s{[/b]}" % six.text_type(line.entry_account))
                self.line_idx += 1
            self.last_third = line.third
            for header in self.grid.headers:
                add_cell_in_grid(self.grid, self.line_offset + self.line_idx, header.name, line.evaluate('#' + header.name))
            if line.amount > 0:
                self.last_total[0] += line.amount
            else:
                self.last_total[1] -= line.amount
            self.line_idx += 1
        self._add_total_account()


@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_NOMODAL, 'bookkeeping', _('Show trial balance for current fiscal year'))
class FiscalYearTrialBalance(FiscalYearReport):
    caption = _("Trial balance")
    add_filtering = True
    force_date_filter = True

    def fill_filterCode(self):
        FiscalYearReport.fill_filterCode(self)
        row = self.get_max_row() + 1

        self.only_nonull = self.getparam('only_nonull', False)
        edt = XferCompCheck('only_nonull')
        edt.set_value(self.only_nonull)
        edt.set_location(1, row)
        edt.description = _("Only no null")
        edt.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(edt)

        self.with_third = self.getparam('with_third', False)
        edt = XferCompCheck('with_third')
        edt.set_value(self.with_third)
        edt.set_location(2, row, 2)
        edt.description = _("Detail by third")
        edt.set_action(self.request, self.__class__.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(edt)

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        self.grid.add_header('designation', _('name'))
        self.grid.add_header('total_debit', _('debit sum'))
        self.grid.add_header('total_credit', _('credit sum'))
        self.grid.add_header('solde_debit', _('debit'))
        self.grid.add_header('solde_credit', _('credit'))

    def _get_balance_values(self):
        balance_values = {}
        if self.with_third:
            fields = ['account', 'third']
        else:
            fields = ['account']
        data_line_positifs = list(EntryLineAccount.objects.filter(self.filter & Q(amount__gt=0)).order_by(*fields).values(*fields).annotate(data_sum=Sum('amount')))
        data_line_negatifs = list(EntryLineAccount.objects.filter(self.filter & Q(amount__lt=0)).order_by(*fields).values(*fields).annotate(data_sum=Sum('amount')))
        for data_line in data_line_positifs + data_line_negatifs:
            if abs(data_line['data_sum']) > 0.0001:
                account = ChartsAccount.objects.get(id=data_line['account'])
                account_code = correct_accounting_code(account.code)
                if ('third' in data_line.keys()) and (data_line['third'] is not None):
                    account_code = "%s#%s" % (account_code, data_line['third'])
                if account_code not in balance_values.keys():
                    if ('third' in data_line.keys()) and (data_line['third'] is not None):
                        third = Third.objects.get(id=data_line['third'])
                        account_title = "[%s %s]" % (account.code, six.text_type(third))
                    else:
                        account_title = account.get_name()
                    balance_values[account_code] = [account_title, 0, 0]
                if (account.credit_debit_way() * data_line['data_sum']) > 0.0001:
                    balance_values[account_code][2] = account.credit_debit_way() * data_line['data_sum']
                else:
                    balance_values[account_code][1] = -1 * account.credit_debit_way() * data_line['data_sum']
        return balance_values

    def calcul_table(self):
        line_idx = 1
        balance_values = self._get_balance_values()
        keys = sorted(balance_values.keys())
        for key in keys:
            diff = balance_values[key][1] - balance_values[key][2]
            if (self.only_nonull is False) or (abs(diff) > 0.0001):
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'designation', balance_values[key][0])
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'total_debit', format_devise(balance_values[key][1], 5))
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'total_credit', format_devise(balance_values[key][2], 5))
                add_cell_in_grid(self.grid, self.line_offset + line_idx, 'solde_debit', format_devise(max(0, diff), 0))
                if abs(diff) < 0.0001:
                    add_cell_in_grid(self.grid, self.line_offset + line_idx, 'solde_credit', format_devise(0, 5))
                else:
                    add_cell_in_grid(self.grid, self.line_offset + line_idx, 'solde_credit', format_devise(max(0, -1 * diff), 0))
                line_idx += 1


@MenuManage.describ('accounting.change_fiscalyear')
class FiscalYearReportPrint(XferPrintAction):
    caption = _("Print report fiscal year")
    icon = "accountingReport.png"
    model = FiscalYear
    field_id = 'year'
    with_text_export = True
    tab_change_page = True

    def __init__(self):
        XferPrintAction.__init__(self)
        self.action_class = self.__class__.action_class
        self.caption = self.__class__.caption

    def get_report_generator(self):
        self.action_class = getattr(sys.modules[self.getparam("modulename", __name__)], self.getparam("classname", ''))
        gen = XferPrintAction.get_report_generator(self)
        own_struct = LegalEntity.objects.get(id=1)
        if self.item.status != 2:
            date_txt = formats.date_format(date.today(), "DATE_FORMAT")
        else:
            date_txt = ''
        gen.title = "{[u]}{[b]}%s{[/b]}{[/u]}{[br/]}{[i]}%s{[/i]}{[br/]}{[b]}%s{[/b]}" % (own_struct, self.action_class.caption, date_txt)
        gen.page_width = 297
        gen.page_height = 210
        return gen


@MenuManage.describ('accounting.change_fiscalyear')
class CostAccountingReportPrint(XferPrintAction):
    caption = _("Print report cost accounting")
    icon = "accountingReport.png"
    model = CostAccounting
    field_id = 'costaccounting'
    with_text_export = True
    tab_change_page = True

    def __init__(self):
        XferPrintAction.__init__(self)
        self.action_class = self.__class__.action_class
        self.caption = self.__class__.caption

    def get_report_generator(self):
        self.action_class = getattr(sys.modules[self.getparam("modulename", __name__)], self.getparam("classname", ''))
        gen = XferPrintAction.get_report_generator(self)
        own_struct = LegalEntity.objects.get(id=1)
        gen.title = "{[u]}{[b]}%s{[/b]}{[/u]}{[br/]}{[i]}%s{[/i]}{[br/]}{[b]}%s{[/b]}" % (
            own_struct, self.action_class.caption, formats.date_format(date.today(), "DATE_FORMAT"))
        gen.page_width = 297
        gen.page_height = 210
        return gen


class CostAccountingReport(FiscalYearReport):
    icon = "costAccounting.png"
    model = CostAccounting
    field_id = 'costaccounting'

    def fillresponse(self):
        self.fill_header()
        self.addNameCol = False
        for self.item in self.items:
            self.filter = Q(costaccounting=self.item)
            self.new_tab(six.text_type(self.item))
            self.define_gridheader()
            self.fill_filterheader()
            self.calcul_table()
            self.fill_body()
        self.fill_buttons()

    def define_gridheader(self):
        self.grid = XferCompGrid('report_%d' % self.item.id)
        if self.addNameCol:
            self.grid.add_header('name', _('Cost accounting'))
        self.grid.add_header('left', _('Expenses'))
        self.grid.add_header('left_n', _('Value'))
        self.grid.add_header('left_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header('left_n_1', _('Last'))
        self.grid.add_header('space', '')
        self.grid.add_header('right', _('Revenues'))
        self.grid.add_header('right_n', _('Value'))
        self.grid.add_header('right_b', _('Budget'))
        if self.lastfilter is not None:
            self.grid.add_header('right_n_1', _('Last'))

    def fill_filterheader(self):
        pass

    def fill_header(self):
        self.date_begin = self.getparam("begin_date")
        self.date_end = self.getparam("end_date")
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 3)
        self.add_component(img)
        if len(self.items) == 1:
            lbl = XferCompLabelForm('name')
            lbl.set_value(six.text_type(self.items[0]))
            lbl.set_location(1, 2, 4)
            lbl.description = self.model._meta.verbose_name
            self.add_component(lbl)

        self.filter = Q(costaccounting=self.item)
        if self.date_begin is not None:
            begin_filter = XferCompLabelForm('begin_date')
            begin_filter.set_location(1, 4)
            begin_filter.set_needed(True)
            begin_filter.set_value(get_value_converted(datetime.strptime(self.date_begin, "%Y-%m-%d").date()))
            begin_filter.description = _('begin')
            self.add_component(begin_filter)
            self.filter &= Q(entry__date_value__gte=self.date_begin)
        if self.date_end is not None:
            end_filter = XferCompLabelForm('end_date')
            end_filter.set_location(2, 4)
            end_filter.set_needed(True)
            end_filter.set_value(get_value_converted(datetime.strptime(self.date_end, "%Y-%m-%d").date()))
            end_filter.description = _('end')
            self.add_component(end_filter)
            self.filter &= Q(entry__date_value__lte=self.date_end)
        self.fill_filterCode()

    def fill_buttons(self):
        self.add_action(CostAccountingReportPrint.get_action(TITLE_PRINT, "images/print.png"),
                        close=CLOSE_NO, params={'classname': self.__class__.__name__})
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@ActionsManage.affect_grid(_("Report"), 'images/print.png', unique=SELECT_MULTI, modal=FORMTYPE_NOMODAL)
@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingIncomeStatement(CostAccountingReport, FiscalYearIncomeStatement):
    caption = _("Income statement of cost accounting")

    def fill_header(self):
        CostAccountingReport.fill_header(self)

    def fillresponse(self):
        self.fill_header()
        all_have_last = False
        tot_n, tot_b, tot_n1 = (0, 0, 0)
        res1, res2, resb = (0, 0, 0)
        self.addNameCol = True
        self.lastfilter = True
        self.item = self.items[len(self.items) - 1]
        self.define_gridheader()
        for self.item in self.items:
            add_cell_in_grid(self.grid, self.line_offset, 'name', '{[b]}{[u]}%s{[/u]}{[/b]}' % self.item)
            self.line_offset += 1
            self.filter = Q(costaccounting=self.item)
            if self.date_begin is not None:
                self.filter &= Q(entry__date_value__gte=self.date_begin)
            if self.date_end is not None:
                self.filter &= Q(entry__date_value__lte=self.date_end)
            self.fill_filterheader()
            all_have_last = all_have_last or (self.lastfilter is not None)
            self.calcul_table()
            total1_left, total2_left, totalb_left = self.total_summary_left
            if total1_left:
                tot_n += total1_left
            if totalb_left:
                tot_b += totalb_left
            if total2_left:
                tot_n1 += total2_left
            subres1, subres2, subresb = self.result
            res1 -= subres1
            res2 -= subres2
            resb -= subresb
            self.fill_body()
            self.line_offset = len(self.grid.records)
        if not all_have_last:
            self.grid.delete_header('left_n_1')
            self.grid.delete_header('right_n_1')
        if len(self.items) > 1:
            add_cell_in_grid(self.grid, self.line_offset + 1, 'left', get_spaces(5) + "{[i]}%s{[/i]}" % _('general result (profit)'))
            add_cell_in_grid(self.grid, self.line_offset + 1, 'right', get_spaces(5) + "{[i]}%s{[/i]}" % _('general result (deficit)'))
            if res1 < 0:
                add_cell_in_grid(self.grid, self.line_offset + 1, 'left_n', format_devise(-1 * res1, 5))
                tot_n -= res1
            else:
                add_cell_in_grid(self.grid, self.line_offset + 1, 'right_n', format_devise(res1, 5))
            if res2 < 0:
                add_cell_in_grid(self.grid, self.line_offset + 1, 'left_n_1', format_devise(-1 * res2, 5))
                tot_n1 -= res2
            else:
                add_cell_in_grid(self.grid, self.line_offset + 1, 'right_n_1', format_devise(res2, 5))
            if resb < 0:
                add_cell_in_grid(self.grid, self.line_offset + 1, 'left_b', format_devise(-1 * resb, 5))
                tot_b -= resb
            else:
                add_cell_in_grid(self.grid, self.line_offset + 1, 'right_b', format_devise(resb, 5))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'left', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('general total'))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'left_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(tot_n, 5))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'left_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(tot_b, 5))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'left_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(tot_n1, 5))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'right', get_spaces(10) + "{[u]}{[b]}%s{[/b]}{[/u]}" % _('general total'))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'right_n', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(tot_n, 5))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'right_b', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(tot_b, 5))
            add_cell_in_grid(self.grid, self.line_offset + 2, 'right_n_1', "{[u]}{[b]}%s{[/b]}{[/u]}" % format_devise(tot_n1, 5))
        else:
            self.grid.delete_header('name')
        self.fill_buttons()

    def fill_filterheader(self):
        if self.item.last_costaccounting is not None:
            self.lastfilter = Q(costaccounting=self.item.last_costaccounting)
        else:
            self.lastfilter = None

    def calcul_table(self):
        if (self.date_begin is not None) or (self.date_end is not None):
            self.budgetfilter_right = None
            self.budgetfilter_left = None
            self.lastfilter = None
            self.grid.delete_header('left_b')
            self.grid.delete_header('left_n_1')
            self.grid.delete_header('right_b')
            self.grid.delete_header('right_n_1')
        else:
            self.budgetfilter_right = Q(cost_accounting=self.item) & Q(code__regex=current_system_account().get_revenue_mask())
            self.budgetfilter_left = Q(cost_accounting=self.item) & Q(code__regex=current_system_account().get_expence_mask())
        line_idx = self._add_left_right_accounting(Q(account__type_of_account=4), Q(account__type_of_account=3), True)
        self.show_annexe(line_idx, Q(cost_accounting=self.item))


@ActionsManage.affect_grid(_("Ledger"), 'images/print.png', unique=SELECT_MULTI, modal=FORMTYPE_NOMODAL)
@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingLedger(CostAccountingReport, FiscalYearLedger):
    caption = _("Ledger of cost accounting")
    add_filtering = True

    def fill_header(self):
        CostAccountingReport.fill_header(self)

    def define_gridheader(self):
        FiscalYearLedger.define_gridheader(self)

    def calcul_table(self):
        FiscalYearLedger.calcul_table(self)

    def fill_filterCode(self):
        FiscalYearReport.fill_filterCode(self)


@ActionsManage.affect_grid(_("Trial balance"), 'images/print.png', unique=SELECT_MULTI, modal=FORMTYPE_NOMODAL)
@MenuManage.describ('accounting.change_entryaccount')
class CostAccountingTrialBalance(CostAccountingReport, FiscalYearTrialBalance):
    caption = _("Trial balance of cost accounting")
    add_filtering = True

    def fill_header(self):
        CostAccountingReport.fill_header(self)

    def define_gridheader(self):
        FiscalYearTrialBalance.define_gridheader(self)

    def calcul_table(self):
        FiscalYearTrialBalance.calcul_table(self)

    def fill_filterCode(self):
        FiscalYearReport.fill_filterCode(self)
        self.with_third = False
        self.only_nonull = False
