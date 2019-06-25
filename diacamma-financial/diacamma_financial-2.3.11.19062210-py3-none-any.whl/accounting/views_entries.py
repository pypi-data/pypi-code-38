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
from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.utils import formats, six
from django.db.models import Q, F
from django.db.models.expressions import Case, When, ExpressionWrapper
from django.db.models.fields import DecimalField
from django.db.models.aggregates import Count

from lucterios.framework.xferadvance import XferShowEditor, XferDelete, XferSave, TITLE_LISTING, TITLE_DELETE, TITLE_OK, TITLE_CANCEL, TITLE_CLOSE, TITLE_MODIFY,\
    TITLE_EDIT, TITLE_ADD
from lucterios.framework.tools import FORMTYPE_NOMODAL, CLOSE_NO, FORMTYPE_REFRESH, SELECT_SINGLE, SELECT_MULTI, SELECT_NONE, CLOSE_YES
from lucterios.framework.tools import ActionsManage, MenuManage, WrapAction
from lucterios.framework.xferadvance import action_list_sorted
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from lucterios.framework.xfercomponents import XferCompSelect, XferCompLabelForm, XferCompImage, XferCompFloat
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.CORE.xferprint import XferPrintListing
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor
from lucterios.CORE.parameters import Params

from diacamma.accounting.models import EntryLineAccount, EntryAccount, FiscalYear, Journal, AccountLink, current_system_account, CostAccounting, ModelEntry


@MenuManage.describ('accounting.change_entryaccount', FORMTYPE_NOMODAL, 'bookkeeping', _('Edition of accounting entry for current fiscal year'),)
class EntryAccountList(XferListEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = '???'
    caption = _("accounting entries")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.select_filter = 1

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        items = items.annotate(num_link=Count('entry__entrylineaccount__link'))
        items = items.annotate(cdway=Case(When(account__type_of_account__in=(0, 4), then=-1), default=1, output_field=DecimalField()))
        items = items.annotate(credit_num=ExpressionWrapper(F('amount') * F('cdway'), output_field=DecimalField()), debit_num=ExpressionWrapper(-1 * F('amount') * F('cdway'), output_field=DecimalField()))
        if self.select_filter == 3:
            items = items.filter(Q(num_link__gt=0)).distinct()
        elif self.select_filter == 4:
            items = items.filter(Q(num_link=0)).distinct()
        return items

    def _filter_by_year(self):
        select_year = self.getparam('year')
        self.item.year = FiscalYear.get_current(select_year)
        self.item.journal = Journal.objects.get(id=1)
        self.fill_from_model(0, 1, False, ['year', 'journal'])
        self.get_components('year').set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.get_components('year').colspan = 2
        self.filter = Q(entry__year=self.item.year)

    def _filter_by_journal(self):
        select_journal = self.getparam('journal', 4)
        journal = self.get_components('journal')
        journal.select_list.append((-1, '---'))
        journal.set_value(select_journal)
        journal.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        journal.colspan = 2
        if select_journal != -1:
            self.filter &= Q(entry__journal__id=select_journal)

    def _filter_by_nature(self):
        self.select_filter = self.getparam('filter', 1)
        sel = XferCompSelect("filter")
        sel.set_select({0: _('All'), 1: _('In progress'), 2: _('Valid'), 3: _('Lettered'), 4: _('Not lettered')})
        sel.set_value(self.select_filter)
        sel.set_location(0, 3, 2)
        sel.description = _("Filter")
        sel.set_size(20, 200)
        sel.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(sel)
        if self.select_filter == 1:
            self.filter &= Q(entry__close=False)
        elif self.select_filter == 2:
            self.filter &= Q(entry__close=True)

    def fillresponse_header(self):
        self._filter_by_year()
        self._filter_by_journal()
        self._filter_by_nature()

    def fillresponse_body(self):
        lineorder = self.getparam('GRID_ORDER%entryline', ())
        self.params['GRID_ORDER%entryline'] = ','.join([item.replace('entry_account', 'account__code').replace('designation_ref', 'entry__designation').replace('debit', 'debit_num').replace('credit', 'credit_num') for item in lineorder])
        self.model = EntryLineAccount
        self.field_id = 'entryline'
        XferListEditor.fillresponse_body(self)
        grid = self.get_components('entryline')
        grid.get_header('entry_account').orderable = 1
        grid.get_header('designation_ref').orderable = 1
        grid.get_header('debit').orderable = 1
        grid.get_header('credit').orderable = 1
        grid.actions = []
        grid.add_action_notified(self, model=EntryAccount)
        grid.order_list = lineorder
        self.params['GRID_ORDER%entryline'] = ','.join(lineorder)
        self.model = EntryAccount

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        lbl = XferCompLabelForm("result")
        lbl.set_value_center(self.item.year.total_result_text)
        lbl.set_location(0, 10, 2)
        self.add_component(lbl)


@ActionsManage.affect_list(_("Search"), "diacamma.accounting/images/entry.png", modal=FORMTYPE_NOMODAL, close=CLOSE_YES, condition=lambda xfer: xfer.url_text.endswith('AccountList'))
@MenuManage.describ('accounting.change_entryaccount')
class EntryAccountSearch(XferSavedCriteriaSearchEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = '???'
    caption = _("Search accounting entry")

    def __init__(self):
        self.model = EntryLineAccount
        self.field_id = 'entryline'
        XferSavedCriteriaSearchEditor.__init__(self)

    def filter_items(self):
        XferSavedCriteriaSearchEditor.filter_items(self)
        self.items = self.items.annotate(cdway=Case(When(account__type_of_account__in=(0, 4), then=-1), default=1, output_field=DecimalField()))
        self.items = self.items.annotate(credit_num=ExpressionWrapper(F('amount') * F('cdway'), output_field=DecimalField()), debit_num=ExpressionWrapper(-1 * F('amount') * F('cdway'), output_field=DecimalField()))

    def fillresponse(self):
        lineorder = self.getparam('GRID_ORDER%entryline', ())
        self.params['GRID_ORDER%entryline'] = ','.join([item.replace('entry_account', 'account__code').replace('designation_ref', 'entry__designation').replace('debit', 'debit_num').replace('credit', 'credit_num') for item in lineorder])
        XferSavedCriteriaSearchEditor.fillresponse(self)
        grid = self.get_components('entryline')
        grid.get_header('entry_account').orderable = 1
        grid.get_header('designation_ref').orderable = 1
        grid.get_header('debit').orderable = 1
        grid.get_header('credit').orderable = 1
        grid.actions = []
        self.item = EntryAccount()
        self.item.year = FiscalYear()
        self.model = EntryAccount
        grid.add_action_notified(self, model=EntryAccount)
        grid.order_list = lineorder
        self.params['GRID_ORDER%entryline'] = ','.join(lineorder)
        self.actions = []
        for act, opt in ActionsManage.get_actions(ActionsManage.ACTION_IDENT_LIST, self, key=action_list_sorted):
            self.add_action(act, **opt)
        self.add_action(WrapAction(_('Close'), 'images/close.png'))


@ActionsManage.affect_list(TITLE_LISTING, "images/print.png")
@MenuManage.describ('accounting.change_entryaccount')
class EntryAccountListing(XferPrintListing):
    icon = "entry.png"
    model = EntryAccount
    field_id = '???'
    caption = _("Listing accounting entry")

    def __init__(self):
        self.model = EntryLineAccount
        self.field_id = 'entrylineaccount'
        XferPrintListing.__init__(self)
        self.select_filter = 1

    def get_filter(self):
        if self.getparam('CRITERIA') is None:
            select_year = self.getparam('year')
            select_journal = self.getparam('journal', 4)
            self.select_filter = self.getparam('filter', 1)
            new_filter = Q(entry__year=FiscalYear.get_current(select_year))
            if self.select_filter == 1:
                new_filter &= Q(entry__close=False)
            elif self.select_filter == 2:
                new_filter &= Q(entry__close=True)
            if select_journal != -1:
                new_filter &= Q(entry__journal__id=select_journal)
        else:
            new_filter = XferPrintListing.get_filter(self)
        return new_filter

    def filter_callback(self, items):
        items = items.annotate(num_link=Count('entry__entrylineaccount__link'))
        if self.select_filter == 3:
            items = items.filter(Q(num_link__gt=0)).distinct()
        elif self.select_filter == 4:
            items = items.filter(Q(num_link=0)).distinct()
        return items

    def fillresponse(self):
        self.caption = _("Listing accounting entry") + " - " + formats.date_format(date.today(), "DATE_FORMAT")
        if self.getparam('CRITERIA') is None:
            info_list = []
            select_year = self.getparam('year')
            info_list.append("{[b]}{[u]}%s{[/u]}{[/b]} : %s" % (_('fiscal year'), six.text_type(FiscalYear.get_current(select_year))))
            select_journal = self.getparam('journal', 4)
            if select_journal >= 0:
                info_list.append("{[b]}{[u]}%s{[/u]}{[/b]} : %s" % (_('journal'), six.text_type(Journal.objects.get(id=select_journal))))
            select_filter = self.getparam('filter', 1)
            select_filter_list = {0: _('All'), 1: _('In progress'), 2: _('Valid'), 3: _('Lettered'), 4: _('Not lettered')}
            info_list.append("{[b]}{[u]}%s{[/u]}{[/b]} : %s" % (_("Filter"), select_filter_list[select_filter]))
            self.info = '{[br]}'.join(info_list)
        XferPrintListing.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, 'images/delete.png', unique=SELECT_MULTI, condition=lambda xfer, gridname='': (xfer.item.year.status in [0, 1]) and (xfer.getparam('filter', 0) != 2))
@MenuManage.describ('accounting.delete_entryaccount')
class EntryAccountDel(XferDelete):
    icon = "entry.png"
    model = EntryAccount
    field_id = '???'
    caption = _("Delete accounting entry")

    def _search_model(self):
        if self.getparam('entryline') is not None:
            entryline = self.getparam('entryline', ())
            self.items = EntryAccount.objects.filter(entrylineaccount__id__in=entryline).distinct()
        else:
            XferDelete._search_model(self)


@ActionsManage.affect_grid(_("Closed"), "images/ok.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': not hasattr(xfer.item, 'year') or ((xfer.item.year.status in [0, 1]) and (xfer.getparam('filter', 0) != 2)))
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountClose(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Close accounting entry")

    def _search_model(self):
        if (self.getparam('entryline') is not None) and (self.getparam('entryaccount') is None):
            entryline = self.getparam('entryline', ())
            self.items = EntryAccount.objects.filter(entrylineaccount__id__in=entryline).distinct()
        else:
            XferContainerAcknowledge._search_model(self)

    def fillresponse(self):
        if (len(self.items) > 0) and self.confirme(_("Do you want to close this entry?")):
            for item in self.items:
                item.closed()
        if (len(self.items) == 1) and (self.getparam('REOPEN') == 'YES'):
            if 'entryline' in self.params.keys():
                del self.params['entryline']
            self.params['entryaccount'] = self.items[0].id
            self.redirect_action(EntryAccountOpenFromLine.get_action())


@ActionsManage.affect_grid(_("Link/Unlink"), "images/left.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': not hasattr(xfer.item, 'year') or (xfer.item.year.status in [0, 1]))
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountLink(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = '???'
    caption = _("Delete accounting entry")

    def _search_model(self):
        if self.getparam('entryline') is not None:
            entryline = self.getparam('entryline', ())
            self.model = EntryLineAccount
            self.items = EntryLineAccount.objects.filter(Q(id__in=entryline)).distinct()
            if len(self.items) > 0:
                self.item = self.items[0]
        else:
            XferContainerAcknowledge._search_model(self)

    def fillresponse(self):
        if self.items is None:
            raise Exception('no link')
        if len(self.items) == 1:
            if self.items[0].entry.year.status == 2:
                raise LucteriosException(IMPORTANT, _("Fiscal year finished!"))
            if self.confirme(_('Do you want unlink this entry?')):
                self.items[0].unlink()
        else:
            AccountLink.create_link(self.items)


@ActionsManage.affect_grid(_("Cost"), "images/edit.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': len(CostAccounting.objects.filter(status=0)) > 0)
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountCostAccounting(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    readonly = True
    field_id = '???'
    caption = _("cost accounting for entry")

    def _search_model(self):
        if (self.getparam('entryline') is not None) or (self.getparam('entrylineaccount') is not None):
            entryline = self.getparam('entryline', self.getparam('entrylineaccount', ()))
            self.model = EntryLineAccount
            self.items = EntryLineAccount.objects.filter(Q(id__in=entryline) & Q(account__type_of_account__in=(3, 4, 5)) & (Q(costaccounting__isnull=True) | Q(costaccounting__status=0))).distinct()
            if len(self.items) > 0:
                self.item = self.items[0]
        else:
            XferContainerAcknowledge._search_model(self)

    def fillresponse(self, cost_accounting_id=0):
        if len(self.items) == 0:
            raise LucteriosException(IMPORTANT, _('No entry line selected is availabled to change cost accounting !'))
        current_year = self.item.entry.year
        if self.getparam("SAVE") is None:
            dlg = self.create_custom()
            icon = XferCompImage('img')
            icon.set_location(0, 0, 1, 6)
            icon.set_value(self.icon_path())
            dlg.add_component(icon)
            lbl = XferCompLabelForm('lb_costaccounting')
            lbl.set_value_as_name(_('cost accounting'))
            lbl.set_location(1, 1)
            dlg.add_component(lbl)
            sel = XferCompSelect('cost_accounting_id')
            sel.set_needed(Params.getvalue('accounting-needcost'))
            sel.set_select_query(CostAccounting.objects.filter(Q(status=0) & (Q(year=None) | Q(year=current_year))).distinct())
            if self.item is not None:
                sel.set_value(self.item.costaccounting_id)
            sel.set_location(1, 2)
            dlg.add_component(sel)
            dlg.add_action(self.get_action(_('Ok'), 'images/ok.png'), params={"SAVE": "YES"})
            dlg.add_action(WrapAction(_('Cancel'), 'images/cancel.png'))
        else:
            if cost_accounting_id == 0:
                new_cost = None
            else:
                new_cost = CostAccounting.objects.get(id=cost_accounting_id)
            if (new_cost is None) or (new_cost.year is None) or (new_cost.year == current_year):
                for item in self.items:
                    if (item.costaccounting is None) or (item.costaccounting.status == 0):
                        item.costaccounting = new_cost
                        item.save()


@ActionsManage.affect_grid(TITLE_EDIT, 'images/edit.png', unique=SELECT_SINGLE)
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountOpenFromLine(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("accounting entries")

    def _search_model(self):
        if self.getparam('entryline') is not None:
            entryline = self.getparam('entryline', 0)
            self.item = EntryAccount.objects.get(entrylineaccount__id=entryline)
            self.params['entryaccount'] = self.item.id
        else:
            XferContainerAcknowledge._search_model(self)

    def fillresponse(self, field_id='', entryline=0):
        if field_id != '':
            self.item = EntryAccount.objects.get(id=self.getparam(field_id, 0))
            self.params['entryaccount'] = self.item.id
        for old_key in ["SAVE", 'entrylineaccount', 'entrylineaccount_link', 'third', 'reference', 'serial_entry', 'costaccounting']:
            if old_key in self.params.keys():
                del self.params[old_key]
        if self.item.close:
            self.redirect_action(EntryAccountShow.get_action())
        else:
            self.redirect_action(EntryAccountEdit.get_action())


@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountShow(XferShowEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Show accounting entry")

    def clear_fields_in_params(self):
        if (self.getparam('SAVE', '') == 'YES') and (self.getparam('costaccounting') is not None):
            self.item.costaccounting_id = self.getparam('costaccounting', 0)
            if self.item.costaccounting_id == 0:
                self.item.costaccounting_id = None
            self.item.save()
        XferShowEditor.clear_fields_in_params(self)


@ActionsManage.affect_grid(TITLE_ADD, 'images/add.png', unique=SELECT_NONE, condition=lambda xfer, gridname='': (xfer.item.year.status in [0, 1]) and (xfer.getparam('filter', 0) != 2))
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountEdit(XferAddEditor):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    redirect_to_show = 'AfterSave'
    caption_add = _("Add entry of account")
    caption_modify = _("Modify accounting entry")

    def fillresponse(self):
        self.item.check_date()
        XferAddEditor.fillresponse(self)
        self.actions = []
        if self.no_change:
            if self.added:
                self.add_action(self.get_action(TITLE_MODIFY, "images/ok.png"), params={"SAVE": "YES"})
                self.add_action(EntryAccountClose.get_action(_("Closed"), "images/up.png"), close=CLOSE_YES, params={"REOPEN": "YES"})
            if (self.item.link is None) and self.item.has_third and not self.item.has_cash:
                self.add_action(EntryAccountCreateLinked.get_action(_('Payment'), "images/right.png"), close=CLOSE_YES)
            self.add_action(EntryAccountReverse.get_action(_('Reverse'), 'images/edit.png'), close=CLOSE_YES)
            self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))
        else:
            if (self.debit_rest < 0.0001) and (self.credit_rest < 0.0001) and (self.nb_lines > 0):
                self.add_action(EntryAccountValidate.get_action(TITLE_OK, 'images/ok.png'))
            elif self.added:
                self.add_action(self.get_action(TITLE_MODIFY, "images/ok.png"), params={"SAVE": "YES"})
            if self.item.id is None:
                self.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
            else:
                self.add_action(EntryAccountUnlock.get_action(TITLE_CANCEL, 'images/cancel.png'))


@MenuManage.describ('')
class EntryAccountUnlock(XferContainerAcknowledge):
    model = EntryAccount
    field_id = 'entryaccount'

    def fillresponse(self):
        self.item.delete_if_ghost_entry()


@ActionsManage.affect_other('', '')
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountAfterSave(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Modify accounting entry")

    def fillresponse(self):
        for old_key in ['date_value', 'designation', 'SAVE']:
            if old_key in self.params.keys():
                del self.params[old_key]
        self.redirect_action(EntryAccountEdit.get_action())


@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountValidate(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Validate entry line of account")

    def fillresponse(self, serial_entry=''):
        save = XferSave()
        save.model = self.model
        save.field_id = self.field_id
        save.caption = self.caption
        save._initialize(self.request)
        save.params["SAVE"] = "YES"
        save.fillresponse()
        self.item.save_entrylineaccounts(serial_entry)
        linked_entryaccount = self.getparam('linked_entryaccount', 0)
        if linked_entryaccount != 0:
            try:
                linked_entry = EntryAccount.objects.get(id=linked_entryaccount)
                AccountLink.create_link(list(self.item.get_thirds()) + list(linked_entry.get_thirds()))
            except Exception:
                pass
        for old_key in ['date_value', 'designation', 'SAVE', 'serial_entry', 'linked_entryaccount']:
            if old_key in self.params.keys():
                del self.params[old_key]
        self.redirect_action(EntryAccountEdit.get_action())


@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountReverse(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Reverse entry lines of account")

    def fillresponse(self):
        for old_key in ['serial_entry']:
            if old_key in self.params.keys():
                del self.params[old_key]
        self.item.reverse_entry()
        self.redirect_action(EntryAccountEdit.get_action(), {})


@ActionsManage.affect_show(_('Payment'), '', condition=lambda xfer: (xfer.item.entrylineaccount_set.filter(link__isnull=False).count() == 0) and xfer.item.has_third and not xfer.item.has_cash)
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountCreateLinked(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Add payment entry of account")

    def fillresponse(self):
        new_entry, serial_entry = self.item.create_linked()
        self.redirect_action(EntryAccountEdit.get_action(), params={"serial_entry": serial_entry,
                                                                    'journal': '4', 'entryaccount': new_entry.id,
                                                                    'linked_entryaccount': self.item.id,
                                                                    'num_cpt_txt': current_system_account().get_cash_begin()})


@ActionsManage.affect_grid(_("Model"), "images/add.png", unique=SELECT_NONE, condition=lambda xfer, gridname='': (xfer.item.year.status in [0, 1]) and (xfer.getparam('filter', 0) != 2))
@MenuManage.describ('accounting.add_entryaccount')
class EntryAccountModelSelector(XferContainerAcknowledge):
    icon = "entryModel.png"
    model = EntryAccount
    field_id = 'entryaccount'
    caption = _("Select model of entry")

    def fillresponse(self, journal=0):
        if self.getparam('SAVE') is None:
            dlg = self.create_custom()
            image = XferCompImage('image')
            image.set_value(self.icon_path())
            image.set_location(0, 0, 1, 6)
            dlg.add_component(image)
            if journal > 0:
                mod_query = ModelEntry.objects.filter(journal=journal)
            else:
                mod_query = ModelEntry.objects.all()
            sel = XferCompSelect('model')
            sel.set_location(1, 0)
            sel.set_needed(True)
            sel.set_select_query(mod_query)
            sel.description = _('model name')
            dlg.add_component(sel)
            fact = XferCompFloat('factor', 0.00, 1000000.0, 2)
            fact.set_value(1.0)
            fact.set_location(1, 1)
            fact.description = _('factor')
            dlg.add_component(fact)
            dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"SAVE": "YES"})
            dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))
        else:
            factor = self.getparam('factor', 1.0)
            model = ModelEntry.objects.get(id=self.getparam('model', 0))
            for old_key in ['SAVE', 'model', 'factor']:
                if old_key in self.params.keys():
                    del self.params[old_key]
            year = FiscalYear.get_current(self.getparam('year'))
            serial_entry = model.get_serial_entry(factor, year, model.costaccounting)
            date_value = date.today().isoformat()
            entry = EntryAccount.objects.create(year=year, date_value=date_value, designation=model.designation, journal=model.journal)
            entry.editor.before_save(self)
            self.params["entryaccount"] = entry.id
            self.redirect_action(EntryAccountEdit.get_action(), params={"serial_entry": serial_entry})


@ActionsManage.affect_other(TITLE_ADD, "images/add.png", close=CLOSE_YES)
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountAdd(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Save entry line of account")

    def fillresponse(self, entryaccount=0, entrylineaccount_serial=0, serial_entry='', num_cpt=0, credit_val=0.0, debit_val=0.0, third=0, costaccounting=0, reference='None'):
        if (credit_val > 0.0001) or (debit_val > 0.0001):
            for old_key in ['num_cpt_txt', 'num_cpt', 'credit_val', 'debit_val', 'third', 'reference', 'entrylineaccount_serial', 'serial_entry']:
                if old_key in self.params.keys():
                    del self.params[old_key]
            entry = EntryAccount.objects.get(id=entryaccount)
            serial_entry = entry.add_new_entryline(serial_entry, entrylineaccount_serial, num_cpt, credit_val, debit_val, third, costaccounting, reference)
        self.redirect_action(EntryAccountEdit.get_action(), params={"serial_entry": serial_entry})


@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, close=CLOSE_YES)
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountEdit(XferContainerCustom):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Modify entry line of account")

    def fillresponse(self, entryaccount, entrylineaccount_serial=0, serial_entry=''):
        if 'reference' in self.params.keys():
            del self.params['reference']
        entry = EntryAccount.objects.get(id=entryaccount)
        for line in entry.get_entrylineaccounts(serial_entry):
            if line.id == entrylineaccount_serial:
                self.item = line
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 6)
        self.add_component(img)
        self.fill_from_model(1, 1, True, ['account'])
        self.item.editor.edit_creditdebit_for_line(self, 1, 2)
        self.item.editor.edit_extra_for_line(self, 1, 4, False)
        self.add_action(EntryLineAccountAdd.get_action(TITLE_OK, 'images/ok.png'), params={"num_cpt": self.item.account.id})
        self.add_action(EntryAccountEdit.get_action(TITLE_CANCEL, 'images/cancel.png'))


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_SINGLE, close=CLOSE_YES)
@MenuManage.describ('accounting.add_entryaccount')
class EntryLineAccountDel(XferContainerAcknowledge):
    icon = "entry.png"
    model = EntryLineAccount
    field_id = 'entrylineaccount'
    caption = _("Delete entry line of account")

    def fillresponse(self, entryaccount=0, entrylineaccount_serial=0, serial_entry=''):
        for old_key in ['serial_entry', 'entrylineaccount_serial']:
            if old_key in self.params.keys():
                del self.params[old_key]
        entry = EntryAccount.objects.get(id=entryaccount)
        serial_entry = entry.remove_entrylineaccounts(serial_entry, entrylineaccount_serial)
        self.redirect_action(EntryAccountEdit.get_action(), params={"serial_entry": serial_entry})
