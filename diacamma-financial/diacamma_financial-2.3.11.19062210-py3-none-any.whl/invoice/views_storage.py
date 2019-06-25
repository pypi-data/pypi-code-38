# -*- coding: utf-8 -*-
'''
Describe view for Django

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
from django.db.models.aggregates import Sum
from django.db.models import Q

from lucterios.framework.tools import MenuManage, FORMTYPE_NOMODAL, ActionsManage, SELECT_SINGLE, SELECT_MULTI, CLOSE_YES, FORMTYPE_REFRESH, CLOSE_NO, SELECT_NONE, WrapAction
from lucterios.framework.xferadvance import XferListEditor, XferAddEditor, XferDelete, XferShowEditor, TITLE_ADD, TITLE_MODIFY, TITLE_DELETE, TITLE_EDIT, XferTransition, TITLE_PRINT, TITLE_CLOSE,\
    TITLE_OK, TITLE_CANCEL

from lucterios.CORE.xferprint import XferPrintAction
from lucterios.CORE.views import ObjectImport
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompGrid, XferCompSelect, XferCompCheckList, GRID_ORDER, XferCompDate,\
    XferCompEdit, XferCompImage
from lucterios.framework.xferbasic import NULL_VALUE

from diacamma.accounting.tools import format_devise
from diacamma.invoice.models import StorageSheet, StorageDetail, Article, Category, StorageArea


MenuManage.add_sub("storage", "invoice", "diacamma.invoice/images/storage.png", _("Storage"), _("Manage of storage"), 10)


def right_to_storage(request):
    if StorageSheetShow.get_action().check_permission(request):
        return len(StorageArea.objects.all()) > 0
    else:
        return False


@MenuManage.describ(right_to_storage, FORMTYPE_NOMODAL, 'storage', _('Management of storage sheet list'))
class StorageSheetList(XferListEditor):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'
    caption = _("Storage sheet")

    def fillresponse_header(self):
        status_filter = self.getparam('status', 0)
        type_filter = self.getparam('sheet_type', -1)
        self.fill_from_model(0, 1, False, ['status', 'sheet_type'])
        sel_status = self.get_components('status')
        sel_status.select_list.insert(0, (-1, '---'))
        sel_status.set_value(status_filter)
        sel_status.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        sel_type = self.get_components('sheet_type')
        sel_type.select_list.insert(0, (-1, '---'))
        sel_type.set_value(type_filter)
        sel_type.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.filter = Q()
        if status_filter != -1:
            self.filter &= Q(status=status_filter)
        if type_filter != -1:
            self.filter &= Q(sheet_type=type_filter)


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': xfer.getparam('status', -1) != 1)
@ActionsManage.affect_show(TITLE_MODIFY, "images/edit.png", close=CLOSE_YES, condition=lambda xfer: xfer.item.status == 0)
@MenuManage.describ('invoice.add_storagesheet')
class StorageSheetAddModify(XferAddEditor):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'
    caption_add = _("Add storage sheet")
    caption_modify = _("Modify storage sheet")


@ActionsManage.affect_grid(TITLE_EDIT, "images/show.png", unique=SELECT_SINGLE)
@MenuManage.describ('invoice.change_storagesheet')
class StorageSheetShow(XferShowEditor):
    caption = _("Show storage sheet")
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': xfer.getparam('status', -1) != 1)
@MenuManage.describ('invoice.delete_storagesheet')
class StorageSheetDel(XferDelete):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'
    caption = _("Delete storage sheet")


@ActionsManage.affect_transition("status")
@MenuManage.describ('invoice.add_storagesheet')
class StorageSheetTransition(XferTransition):
    icon = "storagesheet.png"
    model = StorageSheet
    field_id = 'storagesheet'

    def fill_dlg(self):
        dlg = self.create_custom(StorageSheet)
        dlg.caption = _("Confirmation")
        icon = XferCompImage('img')
        icon.set_location(0, 0, 1, 6)
        icon.set_value(self.icon_path())
        dlg.add_component(icon)
        lbl = XferCompLabelForm('lb_title')
        lbl.set_value_as_infocenter(_("Do you want validate '%s'?") % self.item)
        lbl.set_location(1, 1)
        dlg.add_component(lbl)
        sel = XferCompSelect('target_area')
        sel.set_needed(True)
        sel.set_select_query(StorageArea.objects.exclude(id=self.item.storagearea_id))
        sel.set_location(1, 2)
        sel.description = _('target area')
        dlg.add_component(sel)
        dlg.add_action(self.get_action(TITLE_OK, 'images/ok.png'), params={"CONFIRME": "YES"})
        dlg.add_action(WrapAction(TITLE_CANCEL, 'images/cancel.png'))

    def fill_confirm(self, transition, trans):
        if (transition == 'valid') and (self.item.sheet_type == 2):
            target_area = self.getparam('target_area', 0)
            if (target_area != 0) and (self.getparam("CONFIRME") is not None):
                self.item.sheet_type = 1
                self.item.save()
                other_storage = self.item.create_oposit(target_area)
                self._confirmed(transition)
                other_storage.valid()
            else:
                self.fill_dlg()
        else:
            XferTransition.fill_confirm(self, transition, trans)


@MenuManage.describ('invoice.change_storagesheet')
@ActionsManage.affect_show(TITLE_PRINT, "images/print.png", condition=lambda xfer: int(xfer.item.status) == 1)
@ActionsManage.affect_grid(TITLE_PRINT, "images/print.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': xfer.getparam('status', -1) == 1)
class StorageSheetPrint(XferPrintAction):
    caption = _("Print storage sheet")
    icon = "report.png"
    model = StorageSheet
    field_id = 'bill'
    action_class = StorageSheetShow
    with_text_export = True


@ActionsManage.affect_grid(TITLE_ADD, "images/add.png", condition=lambda xfer, gridname='': hasattr(xfer.item, 'status') and (xfer.item.status == 0))
@ActionsManage.affect_grid(TITLE_MODIFY, "images/edit.png", unique=SELECT_SINGLE, condition=lambda xfer, gridname='': hasattr(xfer.item, 'status') and (int(xfer.item.status) == 0))
@MenuManage.describ('invoice.add_storagesheet')
class StorageDetailAddModify(XferAddEditor):
    icon = "storagesheet.png"
    model = StorageDetail
    field_id = 'storagedetail'
    caption_add = _("Add storage detail")
    caption_modify = _("Modify storage detail")


@ActionsManage.affect_grid(TITLE_DELETE, "images/delete.png", unique=SELECT_MULTI, condition=lambda xfer, gridname='': hasattr(xfer.item, 'status') and (int(xfer.item.status) == 0))
@MenuManage.describ('invoice.delete_storagesheet')
class StorageDetailDel(XferDelete):
    icon = "storagesheet.png"
    model = StorageDetail
    field_id = 'storagedetail'
    caption = _("Delete storage detail")


@MenuManage.describ('contacts.add_vat')
@ActionsManage.affect_grid(_('Import'), "images/up.png", unique=SELECT_NONE, condition=lambda xfer, gridname='': hasattr(xfer.item, 'status') and (int(xfer.item.status) == 0) and (int(xfer.item.sheet_type) == 0))
class StorageDetailImport(ObjectImport):
    caption = _("Storage detail import")
    icon = "storagesheet.png"
    model = StorageDetail

    def get_select_models(self):
        return StorageDetail.get_select_contact_type(True)

    def _read_csv_and_convert(self):
        fields_description, csv_readed = ObjectImport._read_csv_and_convert(self)
        new_csv_readed = []
        for csv_readed_item in csv_readed:
            csv_readed_item['storagesheet_id'] = self.getparam("storagesheet", 0)
            new_csv_readed.append(csv_readed_item)
        return fields_description, new_csv_readed

    def fillresponse(self, modelname, quotechar="'", delimiter=";", encoding="utf-8", dateformat="%d/%m/%Y", step=0):
        ObjectImport.fillresponse(self, modelname, quotechar, delimiter, encoding, dateformat, step)
        if step != 3:
            self.move(0, 0, 1)
            self.tab = 0
            sheet = StorageSheet.objects.get(id=self.getparam("storagesheet", 0))
            lbl = XferCompLabelForm('sheet')
            lbl.set_value(six.text_type(sheet))
            lbl.set_location(1, 0, 2)
            lbl.description = _('storage sheet')
            self.add_component(lbl)


@MenuManage.describ(right_to_storage, FORMTYPE_NOMODAL, 'storage', _('Situation of storage'))
class StorageSituation(XferListEditor):
    icon = "storagereport.png"
    model = StorageDetail
    field_id = 'storagedetail'
    caption = _("Situation")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.order_list = None

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        if len(self.categories_filter) > 0:
            for cat_item in Category.objects.filter(id__in=self.categories_filter):
                items = items.filter(article__categories__in=[cat_item])
        order_txt = self.getparam(GRID_ORDER + self.field_id, '')
        if order_txt != '':
            self.order_list = order_txt.split(',')
            items = items.order_by(*self.order_list)
        else:
            self.order_list = None
        return items.values('article', 'storagesheet__storagearea').annotate(data_sum=Sum('quantity'))

    def fillresponse_header(self):
        show_storagearea = self.getparam('storagearea', 0)
        self.categories_filter = self.getparam('cat_filter', ())
        ref_filter = self.getparam('ref_filter', '')
        sel_stock = XferCompSelect('storagearea')
        sel_stock.set_needed(False)
        sel_stock.set_select_query(StorageArea.objects.all())
        sel_stock.set_value(show_storagearea)
        sel_stock.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        sel_stock.set_location(0, 4)
        sel_stock.description = StorageArea._meta.verbose_name
        self.add_component(sel_stock)

        edt = XferCompEdit("ref_filter")
        edt.set_value(ref_filter)
        edt.set_location(0, 5)
        edt.is_default = True
        edt.description = _('ref./designation')
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        cat_list = Category.objects.all()
        if len(cat_list) > 0:
            edt = XferCompCheckList("cat_filter")
            edt.set_select_query(cat_list)
            edt.set_value(self.categories_filter)
            edt.set_location(1, 4, 0, 2)
            edt.description = _('categories')
            edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            self.add_component(edt)
        self.filter = Q(storagesheet__status=1)
        if ref_filter != '':
            self.filter &= Q(article__reference__icontains=ref_filter) | Q(article__designation__icontains=ref_filter)
        if show_storagearea != 0:
            self.filter &= Q(storagesheet__storagearea=show_storagearea)

    def fillresponse_body(self):
        grid = XferCompGrid(self.field_id)
        grid.order_list = self.order_list
        grid.add_header("article", Article._meta.verbose_name, 'str', 1)
        grid.add_header("designation", _('designation'), 1)
        grid.add_header('storagesheet__storagearea', _('Area'), 'str', 1)
        grid.add_header('qty', _('Quantity'))
        grid.add_header('amount', _('Amount'))
        grid.add_header('mean', _('Mean price'))
        six.print_(self.items)
        item_id = 0
        total_val = 0.0
        for item in self.get_items_from_filter():
            if item['data_sum'] > 0:
                item_id += 1
                area_id = item['storagesheet__storagearea']
                art = Article.objects.get(id=item['article'])
                format_txt = "%%.%df" % art.qtyDecimal
                qty = float(item['data_sum'])
                amount = float(art.get_amount_from_area(qty, area_id))
                total_val += amount
                grid.set_value(item_id, "article", six.text_type(art))
                grid.set_value(item_id, "designation", six.text_type(art.designation))
                grid.set_value(item_id, 'storagesheet__storagearea', six.text_type(StorageArea.objects.get(id=area_id)))
                grid.set_value(item_id, 'qty', format_txt % qty)
                grid.set_value(item_id, 'amount', format_devise(amount, 5))
                if abs(qty) > 0.0001:
                    grid.set_value(item_id, 'mean', format_devise(amount / qty, 5))
        grid.set_location(0, self.get_max_row() + 1, 2)
        grid.set_size(200, 500)
        self.add_component(grid)

        lbl = XferCompLabelForm("total")
        lbl.set_value(format_devise(total_val, 5))
        lbl.set_location(0, self.get_max_row() + 1, 2)
        lbl.description = _('total amount')
        self.add_component(lbl)

        self.add_action(StorageSituationPrint.get_action(TITLE_PRINT, "images/print.png"), close=CLOSE_NO)
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('invoice.change_storagesheet')
class StorageSituationPrint(XferPrintAction):
    caption = _("Print situation")
    icon = "report.png"
    model = StorageSheet
    field_id = 'storagedetail'
    action_class = StorageSituation
    with_text_export = True


@MenuManage.describ(right_to_storage, FORMTYPE_NOMODAL, 'storage', _('Historic of storage'))
class StorageHistoric(XferListEditor):
    icon = "storagereport.png"
    model = StorageDetail
    field_id = 'storagedetail'
    caption = _("Historic")

    def __init__(self, **kwargs):
        XferListEditor.__init__(self, **kwargs)
        self.fieldnames = ["article", "article.designation", "storagesheet.date", "storagesheet.storagearea",
                           (_('buying price'), "price_txt"), 'quantity']

    def get_items_from_filter(self):
        items = XferListEditor.get_items_from_filter(self)
        if len(self.categories_filter) > 0:
            for cat_item in Category.objects.filter(id__in=self.categories_filter):
                items = items.filter(article__categories__in=[cat_item])
        return items.order_by('-storagesheet__date')

    def fillresponse_header(self):
        date_begin = self.getparam('begin_date', 'NULL')
        date_end = self.getparam('end_date', 'NULL')
        show_storagearea = self.getparam('storagearea', 0)
        self.categories_filter = self.getparam('cat_filter', ())
        ref_filter = self.getparam('ref_filter', '')

        date_init = XferCompDate("begin_date")
        date_init.set_needed(False)
        date_init.set_value(date_begin)
        date_init.set_location(0, 3)
        date_init.description = _('begin date')
        date_init.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_init)
        date_finish = XferCompDate("end_date")
        date_finish.set_needed(False)
        date_finish.set_value(date_end)
        date_finish.set_location(1, 3)
        date_finish.description = _('end date')
        date_finish.set_action(self.request, self.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)
        self.add_component(date_finish)

        sel_stock = XferCompSelect('storagearea')
        sel_stock.set_needed(False)
        sel_stock.set_select_query(StorageArea.objects.all())
        sel_stock.set_value(show_storagearea)
        sel_stock.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        sel_stock.set_location(0, 4)
        sel_stock.description = StorageArea._meta.verbose_name
        self.add_component(sel_stock)

        edt = XferCompEdit("ref_filter")
        edt.set_value(ref_filter)
        edt.set_location(0, 5)
        edt.is_default = True
        edt.description = _('ref./designation')
        edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        self.add_component(edt)

        cat_list = Category.objects.all()
        if len(cat_list) > 0:
            edt = XferCompCheckList("cat_filter")
            edt.set_select_query(cat_list)
            edt.set_value(self.categories_filter)
            edt.set_location(1, 4, 0, 2)
            edt.description = _('categories')
            edt.set_action(self.request, self.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            self.add_component(edt)
        self.filter = Q(storagesheet__status=1)
        if show_storagearea != 0:
            self.filter &= Q(storagesheet__storagearea=show_storagearea)
        if (date_begin is not None) and (date_begin != NULL_VALUE):
            self.filter &= Q(storagesheet__date__gte=date_begin)
        if (date_end is not None) and (date_end != NULL_VALUE):
            self.filter &= Q(storagesheet__date__lte=date_end)
        if ref_filter != '':
            self.filter &= Q(article__reference__icontains=ref_filter) | Q(article__designation__icontains=ref_filter)

    def fillresponse_body(self):
        XferListEditor.fillresponse_body(self)
        self.add_action(StorageHistoricPrint.get_action(TITLE_PRINT, "images/print.png"), close=CLOSE_NO)
        self.add_action(WrapAction(TITLE_CLOSE, 'images/close.png'))


@MenuManage.describ('invoice.change_storagesheet')
class StorageHistoricPrint(XferPrintAction):
    caption = _("Print historic")
    icon = "report.png"
    model = StorageSheet
    field_id = 'storagedetail'
    action_class = StorageHistoric
    with_text_export = True
