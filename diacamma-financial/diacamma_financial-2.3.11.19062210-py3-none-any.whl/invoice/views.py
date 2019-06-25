# -*- coding: utf-8 -*-
'''
diacamma.invoice view package

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
from datetime import date

from django.utils.translation import ugettext_lazy as _
from django.utils import formats, six
from django.db.models.functions import Concat
from django.db.models import Q, Value
from django.db.models.query import QuerySet

from lucterios.framework.xferadvance import TITLE_PRINT, TITLE_CLOSE, TITLE_DELETE, TITLE_MODIFY, TITLE_ADD, TITLE_CANCEL, TITLE_OK, TITLE_EDIT,\
    TITLE_LABEL
from lucterios.framework.xferadvance import XferListEditor, XferShowEditor, XferAddEditor, XferDelete, XferTransition
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect, XferCompImage, XferCompGrid, XferCompCheck, XferCompEdit, XferCompCheckList, XferCompMemo,\
    XferCompButton
from lucterios.framework.tools import FORMTYPE_NOMODAL, ActionsManage, MenuManage, FORMTYPE_MODAL, CLOSE_YES, SELECT_SINGLE, FORMTYPE_REFRESH, CLOSE_NO, SELECT_MULTI, WrapAction
from lucterios.framework.xfergraphic import XferContainerAcknowledge, XferContainerCustom
from lucterios.framework.error import LucteriosException, IMPORTANT
from lucterios.framework import signal_and_lock

from lucterios.CORE.xferprint import XferPrintAction, XferPrintReporting, XferPrintListing,\
    XferPrintLabel
from lucterios.CORE.parameters import Params
from lucterios.CORE.editors import XferSavedCriteriaSearchEditor
from lucterios.CORE.models import PrintModel
from lucterios.CORE.views import ObjectMerge

from lucterios.contacts.views_contacts import AbstractContactFindDouble
from lucterios.contacts.models import Individual, LegalEntity

from diacamma.invoice.models import Article, Bill, Detail, Category, Provider,\
    StorageArea, AutomaticReduce
from diacamma.payoff.views import PayoffAddModify, PayableEmail, can_send_email
from diacamma.payoff.models import Payoff
from diacamma.accounting.models import FiscalYear, Third
from diacamma.accounting.views import get_main_third
from diacamma.accounting.tools import current_system_account, format_devise
from lucterios.framework.xfersearch import get_criteria_list

MenuManage.add_sub("invoice", None, "diacamma.invoice/images/invoice.png", _("invoice"), _("Manage of billing"), 45)


def _add_bill_filter(xfer, row, with_third=False):
    current_filter = Q()
    if with_third:
        third_filter = xfer.getparam('filter', '')
        comp = XferCompEdit('filter')
        comp.set_value(third_filter)
        comp.is_default = True
        comp.description = _('Filtrer by third')
        comp.set_action(xfer.request, xfer.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        comp.set_location(0, row)
        xfer.add_component(comp)
        row += 1
        if third_filter != "":
            q_legalentity = Q(third__contact__legalentity__name__icontains=third_filter)
            # annotate(completename=Concat('third__contact__individual__lastname', Value(' '), 'third__contact__individual__firstname'))
            q_individual = Q(completename__icontains=third_filter)
            current_filter &= (q_legalentity | q_individual)
    status_filter = xfer.getparam('status_filter', -1)
    dep_field = Bill.get_field_by_name('status')
    sel_list = list(dep_field.choices)
    sel_list.insert(0, (-1, '%s+%s' % (_('building'), _('valid'))))
    sel_list.append((-2, None))
    edt = XferCompSelect("status_filter")
    edt.set_select(sel_list)
    edt.description = _('Filter by status')
    edt.set_value(status_filter)
    edt.set_location(0, row)
    edt.set_action(xfer.request, xfer.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
    xfer.add_component(edt)

    type_filter = xfer.getparam('type_filter', -1)
    dep_field = Bill.get_field_by_name('bill_type')
    sel_list = list(dep_field.choices)
    sel_list.insert(0, (-1, None))
    edt = XferCompSelect("type_filter")
    edt.set_select(sel_list)
    edt.description = _('Filter by type')
    edt.set_value(type_filter)
    edt.set_location(0, row + 1)
    edt.set_action(xfer.request, xfer.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
    xfer.add_component(edt)

    if status_filter >= 0:
        current_filter &= Q(status=status_filter)
    elif status_filter == -1:
        current_filter &= Q(status=0) | Q(status=1)
    if type_filter >= 0:
        current_filter &= Q(bill_type=type_filter)
    return current_filter, status_filter


@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('Management of bill list'))
class BillList(XferListEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Bill")

    def fillresponse_header(self):
        self.filter, status_filter = _add_bill_filter(self, 3, True)
        self.fieldnames = Bill.get_default_fields(status_filter)

    def get_items_from_filter(self):
        items = self.model.objects.annotate(completename=Concat('third__contact__individual__lastname',
                                                                Value(' '), 'third__contact__individual__firstname')).filter(self.filter)
        sort_bill = self.getparam('GRID_ORDER%bill', '').split(',')
        sort_bill_third = self.getparam('GRID_ORDER%bill_third', '')
        if ((len(sort_bill) == 0) and (sort_bill_third != '')) or (sort_bill.count('third') + sort_bill.count('-third')) > 0:
            self.params['GRID_ORDER%bill'] = ""
            if sort_bill_third.startswith('+'):
                sort_bill_third = "-"
            else:
                sort_bill_third = "+"
            self.params['GRID_ORDER%bill_third'] = sort_bill_third
            items = sorted(items, key=lambda t: six.text_type(t.third).lower(), reverse=sort_bill_third.startswith('-'))
            res = QuerySet(model=Bill)
            res._result_cache = items
            return res
        else:
            self.params['GRID_ORDER%bill_third'] = ''
            return items

    def fillresponse(self):
        XferListEditor.fillresponse(self)
        grid = self.get_components(self.field_id)
        grid.colspan = 3
        if Params.getvalue("invoice-vat-mode") == 1:
            grid.headers[5].descript = _('total excl. taxes')
        elif Params.getvalue("invoice-vat-mode") == 2:
            grid.headers[5].descript = _('total incl. taxes')


@MenuManage.describ('invoice.change_bill', FORMTYPE_NOMODAL, 'invoice', _('To find a bill following a set of criteria.'))
class BillSearch(XferSavedCriteriaSearchEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Search bill")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) < 1)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status == 0)
@MenuManage.describ('invoice.add_bill')
class BillAddModify(XferAddEditor):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption_add = _("Add bill")
    caption_modify = _("Modify bill")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.change_bill')
class BillShow(XferShowEditor):
    caption = _("Show bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        XferShowEditor.fillresponse(self)
        self.add_action(ActionsManage.get_action_url('payoff.Supporting', 'Show', self),
                        close=CLOSE_NO, params={'item_name': self.field_id}, pos_act=0)


@ActionsManage.affect_transition("status", multi_list=('archive',))
@MenuManage.describ('invoice.add_bill')
class BillTransition(XferTransition):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fill_dlg_payoff(self, withpayoff, sendemail):
        dlg = self.create_custom(Payoff)
        dlg.caption = _("Confirmation")
        icon = XferCompImage('img')
        icon.set_location(0, 0, 1, 6)
        icon.set_value(self.icon_path())
        dlg.add_component(icon)
        lbl = XferCompLabelForm('lb_title')
        lbl.set_value_as_infocenter(_("Do you want validate '%s'?") % self.item)
        lbl.set_location(1, 1, 2)
        dlg.add_component(lbl)
        if (self.item.bill_type != 0) and (abs(self.item.get_total_rest_topay()) > 0.0001):
            check_payoff = XferCompCheck('withpayoff')
            check_payoff.set_value(withpayoff)
            check_payoff.set_location(1, 2)
            check_payoff.java_script = """
    var type=current.getValue();
    parent.get('date_payoff').setEnabled(type);
    parent.get('amount').setEnabled(type);
    parent.get('payer').setEnabled(type);
    parent.get('mode').setEnabled(type);
    parent.get('reference').setEnabled(type);
    if (parent.get('bank_account')) {
        parent.get('bank_account').setEnabled(type);
    }
    """
            check_payoff.description = _("Payment of deposit or cash")
            dlg.add_component(check_payoff)
            dlg.item.supporting = self.item
            dlg.fill_from_model(2, 3, False)
            if dlg.get_components("bank_fee") is not None:
                check_payoff.java_script += "parent.get('bank_fee').setEnabled(type);\n"
            dlg.get_components("date").name = "date_payoff"
            dlg.get_components("mode").set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        if (self.item.bill_type != 2) and can_send_email(dlg):
            row = dlg.get_max_row()
            check_payoff = XferCompCheck('sendemail')
            check_payoff.set_value(sendemail)
            check_payoff.set_location(1, row + 1)
            check_payoff.java_script = """
    var type=current.getValue();
    parent.get('subject').setEnabled(type);
    parent.get('message').setEnabled(type);
    parent.get('model').setEnabled(type);
    """
            check_payoff.description = _("Send email with PDF")
            dlg.add_component(check_payoff)
            edt = XferCompEdit('subject')
            edt.set_value(six.text_type(self.item))
            edt.set_location(2, row + 2)
            edt.description = _('subject')
            dlg.add_component(edt)
            contact = self.item.third.contact.get_final_child()
            memo = XferCompMemo('message')
            memo.description = _('message')
            memo.set_value(Params.getvalue('payoff-email-message') % {'name': contact.get_presentation(), 'doc': self.item.get_docname()})
            memo.with_hypertext = True
            memo.set_size(130, 450)
            memo.set_location(2, row + 3)
            dlg.add_component(memo)
            selectors = PrintModel.get_print_selector(2, self.item.__class__)[0]
            sel = XferCompSelect('model')
            sel.set_select(selectors[2])
            sel.set_location(2, row + 4)
            sel.description = selectors[1]
            dlg.add_component(sel)
        dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"CONFIRME": "YES"})
        dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))

    def fill_confirm(self, transition, trans):
        withpayoff = self.getparam('withpayoff', False)
        sendemail = self.getparam('sendemail', False)
        if transition != 'valid':
            XferTransition.fill_confirm(self, transition, trans)
            if transition == 'cancel':
                if self.trans_result is not None:
                    self.redirect_action(ActionsManage.get_action_url('invoice.Bill', 'Show', self), params={self.field_id: self.trans_result})
        elif self.getparam("CONFIRME") is None:
            self.fill_dlg_payoff(withpayoff, sendemail)
        else:
            if (self.item.bill_type != 0) and withpayoff:
                Payoff.multi_save((self.item.id,), self.getparam('amount', 0.0), self.getparam('mode', 0), self.getparam('payer'),
                                  self.getparam('reference'), self.getparam('bank_account', 0), self.getparam('date_payoff'), self.getparam('bank_fee', 0.0), repartition=0)
            XferTransition.fill_confirm(self, transition, trans)
            if sendemail:
                self.redirect_action(PayableEmail.get_action("", ""), params={"item_name": self.field_id, "OK": "YES"})


@ActionsManage.affect_grid(_('payoff'), '', close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) == 1)
@MenuManage.describ('payoff.add_payoff')
class BillMultiPay(XferContainerAcknowledge):
    caption = _("Multi-pay bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self, bill):
        self.redirect_action(PayoffAddModify.get_action("", ""), params={"supportings": bill})


@ActionsManage.affect_show(_("=> Bill"), "images/ok.png", close=CLOSE_YES, condition=lambda xfer: (xfer.item.status == 1) and (xfer.item.bill_type == 0))
@MenuManage.describ('invoice.change_bill')
class BillFromQuotation(XferContainerAcknowledge):
    caption = _("Convert to bill")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        if (self.item.bill_type == 0) and (self.item.status == 1) and self.confirme(_("Do you want convert '%s' to bill?") % self.item):
            new_bill = self.item.convert_to_bill()
            if new_bill is not None:
                self.redirect_action(ActionsManage.get_action_url('invoice.Bill', 'Show', self), params={self.field_id: new_bill.id})


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status_filter', -1) < 1)
@MenuManage.describ('invoice.delete_bill')
class BillDel(XferDelete):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Delete bill")


def can_printing(xfer, gridname=''):
    if xfer.getparam('CRITERIA') is not None:
        for criteria_item in get_criteria_list(xfer.getparam('CRITERIA')):
            if (criteria_item[0] == 'status') and (criteria_item[2] in ('1', '3', '1;3')):
                return True
        return False
    else:
        return xfer.getparam('status_filter', -1) in (1, 3)


@ActionsManage.affect_grid(_("Send"), "lucterios.mailing/images/email.png", close=CLOSE_NO, unique=SELECT_MULTI, condition=lambda xfer, gridname='': can_printing(xfer) and can_send_email(xfer))
@ActionsManage.affect_show(_("Send"), "lucterios.mailing/images/email.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.status in (1, 3) and can_send_email(xfer))
@MenuManage.describ('invoice.change_bill')
class BillPayableEmail(XferContainerAcknowledge):
    caption = _("Send by email")
    icon = "bill.png"
    model = Bill
    field_id = 'bill'

    def fillresponse(self):
        self.redirect_action(ActionsManage.get_action_url('payoff.Supporting', 'Email', self),
                             close=CLOSE_NO, params={'item_name': self.field_id})


@ActionsManage.affect_grid(_("Print"), "images/print.png", close=CLOSE_NO, unique=SELECT_MULTI, condition=can_printing)
@ActionsManage.affect_show(_("Print"), "images/print.png", close=CLOSE_NO, condition=lambda xfer: xfer.item.status in (1, 3))
@MenuManage.describ('invoice.change_bill')
class BillPrint(XferPrintReporting):
    icon = "bill.png"
    model = Bill
    field_id = 'bill'
    caption = _("Print bill")

    def get_print_name(self):
        if len(self.items) == 1:
            current_bill = self.items[0]
            return current_bill.get_document_filename()
        else:
            return six.text_type(self.caption)

    def items_callback(self):
        has_item = False
        for item in self.items:
            if item.status > 0:
                has_item = True
                yield item
        if not has_item:
            raise LucteriosException(IMPORTANT, _("No invoice to print!"))


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_bill')
class DetailAddModify(XferAddEditor):
    icon = "article.png"
    model = Detail
    field_id = 'detail'
    caption_add = _("Add detail")
    caption_modify = _("Modify detail")

    def fillresponse(self):
        if self.getparam('CHANGE_ART') is not None:
            if self.item.article is not None:
                self.item.designation = self.item.article.get_designation()
                self.item.price = self.item.article.price
                self.item.unit = self.item.article.unit
        XferAddEditor.fillresponse(self)


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.add_bill')
class DetailDel(XferDelete):
    icon = "article.png"
    model = Detail
    field_id = 'detail'
    caption = _("Delete detail")


@MenuManage.describ('invoice.change_article', FORMTYPE_NOMODAL, 'invoice', _('Management of article list'))
class ArticleList(XferListEditor):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Articles")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.categories_filter = ()

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        if len(self.categories_filter) > 0:
            for cat_item in Category.objects.filter(id__in=self.categories_filter):
                items = items.filter(categories__in=[cat_item])
        return items.distinct()

    def fillresponse_header(self):
        show_filter = self.getparam('show_filter', 0)
        show_stockable = self.getparam('stockable', -1)
        ref_filter = self.getparam('ref_filter', '')
        self.categories_filter = self.getparam('cat_filter', ())
        show_storagearea = self.getparam('storagearea', 0)

        edt = XferCompSelect("show_filter")
        edt.set_select([(0, _('Only activate')), (1, _('All'))])
        edt.set_value(show_filter)
        edt.set_location(0, 3, 2)
        edt.description = _('Show articles')
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        edt = XferCompEdit("ref_filter")
        edt.set_value(ref_filter)
        edt.set_location(0, 4)
        edt.is_default = True
        edt.description = _('ref./designation')
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        self.fill_from_model(0, 5, False, ['stockable'])
        sel_stock = self.get_components('stockable')
        sel_stock.select_list.insert(0, (-1, '---'))
        sel_stock.set_value(show_stockable)
        sel_stock.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)

        cat_list = Category.objects.all()
        if len(cat_list) > 0:
            edt = XferCompCheckList("cat_filter")
            edt.set_select_query(cat_list)
            edt.set_value(self.categories_filter)
            edt.set_location(1, 4, 1, 2)
            edt.description = _('categories')
            edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            self.add_component(edt)

        sel_stock = XferCompSelect('storagearea')
        sel_stock.set_needed(False)
        sel_stock.set_select_query(StorageArea.objects.all())
        sel_stock.set_value(show_storagearea)
        sel_stock.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        sel_stock.set_location(0, 6)
        sel_stock.description = StorageArea._meta.verbose_name
        if len(sel_stock.select_list) > 1:
            self.add_component(sel_stock)

        self.filter = Q()
        if ref_filter != '':
            self.filter &= Q(reference__icontains=ref_filter) | Q(designation__icontains=ref_filter)
        if show_filter == 0:
            self.filter &= Q(isdisabled=False)
        if show_stockable != -1:
            self.filter &= Q(stockable=show_stockable)
        if show_storagearea != 0:
            self.filter &= Q(storagedetail__storagesheet__storagearea=show_storagearea)
        self.add_action(ArticleSearch.get_action(_("Search"), "diacamma.invoice/images/article.png"), modal=FORMTYPE_NOMODAL, close=CLOSE_YES)


@ActionsManage.affect_list(TITLE_PRINT, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('invoice.change_article')
class ArticlePrint(XferPrintListing):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Print articles")

    def filter_callback(self, items):
        categories_filter = self.getparam('cat_filter', ())
        if len(categories_filter) > 0:
            for cat_item in Category.objects.filter(id__in=categories_filter):
                items = items.filter(categories__in=[cat_item])
        return items.distinct()

    def get_filter(self):
        show_filter = self.getparam('show_filter', 0)
        show_stockable = self.getparam('stockable', -1)
        ref_filter = self.getparam('ref_filter', '')
        show_storagearea = self.getparam('storagearea', 0)
        new_filter = Q()
        if ref_filter != '':
            new_filter &= Q(reference__icontains=ref_filter) | Q(designation__icontains=ref_filter)
        if show_filter == 0:
            new_filter &= Q(isdisabled=False)
        if show_stockable != -1:
            new_filter &= Q(stockable=show_stockable)
        if show_storagearea != 0:
            new_filter &= Q(storagedetail__storagesheet__storagearea=show_storagearea)
        return new_filter


@ActionsManage.affect_list(TITLE_LABEL, "images/print.png", close=CLOSE_NO)
@MenuManage.describ('invoice.change_article')
class ArticleLabel(XferPrintLabel):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Label articles")

    def filter_callback(self, items):
        categories_filter = self.getparam('cat_filter', ())
        if len(categories_filter) > 0:
            for cat_item in Category.objects.filter(id__in=categories_filter):
                items = items.filter(categories__in=[cat_item])
        return items.distinct()

    def get_filter(self):
        show_filter = self.getparam('show_filter', 0)
        show_stockable = self.getparam('stockable', -1)
        ref_filter = self.getparam('ref_filter', '')
        show_storagearea = self.getparam('storagearea', 0)
        new_filter = Q()
        if ref_filter != '':
            new_filter &= Q(reference__icontains=ref_filter) | Q(designation__icontains=ref_filter)
        if show_filter == 0:
            new_filter &= Q(isdisabled=False)
        if show_stockable != -1:
            new_filter &= Q(stockable=show_stockable)
        if show_storagearea != 0:
            new_filter &= Q(storagedetail__storagesheet__storagearea=show_storagearea)
        return new_filter


@MenuManage.describ('accounting.change_article')
class ArticleSearch(XferSavedCriteriaSearchEditor):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Search article")

    def fillresponse(self):
        XferSavedCriteriaSearchEditor.fillresponse(self)
        if WrapAction.is_permission(self.request, 'invoice.add_article'):
            self.get_components(self.field_id).add_action(self.request, ObjectMerge.get_action(_("Merge"), "images/clone.png"),
                                                          close=CLOSE_NO, unique=SELECT_MULTI, params={'modelname': self.model.get_long_name(), 'field_id': self.field_id})
        self.add_action(AbstractContactFindDouble.get_action(_("duplicate"), "images/clone.png"),
                        params={'modelname': self.model.get_long_name(), 'field_id': self.field_id}, pos_act=0)


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.change_article')
class ArticleShow(XferShowEditor):
    caption = _("Show article")
    icon = "article.png"
    model = Article
    field_id = 'article'


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES)
@MenuManage.describ('invoice.add_article')
class ArticleAddModify(XferAddEditor):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption_add = _("Add article")
    caption_modify = _("Modify article")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_article')
class ArticleDel(XferDelete):
    icon = "article.png"
    model = Article
    field_id = 'article'
    caption = _("Delete article")


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png")
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.add_article')
class ProviderAddModify(XferAddEditor):
    icon = "article.png"
    model = Provider
    field_id = 'provider'
    caption_add = _("Add provider")
    caption_modify = _("Modify provider")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI)
@MenuManage.describ('invoice.delete_article')
class ProviderDel(XferDelete):
    icon = "article.png"
    model = Provider
    field_id = 'provider'
    caption = _("Delete provider")


@MenuManage.describ('invoice.change_bill', FORMTYPE_MODAL, 'invoice', _('Statistic of selling'))
class BillStatistic(XferContainerCustom):
    icon = "report.png"
    model = Bill
    field_id = 'bill'
    caption = _("Statistic")

    def fill_header(self):
        img = XferCompImage('img')
        img.set_value(self.icon_path())
        img.set_location(0, 0, 1, 2)
        self.add_component(img)
        select_year = self.getparam('fiscal_year')
        lbl = XferCompLabelForm('lbl_title')
        lbl.set_value_as_headername(_('Statistics in date of %s') % formats.date_format(date.today(), "DATE_FORMAT"))
        lbl.set_location(1, 0, 2)
        self.add_component(lbl)
        self.item.fiscal_year = FiscalYear.get_current(select_year)
        self.fill_from_model(1, 1, False, ['fiscal_year'])
        fiscal_year = self.get_components('fiscal_year')
        fiscal_year.set_needed(True)
        fiscal_year.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        ck = XferCompCheck('without_reduct')
        ck.set_value(self.getparam('without_reduct', False))
        ck.set_location(1, 2, 2)
        ck.description = _('Without reduction')
        ck.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(ck)

    def fill_customers(self):
        costumer_result = self.item.get_statistics_customer(self.getparam('without_reduct', False))
        grid = XferCompGrid("customers")
        grid.add_header("customer", _("customer"))
        grid.add_header("amount", _("amount"))
        grid.add_header("ratio", _("ratio (%)"))
        index = 0
        for cust_val in costumer_result:
            grid.set_value(index, "customer", cust_val[0])
            grid.set_value(index, "amount", cust_val[1])
            grid.set_value(index, "ratio", cust_val[2])
            index += 1
        grid.set_location(0, 1, 3)
        grid.set_size(400, 800)
        self.add_component(grid)

    def fill_articles(self):
        articles_result = self.item.get_statistics_article(self.getparam('without_reduct', False))
        grid = XferCompGrid("articles")
        grid.add_header("article", _("article"))
        grid.add_header("amount", _("amount"))
        grid.add_header("number", _("number"))
        grid.add_header("mean", _("mean"))
        grid.add_header("ratio", _("ratio (%)"))
        index = 0
        for art_val in articles_result:
            grid.set_value(index, "article", art_val[0])
            grid.set_value(index, "amount", art_val[1])
            grid.set_value(index, "number", art_val[2])
            grid.set_value(index, "mean", art_val[3])
            grid.set_value(index, "ratio", art_val[4])
            index += 1
        grid.set_location(0, 1, 3)
        grid.set_size(400, 800)
        self.add_component(grid)

    def fill_month(self):
        month_result = self.item.get_statistics_month(self.getparam('without_reduct', False))
        grid = XferCompGrid("months")
        grid.add_header("month", _("month"))
        grid.add_header("amount", _("amount"))
        grid.add_header("ratio", _("ratio (%)"))
        index = 0
        for month_val in month_result:
            grid.set_value(index, "month", month_val[0])
            grid.set_value(index, "amount", month_val[1])
            grid.set_value(index, "ratio", month_val[2])
            index += 1
        grid.set_location(0, 1, 3)
        grid.set_size(400, 800)
        self.add_component(grid)

    def fillresponse(self):
        self.fill_header()
        self.new_tab(_('Customers'))
        self.fill_customers()
        self.new_tab(_('Articles'))
        self.fill_articles()
        self.new_tab(_('By month'))
        self.fill_month()
        self.add_action(BillStatisticPrint.get_action(TITLE_PRINT, "images/print.png"), close=CLOSE_NO, params={'classname': self.__class__.__name__})
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('invoice.change_bill')
class BillStatisticPrint(XferPrintAction):
    caption = _("Print statistic")
    icon = "report.png"
    model = Bill
    field_id = 'bill'
    action_class = BillStatistic
    with_text_export = True


@MenuManage.describ('invoice.change_bill')
class BillCheckAutoreduce(XferContainerAcknowledge):
    caption = _("Check auto-reduce")
    icon = "bill.png"
    model = Third
    field_id = 'third'

    def fillresponse(self):
        if self.confirme(_('Do you want check auto-reduce ?')):
            filter_auto = Q(bill__third=self.item) & Q(bill__bill_type__in=(0, 1, 3)) & Q(bill__status=0)
            for detail in Detail.objects.filter(filter_auto).distinct():
                detail.reduce = 0
                detail.save(check_autoreduce=False)
            for detail in Detail.objects.filter(filter_auto).distinct().order_by('-price', '-quantity'):
                detail.save(check_autoreduce=True)


@signal_and_lock.Signal.decorate('situation')
def situation_invoice(xfer):
    if not hasattr(xfer, 'add_component'):
        contacts = []
        if not xfer.user.is_anonymous:
            for contact in Individual.objects.filter(user=xfer.user).distinct():
                contacts.append(contact.id)
            for contact in LegalEntity.objects.filter(responsability__individual__user=xfer.user).distinct():
                contacts.append(contact.id)
        return len(contacts) > 0
    else:
        contacts = []
        if not xfer.request.user.is_anonymous:
            for contact in Individual.objects.filter(user=xfer.request.user).distinct():
                contacts.append(contact.id)
            for contact in LegalEntity.objects.filter(responsability__individual__user=xfer.request.user).distinct():
                contacts.append(contact.id)
        if len(contacts) > 0:
            row = xfer.get_max_row() + 1
            lab = XferCompLabelForm('invoicetitle')
            lab.set_value_as_infocenter(_("Invoice"))
            lab.set_location(0, row, 4)
            xfer.add_component(lab)
            nb_build = len(Bill.objects.filter(third__contact_id__in=contacts).distinct())
            lab = XferCompLabelForm('invoicecurrent')
            lab.set_value_as_header(_("You are %d bills") % nb_build)
            lab.set_location(0, row + 1, 4)
            xfer.add_component(lab)
            lab = XferCompLabelForm('invoicesep')
            lab.set_value_as_infocenter("{[hr/]}")
            lab.set_location(0, row + 2, 4)
            xfer.add_component(lab)
            return True
        else:
            return False


@signal_and_lock.Signal.decorate('summary')
def summary_invoice(xfer):
    if not hasattr(xfer, 'add_component'):
        return WrapAction.is_permission(xfer, 'invoice.change_bill')
    else:
        if WrapAction.is_permission(xfer.request, 'invoice.change_bill'):
            row = xfer.get_max_row() + 1
            lab = XferCompLabelForm('invoicetitle')
            lab.set_value_as_infocenter(_("Invoice"))
            lab.set_location(0, row, 4)
            xfer.add_component(lab)
            nb_build = len(Bill.objects.filter(status=0))
            nb_valid = len(Bill.objects.filter(status=1))
            lab = XferCompLabelForm('invoiceinfo')
            lab.set_value_as_header(_("There are %(build)d bills in building and %(valid)d validated") % {'build': nb_build, 'valid': nb_valid})
            lab.set_location(0, row + 1, 4)
            xfer.add_component(lab)
            lab = XferCompLabelForm('invoicesep')
            lab.set_value_as_infocenter("{[hr/]}")
            lab.set_location(0, row + 2, 4)
            xfer.add_component(lab)
            return True
        else:
            return False


@signal_and_lock.Signal.decorate('third_addon')
def thirdaddon_invoice(item, xfer):
    if WrapAction.is_permission(xfer.request, 'invoice.change_bill'):
        try:
            FiscalYear.get_current()
            xfer.new_tab(_('Invoice'))
            current_filter, status_filter = _add_bill_filter(xfer, 1)
            current_filter &= Q(third=item)
            bills = Bill.objects.filter(current_filter).distinct()
            bill_grid = XferCompGrid('bill')
            bill_grid.set_model(bills, Bill.get_default_fields(status_filter), xfer)
            bill_grid.add_action_notified(xfer, Bill)
            bill_grid.set_location(0, 2, 2)
            xfer.add_component(bill_grid)
            if len(bills) > 0:
                reduce_sum = 0.0
                total_sum = 0.0
                for bill in bills:
                    if ((bill.bill_type == 0) and (bill.status == 3)) or (bill.status == 2):
                        continue
                    total_sum += bill.get_total()
                    for detail in bill.detail_set.all():
                        reduce_sum += detail.get_reduce()
                gross_sum = total_sum + reduce_sum
                lab = XferCompLabelForm('sum_summary')
                lab.set_value(_("{[b]}Gross total{[/b]} : %(grosstotal)s - {[b]}total of reduces{[/b]} : %(reducetotal)s = {[b]}total to pay{[/b]} : %(total)s") %
                              {'grosstotal': format_devise(gross_sum, 5), 'reducetotal': format_devise(reduce_sum, 5), 'total': format_devise(total_sum, 5)})
                lab.set_location(0, 3, 2)
                xfer.add_component(lab)
                if AutomaticReduce.objects.all().count() > 0:
                    btn = XferCompButton('btn_autoreduce')
                    btn.set_action(xfer.request, BillCheckAutoreduce.get_action(_('Reduce'), ''), modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'third': item.id})
                    btn.set_location(0, 4, 2)
                    xfer.add_component(btn)
        except LucteriosException:
            pass


@signal_and_lock.Signal.decorate('show_contact')
def show_contact_invoice(contact, xfer):
    if WrapAction.is_permission(xfer.request, 'invoice.change_bill'):
        third = get_main_third(contact)
        if third is not None:
            accounts = third.accountthird_set.filter(Q(code__regex=current_system_account().get_customer_mask()))
            if len(accounts) > 0:
                xfer.new_tab(_("Financial"))
                nb_build = len(Bill.objects.filter(third=third, status=0))
                nb_valid = len(Bill.objects.filter(third=third, status=1))
                lab = XferCompLabelForm('invoiceinfo')
                lab.set_value_as_header(_("There are %(build)d bills in building and %(valid)d validated") % {'build': nb_build, 'valid': nb_valid})
                lab.set_location(0, 5, 2)
                xfer.add_component(lab)
                xfer.params['third'] = third.id
                thirdaddon_invoice(third, xfer)
