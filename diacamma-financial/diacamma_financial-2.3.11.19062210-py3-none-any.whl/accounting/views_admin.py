# -*- coding: utf-8 -*-
'''
Describe entries account viewer for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
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

from lucterios.framework.xferadvance import XferListEditor, XferDelete, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE
from lucterios.framework.xferadvance import XferAddEditor
from lucterios.framework.tools import FORMTYPE_MODAL, ActionsManage, MenuManage, SELECT_SINGLE, CLOSE_NO, SELECT_MULTI
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from lucterios.framework.xfercomponents import XferCompButton, XferCompLabelForm, XferCompSelect, XferCompImage, XferCompDownLoad
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import ParamEdit
from lucterios.CORE.models import Parameter

from diacamma.accounting.models import FiscalYear, Journal, AccountThird, ChartsAccount, ModelLineEntry,\
    Third
from diacamma.accounting.system import accounting_system_list, accounting_system_name
from diacamma.accounting.tools import clear_system_account, correct_accounting_code,\
    current_system_account
from django.utils import six
from lucterios.contacts.models import CustomField

MenuManage.add_sub("financial.conf", "core.extensions", "", _("Financial"), "", 2)


def select_account_system(xfer):
    current_account_system = Params.getvalue("accounting-system")
    if current_account_system == '':
        edt = XferCompSelect("account_system")
        account_systems = list(accounting_system_list().items())
        account_systems.insert(0, ('', '---'))
        edt.set_select(account_systems)
        edt.set_action(xfer.request, ConfigurationAccountingSystem.get_action(), modal=FORMTYPE_MODAL, close=CLOSE_NO)
    else:
        edt = XferCompLabelForm("account_system")
    edt.set_value(accounting_system_name(current_account_system))
    edt.set_location(1, xfer.get_max_row() + 1)
    edt.description = _('accounting system')
    xfer.add_component(edt)
    return edt


def fill_params(xfer, is_mini=False):
    xfer.params['params'] = ['accounting-devise', 'accounting-devise-iso', 'accounting-devise-prec']
    if current_system_account().has_minium_code_size():
        xfer.params['params'].append('accounting-sizecode')
    xfer.params['params'].append('accounting-needcost')
    xfer.params['params'].append('accounting-code-report-filter')
    Params.fill(xfer, xfer.params['params'], 1, xfer.get_max_row() + 1)
    btn = XferCompButton('editparam')
    btn.set_is_mini(is_mini)
    btn.set_location(1, xfer.get_max_row() + 1, 2, 1)
    btn.set_action(xfer.request, ParamEdit.get_action(TITLE_MODIFY, 'images/edit.png'), close=CLOSE_NO)
    xfer.add_component(btn)


def add_year_info(xfer, is_mini=False):
    try:
        row = xfer.get_max_row() + 1
        current_year = FiscalYear.get_current()
        nb_account = len(ChartsAccount.objects.filter(year=current_year))
        lbl = XferCompLabelForm('nb_account')
        if is_mini and (nb_account == 0):
            lbl.set_value(_("No charts of accounts in current fiscal year"))
        else:
            lbl.set_value(_("Total of charts of accounts in current fiscal year: %d") % nb_account)
        lbl.set_location(0, row, 4)
        xfer.add_component(lbl)
        if nb_account == 0:
            lbl.set_color('red')
            xfer.item = ChartsAccount()
            xfer.item.year = current_year
            btn2 = XferCompButton('accountfiscalyear')
            btn2.set_location(0, row + 1)
            btn2.set_action(xfer.request, ActionsManage.get_action_url(ChartsAccount.get_long_name(), 'AccountList', xfer), close=CLOSE_NO)
            xfer.add_component(btn2)
            if not is_mini:
                btn1 = XferCompButton('initialfiscalyear')
                btn1.set_location(1, row + 1, 3)
                btn1.set_action(xfer.request, ActionsManage.get_action_url(ChartsAccount.get_long_name(), 'AccountInitial', xfer), close=CLOSE_NO)
                xfer.add_component(btn1)
    except LucteriosException as lerr:
        lbl = XferCompLabelForm('nb_account')
        lbl.set_value(six.text_type(lerr))
        lbl.set_location(0, row, 4)
        xfer.add_component(lbl)


@ActionsManage.affect_other(_("Accounting configuration"), "images/edit.png")
@MenuManage.describ('accounting.change_fiscalyear', FORMTYPE_MODAL, 'financial.conf', _('Management of fiscal year and financial parameters'))
class Configuration(XferListEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Accounting configuration")

    def fillresponse_header(self):
        self.params['basic_model'] = 'accounting.Third'
        self.new_tab(_('Fiscal year list'))
        select_account_system(self)

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        add_year_info(self)
        self.new_tab(_('Journals'))
        self.fill_grid(self.get_max_row() + 1, Journal, 'journal', Journal.objects.all())
        self.new_tab(_('Parameters'))
        fill_params(self)
        self.new_tab(_("Third Custom field"))
        self.fill_grid(0, CustomField, "custom_field", CustomField.get_filter(Third))
        grid_custom = self.get_components('custom_field')
        grid_custom.delete_header('model_title')


@MenuManage.describ('accounting.add_fiscalyear')
class ConfigurationAccountingSystem(XferContainerAcknowledge):

    def fillresponse(self, account_system=''):
        if account_system != '':
            if self.confirme(_('Do you confirm to select "%s" like accounting system?{[br/]}{[br/]}{[i]}{[u]}Warning{[/u]}: This choose is definitive.{[/i]}') %
                             accounting_system_name(account_system)):
                Parameter.change_value('accounting-system', account_system)
                Params.clear()
                clear_system_account()
                signal_and_lock.Signal.call_signal("param_change", ('accounting-system'))


@ActionsManage.affect_grid(_("Activate"), "images/ok.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearActive(XferContainerAcknowledge):
    icon = "images/ok.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Activate")

    def fillresponse(self):
        self.item.set_has_actif()


@ActionsManage.affect_grid(_("Export"), "diacamma.accounting/images/entry.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.change_fiscalyear')
class FiscalYearExport(XferContainerCustom):
    icon = "entry.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Export")

    def fillresponse(self):
        if self.item.id is None:
            self.item = FiscalYear.get_current()
        destination_file = self.item.get_xml_export()
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        lbl = XferCompLabelForm('title')
        lbl.set_value_as_title(_('Export fiscal year'))
        lbl.set_location(1, 0)
        self.add_component(lbl)
        down = XferCompDownLoad('filename')
        down.compress = False
        down.set_value('export_year_%s_%s.xml' %
                       (self.item.begin.isoformat(), self.item.end.isoformat()))
        down.set_download(destination_file)
        down.set_location(1, 1)
        self.add_component(down)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_fiscalyear')
class FiscalYearAddModify(XferAddEditor):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption_add = _("Add fiscal year")
    caption_modify = _("Modify fiscal year")

    def fillresponse(self):
        if self.item.id is None:
            if Params.getvalue("accounting-system") == '':
                raise LucteriosException(IMPORTANT, _('Account system not defined!'))
            self.item.init_dates()
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.delete_fiscalyear')
class FiscalYearDel(XferDelete):
    icon = "accountingYear.png"
    model = FiscalYear
    field_id = 'fiscalyear'
    caption = _("Delete fiscal year")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_fiscalyear')
class JournalAddModify(XferAddEditor):
    icon = "entry.png"
    model = Journal
    field_id = 'journal'
    caption_add = _("Add accounting journal")
    caption_modify = _("Modify accounting journal")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('accounting.delete_fiscalyear')
class JournalDel(XferDelete):
    icon = "entry.png"
    model = Journal
    field_id = 'journal'
    caption = _("Delete accounting journal")


@signal_and_lock.Signal.decorate('param_change')
def paramchange_accounting(params):
    if 'accounting-sizecode' in params:
        for account in AccountThird.objects.all():
            if account.code != correct_accounting_code(account.code):
                account.code = correct_accounting_code(account.code)
                account.save()
        for charts_account in ChartsAccount.objects.filter(year__status__in=(0, 1)).distinct():
            if charts_account.code != correct_accounting_code(charts_account.code):
                charts_account.code = correct_accounting_code(charts_account.code)
                charts_account.save()
        for model_line in ModelLineEntry.objects.all():
            if model_line.code != correct_accounting_code(model_line.code):
                model_line.code = correct_accounting_code(model_line.code)
                model_line.save()


@signal_and_lock.Signal.decorate('conf_wizard')
def conf_wizard_accounting(wizard_ident, xfer):
    if isinstance(wizard_ident, list) and (xfer is None):
        wizard_ident.append(("accounting_params", 9))
        wizard_ident.append(("accounting_fiscalyear", 9))
        wizard_ident.append(("accounting_journal", 23))
    elif (xfer is not None) and (wizard_ident == "accounting_params"):
        xfer.add_title(_("Diacamma accounting"), _('Parameters'), _('Configuration of accounting parameters'))
        select_account_system(xfer)
        fill_params(xfer, True)
    elif (xfer is not None) and (wizard_ident == "accounting_fiscalyear"):
        xfer.add_title(_("Diacamma accounting"), _('Fiscal year list'), _('Configuration of fiscal years'))
        xfer.fill_grid(5, FiscalYear, 'fiscalyear', FiscalYear.objects.all())
        add_year_info(xfer)
    elif (xfer is not None) and (wizard_ident == "accounting_journal"):
        xfer.add_title(_("Diacamma accounting"), _('Journals'), _('Configuration of journals'))
        xfer.fill_grid(5, Journal, 'journal', Journal.objects.all())
