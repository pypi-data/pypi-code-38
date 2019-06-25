# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.utils.translation import ugettext_lazy as _
from django.db.models import Q

from lucterios.framework.xferadvance import XferListEditor, XferDelete,\
    TITLE_MODIFY, TITLE_ADD, TITLE_DELETE
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage,\
    CLOSE_NO, SELECT_SINGLE, SELECT_MULTI, FORMTYPE_REFRESH
from lucterios.framework.xfercomponents import XferCompButton, XferCompCheck
from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.models import Parameter

from diacamma.accounting.tools import correct_accounting_code
from diacamma.payoff.models import BankAccount, PaymentMethod
from diacamma.accounting.system import accounting_system_ident


def fill_params(xfer, is_mini=False):
    param_lists = ['payoff-cash-account', 'payoff-bankcharges-account', 'payoff-email-subject', 'payoff-email-message']
    Params.fill(xfer, param_lists, 1, xfer.get_max_row() + 1)
    btn = XferCompButton('editparam')
    btn.set_is_mini(is_mini)
    btn.set_location(1, xfer.get_max_row() + 1, 2, 1)
    btn.set_action(xfer.request, ParamEdit.get_action(TITLE_MODIFY, 'images/edit.png'), close=CLOSE_NO, params={'params': param_lists})
    xfer.add_component(btn)


@MenuManage.describ('payoff.change_bankaccount', FORMTYPE_NOMODAL, 'financial.conf', _('Management of parameters and configuration of payoff'))
class PayoffConf(XferListEditor):
    icon = "bank.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption = _("Payoff configuration")

    def fillresponse_header(self):
        self.new_tab(_('Bank account'))
        show_only_enabled_bank = self.getparam('show_only_enabled_bank', True)
        if show_only_enabled_bank is True:
            self.filter = Q(is_disabled=False)

    def fillresponse(self, show_only_enabled_bank=True):
        XferListEditor.fillresponse(self)
        check = XferCompCheck('show_only_enabled_bank')
        check.set_location(0, 2)
        check.set_value(show_only_enabled_bank)
        check.description = _('show only enabled bank account')
        check.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(check)

        self.new_tab(_('Payment method'))
        self.fill_grid(0, PaymentMethod, "paymentmethod", PaymentMethod.objects.all())
        self.new_tab(_('Parameters'))
        fill_params(self)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('payoff.add_bankaccount')
class BankAccountAddModify(XferAddEditor):
    icon = "bank.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption_add = _("Add bank account")
    caption_modify = _("Modify bank account")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('payoff.delete_bankaccount')
class BankAccountDelete(XferDelete):
    icon = "bank.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption = _("Delete bank account")


@ActionsManage.affect_grid(_('Up'), "images/up.png", unique=SELECT_SINGLE)
@MenuManage.describ('payoff.add_bankaccount')
class BankAccountUp(XferContainerAcknowledge):
    icon = "up.png"
    model = BankAccount
    field_id = 'bankaccount'
    caption = _("Up bank account")

    def fillresponse(self):
        self.item.up_order()


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('payoff.add_bankaccount')
class PaymentMethodAddModify(XferAddEditor):
    icon = "bank.png"
    model = PaymentMethod
    field_id = 'paymentmethod'
    caption_add = _("Add payment method")
    caption_modify = _("Modify payment method")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('payoff.delete_bankaccount')
class PaymentMethodDelete(XferDelete):
    icon = "bank.png"
    model = PaymentMethod
    field_id = 'paymentmethod'
    caption = _("Delete payment method")


@signal_and_lock.Signal.decorate('compte_no_found')
def comptenofound_payoff(known_codes, accompt_returned):
    bank_unknown = BankAccount.objects.exclude(account_code__in=known_codes).values_list('account_code', flat=True)
    param_unknown = Parameter.objects.filter(name__in=('payoff-cash-account', 'payoff-bankcharges-account')).exclude(value__in=known_codes).values_list('value', flat=True)
    comptenofound = ""
    if (len(bank_unknown) > 0):
        comptenofound = _("bank account") + ":" + ",".join(set(bank_unknown)) + " "
    if (len(param_unknown) > 0):
        comptenofound += _("parameters") + ":" + ",".join(set(param_unknown))
    if comptenofound != "":
        accompt_returned.append(
            "- {[i]}{[u]}%s{[/u]}: %s{[/i]}" % (_('Payoff'), comptenofound))
    return True


@signal_and_lock.Signal.decorate('param_change')
def paramchange_payoff(params):
    if 'accounting-sizecode' in params:
        for bank in BankAccount.objects.all():
            if bank.account_code != correct_accounting_code(bank.account_code):
                bank.account_code = correct_accounting_code(bank.account_code)
                bank.save()
    if ('payoff-cash-account' in params) or ('accounting-sizecode' in params):
        Parameter.change_value(
            'payoff-cash-account', correct_accounting_code(Params.getvalue('payoff-cash-account')))
    if ('payoff-bankcharges-account' in params) or ('accounting-sizecode' in params):
        pvalue = Params.getvalue('payoff-bankcharges-account')
        if pvalue != '':
            Parameter.change_value(
                'payoff-bankcharges-account', correct_accounting_code(pvalue))
    if 'accounting-system' in params:
        system_ident = accounting_system_ident(Params.getvalue("accounting-system"))
        if system_ident == "french":
            Parameter.change_value('payoff-cash-account', correct_accounting_code('531'))
        elif system_ident == "belgium":
            Parameter.change_value('payoff-cash-account', correct_accounting_code('570000'))
    Params.clear()


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_payoff(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("payoff_params", 31))
        wizard_ident.append(("payoff_bank", 32))
        wizard_ident.append(("payoff_payment", 33))
    elif (xfer is not None) and (wizard_ident == "payoff_params"):
        xfer.add_title(_("Diacamma payoff"), _('Parameters'), _('Configuration of payoff parameters'))
        fill_params(xfer, True)
    elif (xfer is not None) and (wizard_ident == "payoff_bank"):
        xfer.add_title(_("Diacamma payoff"), _('Bank account'), _('Configuration of bank account'))
        xfer.fill_grid(5, BankAccount, 'bankaccount', BankAccount.objects.all())
    elif (xfer is not None) and (wizard_ident == "payoff_payment"):
        xfer.add_title(_("Diacamma payoff"), _('Payment method'), _('Configuration of payment method'))
        xfer.fill_grid(5, PaymentMethod, 'paymentmethod', PaymentMethod.objects.all())
