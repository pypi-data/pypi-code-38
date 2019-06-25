# -*- coding: utf-8 -*-

'''
Describe database model for Django

@author: Laurent GAY
@organization: sd-libre.fr
@contact: info@sd-libre.fr
@license: This file is part of Lucterios.

Lucterios is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals
from datetime import date
from os import unlink

from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils import six

from lucterios.framework.editors import LucteriosEditor
from lucterios.framework.xfercomponents import XferCompLabelForm, XferCompSelect, XferCompCheckList, XferCompGrid, XferCompButton, XferCompEdit,\
    XferCompUpLoad, XferCompImage
from lucterios.framework.tools import CLOSE_NO, FORMTYPE_REFRESH, ActionsManage, FORMTYPE_MODAL
from lucterios.framework.models import get_value_if_choices
from lucterios.framework.filetools import save_from_base64, open_image_resize, get_user_path
from lucterios.CORE.parameters import Params

from diacamma.accounting.tools import current_system_account, format_devise
from diacamma.accounting.models import CostAccounting, FiscalYear, Third
from diacamma.payoff.editors import SupportingEditor
from diacamma.invoice.models import Provider, Category, CustomField, Article


class VatEditor(LucteriosEditor):

    def edit(self, xfer):
        old_account = xfer.get_components("account")
        xfer.tab = old_account.tab
        xfer.remove_component("account")
        sel_code = XferCompSelect("account")
        sel_code.description = old_account.description
        sel_code.set_location(old_account.col, old_account.row, old_account.colspan, old_account.rowspan)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_third_mask()).order_by('code'):
            sel_code.select_list.append((item.code, six.text_type(item)))
        sel_code.set_value(self.item.account)
        xfer.add_component(sel_code)


class AccountPostingEditor(LucteriosEditor):

    def edit(self, xfer):
        old_account = xfer.get_components("sell_account")
        xfer.tab = old_account.tab
        xfer.remove_component("sell_account")
        sel_code = XferCompSelect("sell_account")
        sel_code.description = old_account.description
        sel_code.set_location(old_account.col, old_account.row, old_account.colspan, old_account.rowspan)
        for item in FiscalYear.get_current().chartsaccount_set.all().filter(code__regex=current_system_account().get_revenue_mask()).order_by('code'):
            sel_code.select_list.append((item.code, six.text_type(item)))
        sel_code.set_value(self.item.sell_account)
        xfer.add_component(sel_code)
        comp = xfer.get_components("cost_accounting")
        comp.set_needed(False)
        comp.set_select_query(CostAccounting.objects.filter(Q(status=0) & (Q(year=None) | Q(year=FiscalYear.get_current()))).distinct())


class ArticleEditor(LucteriosEditor):

    def edit(self, xfer):
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        accountposting = xfer.get_components("accountposting")
        CustomField.edit_fields(xfer, accountposting.col)
        if Params.getvalue("invoice-article-with-picture"):
            obj_ref = xfer.get_components('reference')
            xfer.tab = obj_ref.tab
            upload = XferCompUpLoad('uploadlogo')
            upload.set_value('')
            upload.description = _('image')
            upload.add_filter('.jpg')
            upload.add_filter('.gif')
            upload.add_filter('.png')
            upload.add_filter('.bmp')
            upload.set_location(0, xfer.get_max_row() + 1, 2, 1)
            xfer.add_component(upload)

    def saving(self, xfer):
        if Params.getvalue("invoice-article-with-picture"):
            uploadlogo = xfer.getparam('uploadlogo')
            if uploadlogo is not None:
                tmp_file = save_from_base64(uploadlogo)
                with open(tmp_file, "rb") as image_tmp:
                    image = open_image_resize(image_tmp, 100, 100)
                    image = image.convert("RGB")
                    img_path = get_user_path("invoice", "Article_%s.jpg" % self.item.id)
                    with open(img_path, "wb") as image_file:
                        image.save(image_file, 'JPEG', quality=90)
                unlink(tmp_file)
        LucteriosEditor.saving(self, xfer)
        self.item.set_custom_values(xfer.params)

    def show(self, xfer):
        if Params.getvalue("invoice-article-with-picture"):
            obj_ref = xfer.get_components('designation')
            xfer.tab = obj_ref.tab
            new_col = obj_ref.col
            xfer.move(obj_ref.tab, 1, 0)
            img = XferCompImage('logoimg')
            img.set_value(self.item.image)
            img.type = 'jpg'
            img.set_location(new_col, obj_ref.row, 1, 6)
            xfer.add_component(img)
        if self.item.stockable != 0:
            xfer.new_tab(_("Storage"))
            grid = XferCompGrid('storage')
            grid.add_header('area', _('Area'))
            grid.add_header('qty', _('Quantity'))
            grid.add_header('amount', _('Amount'))
            grid.add_header('mean', _('Mean price'))
            grid.set_location(1, 1)
            grid.description = _('quantities')
            format_txt = "%%.%df" % self.item.qtyDecimal
            for area_id, area, qty, amount in self.item.get_stockage_values():
                valformat = "{[b]}%s{[/b]}" if area_id == 0 else "%s"
                grid.set_value(area_id, 'area', valformat % area)
                grid.set_value(area_id, 'qty', valformat % (format_txt % float(qty),))
                grid.set_value(area_id, 'amount', valformat % format_devise(amount, 5))
                if abs(qty) > 0.001:
                    grid.set_value(area_id, 'mean', valformat % format_devise(amount / qty, 5))
            xfer.add_component(grid)

            grid = XferCompGrid('moving')
            grid.set_location(1, 3)
            grid.description = _('moving')
            grid.set_model(self.item.storagedetail_set.filter(storagesheet__status=1).order_by('-storagesheet__date'),
                           ['storagesheet.date', 'storagesheet.comment', 'quantity'], xfer)
            xfer.add_component(grid)
        else:
            xfer.remove_component('provider')
            xfer.del_tab(_('002@Provider'))


class BillEditor(SupportingEditor):

    def edit(self, xfer):
        if xfer.item.id is None:
            xfer.item.status = 0
            xfer.params['status'] = 0
        xfer.move(0, 0, 2)
        xfer.fill_from_model(1, 0, True, ["third"])
        comp_comment = xfer.get_components('comment')
        comp_comment.with_hypertext = True
        comp_comment.set_size(100, 375)
        com_type = xfer.get_components('bill_type')
        com_type.set_action(xfer.request, xfer.get_action(), close=CLOSE_NO, modal=FORMTYPE_REFRESH)

    def show(self, xfer):
        try:
            if xfer.item.cost_accounting is None:
                xfer.remove_component("cost_accounting")
        except ObjectDoesNotExist:
            xfer.remove_component("cost_accounting")
        xfer.params['new_account'] = Params.getvalue('invoice-account-third')
        xfer.move(0, 0, 1)
        lbl = XferCompLabelForm('title')
        lbl.set_location(1, 0, 4)
        lbl.set_value_as_title(get_value_if_choices(
            self.item.bill_type, self.item.get_field_by_name('bill_type')))
        xfer.add_component(lbl)
        details = xfer.get_components('detail')
        if Params.getvalue("invoice-vat-mode") != 0:
            if Params.getvalue("invoice-vat-mode") == 1:
                details.headers[2].descript = _('price excl. taxes')
                details.headers[7].descript = _('total excl. taxes')
            elif Params.getvalue("invoice-vat-mode") == 2:
                details.headers[2].descript = _('price incl. taxes')
                details.headers[7].descript = _('total incl. taxes')
            xfer.get_components('total_excltax').description = _('total excl. taxes')
            xfer.filltab_from_model(1, xfer.get_max_row() + 1, True, [((_('VTA sum'), 'vta_sum'), (_('total incl. taxes'), 'total_incltax'))])
        if self.item.status == 0:
            SupportingEditor.show_third(self, xfer, 'invoice.add_bill')
            xfer.get_components('date').colspan += 1
            xfer.get_components('detail').colspan += 1
        else:
            SupportingEditor.show_third_ex(self, xfer)
            details.actions = []
            if self.item.bill_type != 0:
                SupportingEditor.show(self, xfer)
        return


class DetailFilter(object):

    def refresh_article(self, xfer):
        sel_art = xfer.get_components("article")

        if (sel_art.value == 0) or (sel_art.value is None):
            self.item.article_id = None
            self.item.article = None
        else:
            self.item.article_id = int(sel_art.value)
            self.item.article = Article.objects.get(id=self.item.article_id)
        return sel_art

    def _add_provider_filter(self, xfer, sel_art, init_row):
        old_model = xfer.model
        xfer.model = Provider
        xfer.item = Provider()
        xfer.filltab_from_model(sel_art.col, init_row, False, ['third'])
        xfer.filltab_from_model(sel_art.col + 1, init_row, False, ['reference'])
        xfer.item = self.item
        xfer.model = old_model
        filter_thirdid = xfer.getparam('third', 0)
        filter_ref = xfer.getparam('reference', '')
        sel_third = xfer.get_components("third")
        sel_third.set_needed(False)
        sel_third.set_select_query(Third.objects.filter(provider__isnull=False).distinct())
        sel_third.set_value(filter_thirdid)
        sel_third.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
        sel_third.description = _('provider')
        sel_ref = xfer.get_components("reference")
        sel_ref.set_value(filter_ref)
        sel_ref.set_needed(False)
        sel_ref.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
        if (filter_thirdid != 0) or (filter_ref != ''):
            sel_art.set_needed(True)

    def edit_filter(self, xfer, sel_art):
        init_row = sel_art.row
        xfer.move(sel_art.tab, 0, 10)
        sel_art.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})

        btn = XferCompButton('show_art')
        btn.set_is_mini(True)
        btn.set_location(sel_art.col + sel_art.colspan, sel_art.row)
        btn.set_action(xfer.request, ActionsManage.get_action_url('invoice.Article', 'Show', xfer),
                       modal=FORMTYPE_MODAL, close=CLOSE_NO, params={'article': self.item.article_id})
        xfer.add_component(btn)

        has_filter = False
        cat_list = Category.objects.all()
        if len(cat_list) > 0:
            filter_cat = xfer.getparam('cat_filter', ())
            edt = XferCompCheckList("cat_filter")
            edt.set_select_query(cat_list)
            edt.set_value(filter_cat)
            edt.set_location(sel_art.col, init_row, 2)
            edt.description = _('categories')
            edt.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
            xfer.add_component(edt)
            if (len(filter_cat) > 0) or not Params.getvalue("invoice-reduce-allow-article-empty"):
                sel_art.set_needed(True)
            ref_filter = xfer.getparam('ref_filter', '')
            edt = XferCompEdit("ref_filter")
            edt.set_value(ref_filter)
            edt.set_location(sel_art.col, init_row + 1, 2)
            edt.description = _('ref./designation')
            edt.set_action(xfer.request, xfer.get_action(), modal=FORMTYPE_REFRESH, close=CLOSE_NO, params={'CHANGE_ART': 'YES'})
            xfer.add_component(edt)
            has_filter = True

        if len(Provider.objects.all()) > 0:
            self._add_provider_filter(xfer, sel_art, init_row + 2)
            has_filter = True
        if has_filter:
            lbl = XferCompLabelForm('sep_filter')
            lbl.set_value("{[hr/]}")
            lbl.set_location(sel_art.col, init_row + 9, 2)
            xfer.add_component(lbl)


class DetailEditor(LucteriosEditor, DetailFilter):

    def before_save(self, xfer):
        self.item.vta_rate = 0
        if (Params.getvalue("invoice-vat-mode") != 0) and (self.item.article is not None) and (self.item.article.vat is not None):
            self.item.vta_rate = float(self.item.article.vat.rate / 100)
        if Params.getvalue("invoice-vat-mode") == 2:
            self.item.vta_rate = -1 * self.item.vta_rate
        return

    def edit(self, xfer):
        sel_art = self.refresh_article(xfer)
        currency_decimal = Params.getvalue("accounting-devise-prec")
        xfer.get_components('price').prec = currency_decimal
        xfer.get_components('reduce').prec = currency_decimal
        xfer.get_components('designation').with_hypertext = True

        DetailFilter.edit_filter(self, xfer, sel_art)

        if self.item.article_id is None:
            xfer.remove_component("show_art")
            xfer.get_components('quantity').prec = 3
        else:
            xfer.get_components('quantity').prec = self.item.article.qtyDecimal

        if (self.item.article_id is None) or (self.item.article.stockable == 0):
            xfer.remove_component("storagearea")
            xfer.params['storagearea'] = 0
        else:
            area_list = []
            for val in self.item.article.get_stockage_values():
                if (val[0] != 0) and (abs(val[2]) > 0.0001):
                    format_txt = "%%.%df" % self.item.article.qtyDecimal
                    area_list.append((val[0], "%s [%s]" % (val[1], format_txt % val[2])))
            sel_area = xfer.get_components('storagearea')
            sel_area.set_needed(True)
            sel_area.set_select(area_list)


class StorageSheetEditor(LucteriosEditor):

    def edit(self, xfer):
        if xfer.item.id is None:
            xfer.item.status = 0
            xfer.params['status'] = 0
        sel_type = xfer.get_components("sheet_type")
        sel_type.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
        if int(self.item.sheet_type) != 0:
            xfer.remove_component("provider")
            xfer.remove_component("bill_reference")
            xfer.remove_component("bill_date")
        else:
            sel_provider = xfer.get_components("provider")
            sel_provider.set_action(xfer.request, xfer.get_action('', ''), modal=FORMTYPE_REFRESH, close=CLOSE_NO)
            if (self.item.provider_id is None) or (self.item.provider_id == 0):
                xfer.get_components("bill_reference").value = ""
                xfer.get_components("bill_date").value = None
                xfer.change_to_readonly("bill_reference")
                xfer.change_to_readonly("bill_date")
            else:
                xfer.get_components("bill_reference").set_needed(True)
                bill_date = xfer.get_components("bill_date")
                bill_date.set_needed(True)
                if bill_date.value is None:
                    bill_date.value = date.today()

    def show(self, xfer):
        if int(self.item.sheet_type) != 0:
            xfer.remove_component("provider")
            xfer.remove_component("bill_reference")
            xfer.remove_component("bill_date")
            xfer.remove_component("total")
            storagedetail = xfer.get_components("storagedetail")
            storagedetail.delete_header("price_txt")
        if int(self.item.status) == 0:
            lbl = XferCompLabelForm('info')
            lbl.set_color('red')
            lbl.set_location(1, xfer.get_max_row() + 1, 4)
            lbl.set_value(self.item.get_info_state())
            xfer.add_component(lbl)


class StorageDetailEditor(LucteriosEditor, DetailFilter):

    def edit(self, xfer):
        sel_art = self.refresh_article(xfer)
        if int(self.item.storagesheet.sheet_type) != 0:
            xfer.remove_component("price")
            max_qty = 0
            if self.item.article_id is not None:
                for val in self.item.article.get_stockage_values():
                    if val[0] == self.item.storagesheet.storagearea_id:
                        max_qty = val[2]
                lbl = XferCompLabelForm('max')
                lbl.set_color('blue')
                lbl.set_location(1, xfer.get_max_row() + 1)
                lbl.set_value(max_qty)
                lbl.description = _('max quantity')
                xfer.add_component(lbl)
                xfer.get_components('quantity').max = max_qty
        if self.item.article_id is not None:
            xfer.get_components('quantity').prec = self.item.article.qtyDecimal
        else:
            xfer.get_components('quantity').prec = 3
        DetailFilter.edit_filter(self, xfer, sel_art)
