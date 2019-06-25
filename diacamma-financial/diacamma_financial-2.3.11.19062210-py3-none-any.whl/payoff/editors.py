# -*- coding: utf-8 -*-
'''
diacamma.payoff editors package

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
from django.utils import six

from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompButton, \
    XferCompEdit, XferCompMemo, XferCompSelect, XferCompCheck, XferCompLinkLabel
from lucterios.CORE.parameters import Params
from lucterios.framework.tools import ActionsManage, CLOSE_NO, FORMTYPE_REFRESH, FORMTYPE_MODAL, WrapAction
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.contacts.models import LegalEntity

from diacamma.payoff.models import Supporting
from diacamma.accounting.models import FiscalYear
from diacamma.accounting.tools import current_system_account


class SupportingEditor(LucteriosEditor):

    def show_third(self, xfer, right=''):
        xfer.params['supporting'] = self.item.id
        third = xfer.get_components('third')
        third.colspan -= 1
        if (self.item.third_id is not None) and (self.item.third.contact.email != ''):
            xfer.remove_component('third')
            new_third = XferCompLinkLabel('third')
            new_third.set_value(six.text_type(self.item.third))
            new_third.tab = third.tab
            new_third.col = third.col
            new_third.row = third.row
            new_third.colspan = third.colspan
            new_third.rowspan = third.rowspan
            new_third.description = third.description
            new_third.set_link('mailto:' + self.item.third.contact.email)
            xfer.add_component(new_third)
            third = new_third
        if WrapAction.is_permission(xfer.request, right):
            btn = XferCompButton('change_third')
            btn.set_is_mini(True)
            btn.set_location(third.col + third.colspan, third.row)
            btn.set_action(xfer.request, ActionsManage.get_action_url('payoff.Supporting', 'Third', xfer),
                           modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'code_mask': self.item.get_third_mask()})
            xfer.add_component(btn)

        if self.item.third is not None:
            btn = XferCompButton('show_third')
            btn.set_is_mini(True)
            btn.set_location(third.col + third.colspan + 1, third.row)
            btn.set_action(xfer.request, ActionsManage.get_action_url('accounting.Third', 'Show', xfer),
                           modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'third': self.item.third.id})
            xfer.add_component(btn)
        lbl = XferCompLabelForm('info')
        lbl.set_color('red')
        lbl.set_location(1, xfer.get_max_row() + 1, 4)
        lbl.set_value(self.item.get_info_state())
        xfer.add_component(lbl)

    def show_third_ex(self, xfer):
        xfer.params['supporting'] = self.item.id
        third = xfer.get_components('third')
        third.colspan -= 1
        if (self.item.third_id is not None) and (self.item.third.contact.email != ''):
            xfer.remove_component('third')
            new_third = XferCompLinkLabel('third')
            new_third.set_value(six.text_type(self.item.third))
            new_third.tab = third.tab
            new_third.col = third.col
            new_third.row = third.row
            new_third.colspan = third.colspan
            new_third.rowspan = third.rowspan
            new_third.description = third.description
            new_third.set_link('mailto:' + self.item.third.contact.email)
            xfer.add_component(new_third)
            third = new_third
        if self.item.third is not None:
            btn = XferCompButton('show_third')
            btn.set_is_mini(True)
            btn.set_location(third.col + third.colspan, third.row)
            btn.set_action(xfer.request, ActionsManage.get_action_url('accounting.Third', 'Show', xfer),
                           modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'third': self.item.third.id})
            xfer.add_component(btn)

    def show(self, xfer):
        xfer.params['supporting'] = self.item.id
        xfer.filltab_from_model(1, xfer.get_max_row() + 1, True, self.item.get_payoff_fields())
        payoff = xfer.get_components("payoff")
        if not self.item.is_revenu:
            payoff.delete_header('payer')


class BankAccountEditor(LucteriosEditor):

    def edit(self, xfer):
        old_account = xfer.get_components("account_code")
        xfer.remove_component("account_code")
        sel_code = XferCompSelect("account_code")
        sel_code.description = old_account.description
        sel_code.set_location(old_account.col, old_account.row, old_account.colspan + 1, old_account.rowspan)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_cash_mask()).order_by('code'):
            sel_code.select_list.append((item.code, six.text_type(item)))
        sel_code.set_value(self.item.account_code)
        xfer.add_component(sel_code)


class PayoffEditor(LucteriosEditor):

    def before_save(self, xfer):
        if abs(float(self.item.amount)) < 0.0001:
            raise LucteriosException(IMPORTANT, _("payoff null!"))
        info = self.item.supporting.check_date(self.item.date)
        if len(info) > 0:
            raise LucteriosException(IMPORTANT, info[0])
        return

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        fee_code = Params.getvalue("payoff-bankcharges-account")
        supportings = xfer.getparam('supportings', ())
        if len(supportings) > 0:
            supporting_list = Supporting.objects.filter(id__in=supportings, is_revenu=True).distinct()
            if len(supporting_list) == 0:
                supporting_list = Supporting.objects.filter(id__in=supportings, is_revenu=False).distinct()
            if len(supporting_list) == 0:
                raise LucteriosException(IMPORTANT, _('No-valid selection!'))
        else:
            supporting_list = [self.item.supporting]
        amount_max = 0
        amount_min = 0
        amount_sum = xfer.getparam('amount', 0.0)
        title = []
        if self.item.id is None:
            current_payoff = -1
        else:
            current_payoff = self.item.id
        for supporting in supporting_list:
            up_supporting = supporting.get_final_child()
            title.append(six.text_type(up_supporting))
            if xfer.getparam('amount') is None:
                amount_sum += up_supporting.get_total_rest_topay()
            amount_min += up_supporting.get_min_payoff(current_payoff)
            amount_max += up_supporting.get_max_payoff(current_payoff)
        xfer.move(0, 0, 1)
        lbl = XferCompLabelForm('supportings')
        lbl.set_value_center("{[br/]}".join(title))
        lbl.set_location(1, 0, 2)
        xfer.add_component(lbl)
        if len(supportings) > 0:
            row = xfer.get_max_row() + 1
            sel = XferCompSelect('repartition')
            sel.set_value(xfer.getparam('repartition', 0))
            sel.set_select([(0, _('by ratio')), (1, _('by date'))])
            sel.set_location(1, row)
            sel.description = _('repartition mode')
            xfer.add_component(sel)
            if xfer.getparam('NO_REPARTITION') is not None:
                xfer.change_to_readonly('repartition')
        amount = xfer.get_components("amount")
        if self.item.id is None:
            amount.value = min(max(amount_min, amount_sum), amount_max)
            xfer.get_components("payer").value = six.text_type(supporting_list[0].third)
            if xfer.getparam('date') is None:
                xfer.get_components("date").value = supporting_list[0].get_final_child().default_date()
        elif xfer.getparam('amount') is not None:
            amount.value = amount_sum
        amount.prec = currency_decimal
        amount.min = float(amount_min)
        amount.max = float(amount_max)
        mode = xfer.get_components("mode")
        banks = xfer.get_components("bank_account")
        if banks.select_list[0][0] == 0:
            del banks.select_list[0]
        if len(banks.select_list) == 0:
            mode.select_list = [mode.select_list[0]]
        else:
            # change order of payoff mode
            levy = mode.select_list[5]
            mode.select_list.insert(3, levy)
            del mode.select_list[6]
            xfer.get_components("mode").set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        if self.item.mode == 0:
            xfer.remove_component("bank_account")
        else:
            banks = xfer.get_components("bank_account")
            if banks.select_list[0][0] == 0:
                del banks.select_list[0]
            if len(banks.select_list) == 0:
                xfer.remove_component("bank_account")
        if not supporting_list[0].is_revenu:
            xfer.remove_component("payer")
        if (fee_code == '') or (self.item.mode == 0):
            xfer.remove_component("bank_fee")
        else:
            bank_fee = xfer.get_components("bank_fee")
            bank_fee.prec = currency_decimal
            bank_fee.min = 0.0
            bank_fee.max = float(amount_max)


class DepositSlipEditor(LucteriosEditor):

    def show(self, xfer):
        xfer.move(0, 0, 5)
        xfer.item = LegalEntity.objects.get(id=1)
        xfer.fill_from_model(1, 0, True, ["name", 'address', ('postal_code', 'city'), ('tel1', 'email')])
        xfer.item = self.item
        lbl = XferCompLabelForm('sep')
        lbl.set_value_center("{[hr/]}")
        lbl.set_location(1, 4, 4)
        xfer.add_component(lbl)
        depositdetail = xfer.get_components("depositdetail")
        depositdetail.col = 1
        depositdetail.colspan = 2
        depositdetail.description = ''


class PaymentMethodEditor(LucteriosEditor):

    def before_save(self, xfer):
        values = []
        for fieldid, _fieldtitle, _fieldtype in self.item.get_extra_fields():
            values.append(xfer.getparam('item_%d' % fieldid, ''))
        self.item.set_items(values)

    def edit(self, xfer):
        if xfer.item.id is None:
            xfer.get_components("paytype").set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        else:
            xfer.change_to_readonly('paytype')
        items = self.item.get_items()
        for fieldid, fieldtitle, fieldtype in self.item.get_extra_fields():
            row = xfer.get_max_row() + 1
            if fieldtype == 0:
                edt = XferCompEdit('item_%d' % fieldid)
            elif fieldtype == 1:
                edt = XferCompMemo('item_%d' % fieldid)
            elif fieldtype == 2:
                edt = XferCompCheck('item_%d' % fieldid)
            edt.set_value(items[fieldid - 1])
            edt.set_location(1, row)
            edt.description = fieldtitle
            xfer.add_component(edt)
