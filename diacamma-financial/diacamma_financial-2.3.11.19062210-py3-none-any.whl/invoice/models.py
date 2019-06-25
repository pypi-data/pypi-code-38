# -*- coding: utf-8 -*-
'''
diacamma.invoice models package

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
from re import match
import logging
from os.path import exists, join, dirname

from django.db import models
from django.db.models.aggregates import Max, Sum
from django.db.models.functions import Concat
from django.db.models import Q, Value, F
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils.translation import ugettext_lazy as _
from django.utils.dateformat import DateFormat
from django.utils import six, timezone
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, get_value_if_choices, get_value_converted, get_obj_contains
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.signal_and_lock import Signal
from lucterios.framework.filetools import get_user_path, readimage_to_base64,\
    remove_accent
from lucterios.framework.tools import same_day_months_after
from lucterios.CORE.models import Parameter, SavedCriteria
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import CustomField, CustomizeObject

from diacamma.accounting.models import FiscalYear, Third, EntryAccount, CostAccounting, Journal, EntryLineAccount, ChartsAccount, AccountThird
from diacamma.accounting.tools import current_system_account, format_devise, currency_round, correct_accounting_code
from diacamma.payoff.models import Supporting, Payoff
from datetime import timedelta


class Vat(LucteriosModel):
    name = models.CharField(_('name'), max_length=20)
    rate = models.DecimalField(_('rate'), max_digits=6, decimal_places=2,
                               default=10.0, validators=[MinValueValidator(0.0), MaxValueValidator(99.9)])
    isactif = models.BooleanField(verbose_name=_('is actif'), default=True)
    account = models.CharField(_('vat account'), max_length=50, default='4455')

    def __str__(self):
        return six.text_type(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "rate", "account", "isactif"]

    class Meta(object):
        verbose_name = _('VAT')
        verbose_name_plural = _('VATs')


class Category(LucteriosModel):
    name = models.CharField(_('name'), max_length=50)
    designation = models.TextField(_('designation'))

    def __str__(self):
        return six.text_type(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "designation"]

    class Meta(object):
        verbose_name = _('Category')
        verbose_name_plural = _('Categories')
        default_permissions = []


class StorageArea(LucteriosModel):
    name = models.CharField(_('name'), max_length=50)
    designation = models.TextField(_('designation'))

    def __str__(self):
        return six.text_type(self.name)

    @classmethod
    def get_default_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "designation"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "designation"]

    class Meta(object):
        verbose_name = _('Storage area')
        verbose_name_plural = _('Storage areas')
        default_permissions = []


class ArticleCustomField(LucteriosModel):
    article = models.ForeignKey('Article', verbose_name=_('article'), null=False, on_delete=models.CASCADE)
    field = models.ForeignKey(CustomField, verbose_name=_('field'), null=False, on_delete=models.CASCADE)
    value = models.TextField(_('value'), default="")

    class Meta(object):
        verbose_name = _('custom field value')
        verbose_name_plural = _('custom field values')
        default_permissions = []


class AccountPosting(LucteriosModel):
    name = models.CharField(_('name'), max_length=100, blank=False)
    sell_account = models.CharField(_('sell account'), max_length=50, blank=True)
    cost_accounting = models.ForeignKey(CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name", "sell_account", "cost_accounting"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "sell_account", "cost_accounting"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "sell_account", "cost_accounting"]

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.sell_account = correct_accounting_code(self.sell_account)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('account posting code')
        verbose_name_plural = _('account posting codes')
        default_permissions = []


class Article(LucteriosModel, CustomizeObject):
    CustomFieldClass = ArticleCustomField
    FieldName = 'article'

    reference = models.CharField(_('reference'), max_length=30)
    designation = models.TextField(_('designation'))
    price = models.DecimalField(_('price'), max_digits=10, decimal_places=3,
                                default=0.0, validators=[MinValueValidator(0.0),
                                                         MaxValueValidator(9999999.999)])
    unit = models.CharField(_('unit'), null=True, default='', max_length=10)
    isdisabled = models.BooleanField(verbose_name=_('is disabled'), default=False)
    sell_account = models.CharField(_('sell account'), max_length=50)
    vat = models.ForeignKey(Vat, verbose_name=_('vat'), null=True, default=None, on_delete=models.PROTECT)
    stockable = models.IntegerField(verbose_name=_('stockable'),
                                    choices=((0, _('no stockable')), (1, _('stockable')), (2, _('stockable & no marketable'))), null=False, default=0, db_index=True)
    categories = models.ManyToManyField(Category, verbose_name=_('categories'), blank=True)
    qtyDecimal = models.IntegerField(verbose_name=_('quantity decimal'), default=0, validators=[MinValueValidator(0), MaxValueValidator(3)])
    accountposting = models.ForeignKey(AccountPosting, verbose_name=_('account posting code'), null=True, default=None, on_delete=models.PROTECT)

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.show_storagearea = 0

    def __str__(self):
        return six.text_type(self.reference)

    def get_text_value(self):
        text_value = self.designation.split('{[br/]}')[0]
        if len(text_value) > 50:
            text_value = text_value[:47] + '...'
        stock_txt = ''
        stockage_values = self.get_stockage_values()
        if len(stockage_values) > 0:
            stock_txt = '(%s%s)' % (stockage_values[-1][2], self.unit)
        return "%s | %s %s" % (self.reference, text_value, stock_txt)

    @classmethod
    def get_default_fields(cls):
        fields = []
        if Params.getvalue("invoice-article-with-picture"):
            fields.append((_('image'), 'image'))
        fields.extend(["reference", "designation", (_('price'), "price_txt"), 'unit', "isdisabled", 'accountposting', "stockable"])
        if len(Category.objects.all()) > 0:
            fields.append('categories')
        if len(StorageArea.objects.all()) > 0:
            fields.append((_('quantities'), 'stockage_total'))
        return fields

    @classmethod
    def get_edit_fields(cls):
        fields = {_('001@Description'): ["reference", "designation", ("price", "unit"), ("accountposting", 'vat'), ("stockable", "isdisabled"), ("qtyDecimal",)]}
        if len(Category.objects.all()) > 0:
            fields[_('002@Extra')] = ['categories']
        return fields

    @classmethod
    def get_show_fields(cls):
        fields = {'': ["reference"]}
        fields_desc = ["designation", ("price", "unit"), ("accountposting", 'vat'), ("stockable", "isdisabled"), ("qtyDecimal",)]
        fields_desc.extend(cls.get_fields_to_show())
        if len(Category.objects.all()) > 0:
            fields_desc.append('categories')
        fields[_('001@Description')] = fields_desc
        if len(Provider().third_query) > 0:
            fields[_('002@Provider')] = ['provider_set']
        return fields

    @classmethod
    def get_search_fields(cls):
        fields = ["reference", "designation", "price", "unit", "accountposting", 'vat', "stockable", "isdisabled", "qtyDecimal"]
        for cf_name, cf_model in CustomField.get_fields(cls):
            fields.append((cf_name, cf_model.get_field(), 'articlecustomfield__value', Q(articlecustomfield__field__id=cf_model.id)))
        if len(Category.objects.all()) > 0:
            fields.append('categories.name')
            fields.append('categories.designation')
        if len(Provider().third_query) > 0:
            fields.append('provider_set.third')
            fields.append('provider_set.reference')
        fields.append('storagedetail_set.storagesheet.storagearea')
        return fields

    @classmethod
    def get_import_fields(cls):
        fields = ["reference", "designation", "price", "unit", "accountposting", 'vat', "stockable", "isdisabled", "qtyDecimal"]
        if len(Category.objects.all()) > 0:
            fields.append('categories')
        if len(Provider().third_query) > 0:
            fields.append(('provider.third.contact', _('provider')))
            fields.append('provider.reference')
        for cf_field in CustomField.get_fields(cls):
            fields.append((cf_field[0], cf_field[1].name))
        return fields

    @classmethod
    def import_data(cls, rowdata, dateformat):
        try:
            new_item = super(Article, cls).import_data(rowdata, dateformat)
            if new_item is not None:
                new_item.set_custom_values(rowdata)
                if ('categories' in rowdata.keys()) and (rowdata['categories'] is not None) and (rowdata['categories'] != ''):
                    cat = Category.objects.filter(name__iexact=rowdata['categories']).distinct()
                    if len(cat) > 0:
                        cat_ids = [cat[0].id]
                        for cat_item in new_item.categories.all():
                            cat_ids.append(cat_item.id)
                        new_item.categories.set(Category.objects.filter(id__in=cat_ids).distinct())
                        new_item.save()
                if ('provider.third.contact' in rowdata.keys()) and (rowdata['provider.third.contact'] is not None) and (rowdata['provider.third.contact'] != ''):
                    if ('provider.reference' in rowdata.keys()) and (rowdata['provider.reference'] is not None):
                        reference = rowdata['provider.reference']
                    else:
                        reference = ''
                    q_legalentity = Q(contact__legalentity__name__iexact=rowdata['provider.third.contact'])
                    q_individual = Q(completename__icontains=rowdata['provider.third.contact'])
                    thirds = Third.objects.annotate(completename=Concat('contact__individual__lastname', Value(' '),
                                                                        'contact__individual__firstname')).filter(q_legalentity | q_individual).distinct()
                    if len(thirds) > 0:
                        Provider.objects.get_or_create(article=new_item, third=thirds[0], reference=reference)
            return new_item
        except ValidationError:
            logging.getLogger('lucterios.framwork').exception("import_data")
            raise LucteriosException(GRAVE, "Data error in this line:<br/> %s" % "<br/>".join(get_obj_contains(new_item)))
        except Exception:
            logging.getLogger('diacamma.invoice').exception("import_data")
            raise

    @property
    def image(self):
        img_path = get_user_path("invoice", "Article_%s.jpg" % self.id)
        if exists(img_path):
            img = readimage_to_base64(img_path)
        else:
            img = readimage_to_base64(join(dirname(__file__), "static", 'diacamma.invoice', "images", "NoArticle.png"))
        return img.decode('ascii')

    @property
    def price_txt(self):
        return format_devise(self.price, 5)

    @property
    def ref_price(self):
        return "%s [%s]" % (self.reference, self.price_txt)

    def get_designation(self):
        val = self.designation
        for cf_name, cf_model in CustomField.get_fields(self.__class__):
            val += "{[br/]} - {[u]}%s{[/u]}: {[i]}%s{[/i]}" % (cf_model.name, get_value_converted(getattr(self, cf_name), True))
        return val

    def get_amount_from_area(self, currentqty, area):
        sum_amount = 0.0
        nb_qty = 0.0
        for det_item in self.storagedetail_set.filter(storagesheet__status=1, storagesheet__sheet_type=0, storagesheet__storagearea_id=area).order_by('-storagesheet__date'):
            if (nb_qty + float(det_item.quantity)) < currentqty:
                sum_amount += float(det_item.price * det_item.quantity)
                nb_qty += float(det_item.quantity)
            else:
                sum_amount += float(det_item.price) * (float(currentqty) - nb_qty)
                break
        return sum_amount

    def set_context(self, xfer):
        self.show_storagearea = xfer.getparam('storagearea', 0)

    def get_stockage_values(self):
        stock_list = []
        detail_filter = Q(storagesheet__status=1)
        if self.show_storagearea != 0:
            detail_filter &= Q(storagesheet__storagearea=self.show_storagearea)
        if self.stockable != 0:
            stock = {}
            for val in self.storagedetail_set.filter(detail_filter).values('storagesheet__storagearea').annotate(data_sum=Sum('quantity')):
                if abs(val['data_sum']) > 0.001:
                    if not val['storagesheet__storagearea'] in stock.keys():
                        stock[val['storagesheet__storagearea']] = [six.text_type(StorageArea.objects.get(id=val['storagesheet__storagearea'])), 0.0]
                    stock[val['storagesheet__storagearea']][1] += float(val['data_sum'])
            total_amount = 0.0
            total_qty = 0.0
            for key in sorted(list(stock.keys())):
                sum_amount = self.get_amount_from_area(stock[key][1], key)
                stock_list.append((int(key), stock[key][0], stock[key][1], sum_amount))
                total_qty += stock[key][1]
                total_amount += sum_amount
            stock_list.append((0, _('Total'), total_qty, total_amount))
        return stock_list

    def has_sufficiently(self, storagearea_id, quantity):
        if self.stockable != 0:
            for val in self.get_stockage_values():
                if val[0] == storagearea_id:
                    if (float(quantity) - val[2]) < 0.001:
                        return True
            return False
        return True

    @property
    def stockage_total(self):
        for val in self.get_stockage_values():
            if val[0] == 0:
                format_txt = "%%.%df" % self.qtyDecimal
                return format_txt % float(val[2])
        return None

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        unicity_query = Q(reference=self.reference)
        if self.id is not None:
            unicity_query &= ~Q(id=self.id)
        if (Article.objects.filter(unicity_query).count() != 0):
            raise LucteriosException(IMPORTANT, _("article reference is not unique !"))
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('article')
        verbose_name_plural = _('articles')
        ordering = ['reference']


class Provider(LucteriosModel):
    article = models.ForeignKey(Article, verbose_name=_('article'), null=False, on_delete=models.CASCADE)
    third = models.ForeignKey(Third, verbose_name=_('third'), null=False, on_delete=models.PROTECT)
    reference = models.CharField(_('ref. provider'), max_length=50)

    @property
    def third_query(self):
        thirdfilter = Q(accountthird__code__regex=current_system_account().get_provider_mask())
        return Third.objects.filter(thirdfilter).distinct()

    def __str__(self):
        return self.reference

    @classmethod
    def get_default_fields(cls):
        return ["third", "reference"]

    @classmethod
    def get_edit_fields(cls):
        return ["third", "reference"]

    @classmethod
    def get_show_fields(cls):
        return ["third", "reference"]

    class Meta(object):
        verbose_name = _('Provider')
        verbose_name_plural = _('Providers')
        default_permissions = []


class Bill(Supporting):
    fiscal_year = models.ForeignKey(
        FiscalYear, verbose_name=_('fiscal year'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    bill_type = models.IntegerField(verbose_name=_('bill type'),
                                    choices=((0, _('quotation')), (1, _('bill')), (2, _('asset')), (3, _('receipt'))), null=False, default=0, db_index=True)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    comment = models.TextField(_('comment'), null=False, default="")
    status = FSMIntegerField(verbose_name=_('status'),
                             choices=((0, _('building')), (1, _('valid')), (2, _('cancel')), (3, _('archive'))), null=False, default=0, db_index=True)
    entry = models.ForeignKey(
        EntryAccount, verbose_name=_('entry'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    cost_accounting = models.ForeignKey(
        CostAccounting, verbose_name=_('cost accounting'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    def __str__(self):
        billtype = get_value_if_choices(self.bill_type, self.get_field_by_name('bill_type'))
        if self.num is None:
            return "%s - %s" % (billtype, get_value_converted(self.date))
        else:
            return "%s %s - %s" % (billtype, self.num_txt, get_value_converted(self.date))

    @property
    def reference(self):
        billtype = get_value_if_choices(self.bill_type, self.get_field_by_name('bill_type'))
        if self.num is None:
            return "%s" % billtype
        else:
            return "%s %s" % (billtype, self.num_txt)

    @classmethod
    def get_default_fields(cls, status=-1):
        fields = ["bill_type", (_('numeros'), "num_txt"),
                  "date", "third", "comment", (_('total'), 'total')]
        if status < 0:
            fields.append("status")
        elif status == 1:
            fields.append(Supporting.get_payoff_fields()[-1][-1])
        return fields

    @classmethod
    def get_payment_fields(cls):
        return ["third", ("bill_type", (_('numeros'), "num_txt"),), ("date", (_('total'), 'total'),)]

    def get_third_mask(self):
        return current_system_account().get_customer_mask()

    @classmethod
    def get_edit_fields(cls):
        return ["bill_type", "date", "comment"]

    @classmethod
    def get_search_fields(cls):
        search_fields = ["bill_type", "fiscal_year", "num", "date", "comment", "status"]
        for fieldname in Third.get_search_fields():
            search_fields.append(cls.convert_field_for_search("third", fieldname))
        for fieldname in Detail.get_search_fields():
            search_fields.append(cls.convert_field_for_search("detail_set", fieldname))
        for fieldname in Payoff.get_search_fields():
            search_fields.append(cls.convert_field_for_search("payoff_set", fieldname))
        return search_fields

    @classmethod
    def get_show_fields(cls):
        return [((_('numeros'), "num_txt"), "date"), "third", "detail_set", "comment", ("status", (_('total'), 'total_excltax'))]

    @classmethod
    def get_print_fields(cls):
        print_fields = [
            (_("bill type"), "type_bill"), (_('numeros'), "num_txt"), "date", "third", "detail_set"]
        print_fields.extend(Supporting.get_print_fields())
        print_fields.extend(
            ["comment", "status", (_('total'), 'total_excltax'), (_('VTA sum'), 'vta_sum'), (_('total incl. taxes'), 'total_incltax')])
        print_fields.append('OUR_DETAIL')
        return print_fields

    @property
    def type_bill(self):
        return get_value_if_choices(self.bill_type, self.get_field_by_name("bill_type")).upper()

    @property
    def total(self):
        if Params.getvalue("invoice-vat-mode") == 2:
            return self.total_incltax
        else:
            return self.total_excltax

    def get_current_date(self):
        return self.date

    def get_min_payoff(self, ignore_payoff=-1):
        min_payoff = min(0, self.get_total_rest_topay(ignore_payoff) * 1.5)
        if abs(min_payoff) < 0.00001:
            currency_decimal = Params.getvalue("accounting-devise-prec")
            min_payoff = 1 * 10 ** (-1 * currency_decimal)
        return min_payoff

    def get_max_payoff(self, ignore_payoff=-1):
        max_payoff = max(self.get_total_rest_topay(ignore_payoff) * 1.5, 0)
        if abs(max_payoff) < 0.00001:
            currency_decimal = Params.getvalue("accounting-devise-prec")
            max_payoff = -1 * 10 ** (-1 * currency_decimal)
        return max_payoff

    def get_total_excltax(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_total_excltax()
        return val

    def get_reduce_excltax(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_reduce_excltax()
        return val

    @property
    def total_excltax(self):
        return format_devise(self.get_total_excltax(), 5)

    def get_vta_sum(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_vta()
        return val

    def get_tax_sum(self):
        return self.get_vta_sum()

    @property
    def vta_sum(self):
        return format_devise(self.get_vta_sum(), 5)

    def get_total_incltax(self):
        val = 0
        for detail in self.detail_set.all():
            val += detail.get_total_incltax()
        return val

    def get_total(self):
        return self.get_total_incltax()

    @property
    def total_incltax(self):
        return format_devise(self.get_total_incltax(), 5)

    @property
    def num_txt(self):
        if (self.fiscal_year is None) or (self.num is None):
            return None
        else:
            return "%s-%d" % (self.fiscal_year.letter, self.num)

    def get_vta_details(self):
        vtas = {}
        for detail in self.detail_set.all():
            if abs(detail.vta_rate) > 0.001:
                vta_txt = "%.2f" % abs(float(detail.vta_rate) * 100.0)
                if vta_txt not in vtas.keys():
                    vtas[vta_txt] = float(0.0)
                vtas[vta_txt] += detail.get_vta()
        return vtas

    @property
    def title_vta_details(self):
        vtas = []
        for vta in self.get_vta_details().keys():
            vtas.append(_("VAT %s %%") % vta)
        return "{[br/]}".join(vtas)

    @property
    def vta_details(self):
        vtas = []
        for value in self.get_vta_details().values():
            vtas.append(format_devise(value, 5))
        return "{[br/]}".join(vtas)

    def payoff_is_revenu(self):
        return (self.bill_type != 0) and (self.bill_type != 2)

    def default_date(self):
        return self.date

    def entry_links(self):
        if self.entry_id is not None:
            return [self.entry]
        else:
            return []

    def get_info_state(self):
        info = []
        if self.status == 0:
            info = Supporting.get_info_state(
                self, current_system_account().get_customer_mask())
        details = self.detail_set.all()
        if len(details) == 0:
            info.append(six.text_type(_("no detail")))
        else:
            for detail in details:
                if (detail.article_id is not None) and not detail.article.has_sufficiently(detail.storagearea_id, detail.quantity):
                    info.append(_("Article %s is not sufficiently stocked") % six.text_type(detail.article))
            for detail in details:
                if detail.article is not None:
                    if detail.article.accountposting is None:
                        detail_code = ""
                    else:
                        detail_code = detail.article.accountposting.sell_account
                else:
                    detail_code = Params.getvalue("invoice-default-sell-account")
                detail_account = None
                if match(current_system_account().get_revenue_mask(), detail_code) is not None:
                    try:
                        detail_account = ChartsAccount.get_account(detail_code, FiscalYear.get_current())
                    except LucteriosException:
                        break
                if detail_account is None:
                    info.append(six.text_type(_("article has code account unknown!")))
                    break
        try:
            info.extend(self.check_date(self.date.isoformat()))
        except LucteriosException:
            pass
        return "{[br/]}".join(info)

    def can_delete(self):
        if self.status > 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    def generate_storage(self):
        if self.bill_type == 2:
            sheet_type = 0
        else:
            sheet_type = 1
        old_area = 0
        last_sheet = None
        for detail in self.detail_set.filter(storagearea__isnull=False).order_by('storagearea'):
            if old_area != detail.storagearea_id:
                old_area = detail.storagearea_id
                if last_sheet is not None:
                    last_sheet.valid()
                last_sheet = StorageSheet.objects.create(sheet_type=sheet_type, storagearea_id=old_area, date=self.date, comment=six.text_type(self), status=0)
            if last_sheet is not None:
                StorageDetail.objects.create(storagesheet=last_sheet, article=detail.article, quantity=abs(detail.quantity))
        if last_sheet is not None:
            last_sheet.valid()

    def generate_entry(self):
        if self.bill_type == 2:
            is_bill = -1
        else:
            is_bill = 1
        third_account = self.get_third_account(current_system_account().get_customer_mask(), self.fiscal_year)
        self.entry = EntryAccount.objects.create(year=self.fiscal_year, date_value=self.date, designation=self.__str__(),
                                                 journal=Journal.objects.get(id=3))
        if abs(self.get_total_incltax()) > 0.0001:
            EntryLineAccount.objects.create(account=third_account, amount=is_bill * self.get_total_incltax(), third=self.third, entry=self.entry)
        remise_account = None
        detail_list = {}
        for detail in self.detail_set.all():
            detail_cost = None
            if detail.article is not None:
                if detail.article.accountposting is None:
                    detail_code = ""
                else:
                    detail_code = detail.article.accountposting.sell_account
                    detail_cost = detail.article.accountposting.cost_accounting_id
            else:
                detail_code = Params.getvalue("invoice-default-sell-account")
            detail_account = ChartsAccount.get_account(detail_code, self.fiscal_year)
            if detail_account is None:
                raise LucteriosException(IMPORTANT, _("article has code account unknown!"))
            if (detail_code, detail_cost) not in detail_list.keys():
                detail_list[(detail_code, detail_cost)] = [detail_account, 0, detail_cost]
            detail_list[(detail_code, detail_cost)][1] += detail.get_total_excltax() + detail.get_reduce_excltax()
            if detail.get_reduce_excltax() > 0.001:
                if remise_account is None:
                    remise_code = Params.getvalue("invoice-reduce-account")
                    remise_account = ChartsAccount.get_account(remise_code, self.fiscal_year)
                    if remise_account is None:
                        raise LucteriosException(IMPORTANT, _("reduce-account is not defined!"))
                if (remise_code, detail_cost) not in detail_list.keys():
                    detail_list[(remise_code, detail_cost)] = [remise_account, 0, detail_cost]
                detail_list[(remise_code, detail_cost)][1] -= detail.get_reduce_excltax()
        detail_keys = list(detail_list.keys())
        detail_keys.sort(key=lambda item: "%s__%s" % item)
        for detail_key in detail_keys:
            detail_item = detail_list[detail_key]
            if abs(detail_item[1]) > 0.0001:
                EntryLineAccount.objects.create(account=detail_item[0], amount=is_bill * detail_item[1], entry=self.entry, costaccounting_id=detail_item[2])
        if Params.getvalue("invoice-vat-mode") != 0:
            vat_val = {}
            for detail in self.detail_set.all():
                if (detail.article is not None) and (detail.article.vat is not None):
                    vataccount = detail.article.vat.account
                    if vataccount not in vat_val.keys():
                        vat_val[vataccount] = 0.0
                    vat_val[vataccount] += detail.get_vta()
            for vataccount, vatamount in vat_val.items():
                if vatamount > 0.001:
                    vat_account = ChartsAccount.get_account(vataccount, self.fiscal_year)
                    if vat_account is None:
                        raise LucteriosException(IMPORTANT, _("vta-account is not defined!"))
                    EntryLineAccount.objects.create(account=vat_account, amount=is_bill * vatamount, entry=self.entry, costaccounting=self.cost_accounting)
        no_change, debit_rest, credit_rest = self.entry.serial_control(self.entry.get_serial())
        if not no_change and (len(self.entry.entrylineaccount_set.all()) == 0):
            entry_empty = self.entry
            self.entry = None
            entry_empty.delete()
        elif not no_change or (abs(debit_rest) > 0.001) or (abs(credit_rest) > 0.001):
            raise LucteriosException(GRAVE, _("Error in accounting generator!") + "{[br/]} no_change=%s debit_rest=%.3f credit_rest=%.3f" % (no_change, debit_rest, credit_rest))

    transitionname__valid = _("Validate")

    @transition(field=status, source=0, target=1, conditions=[lambda item:item.get_info_state() == ''])
    def valid(self):
        self.fiscal_year = FiscalYear.get_current()
        bill_list = Bill.objects.filter(Q(bill_type=self.bill_type) & Q(fiscal_year=self.fiscal_year)).exclude(status=0)
        val = bill_list.aggregate(Max('num'))
        if val['num__max'] is None:
            self.num = 1
        else:
            self.num = val['num__max'] + 1
        self.status = 1
        if self.bill_type != 0:
            self.generate_entry()
            self.generate_storage()
        self.save()
        Signal.call_signal("change_bill", 'valid', self, None)

    transitionname__archive = _("Archive")

    @transition(field=status, source=1, target=3)
    def archive(self):
        self.status = 3
        self.save()
        Signal.call_signal("change_bill", 'archive', self, None)

    transitionname__cancel = _("Cancel")

    @transition(field=status, source=1, target=2, conditions=[lambda item:item.bill_type != 2])
    def cancel(self):
        new_asset = None
        if (self.bill_type in (1, 3)):
            new_asset = Bill.objects.create(
                bill_type=2, date=timezone.now(), third=self.third, status=0, cost_accounting=self.cost_accounting)
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_asset
                detail.save()
            self.status = 2
            self.save()
            Signal.call_signal("change_bill", 'cancel', self, new_asset)
        if new_asset is not None:
            return new_asset.id
        else:
            return None

    def convert_to_bill(self):
        if (self.status == 1) and (self.bill_type == 0):
            self.status = 3
            self.save()
            new_bill = Bill.objects.create(bill_type=1, date=timezone.now(), third=self.third, status=0, comment=self.comment)
            cost_accountings = CostAccounting.objects.filter(Q(status=0) & Q(is_default=True))
            if len(cost_accountings) >= 1:
                new_bill.cost_accounting = cost_accountings[0]
                new_bill.save()
            for detail in self.detail_set.all():
                detail.id = None
                detail.bill = new_bill
                detail.save(check_autoreduce=False)
            Signal.call_signal("change_bill", 'convert', self, new_bill)
            return new_bill
        else:
            return None

    def get_statistics_customer(self, without_reduct):
        cust_list = []
        if self.fiscal_year is not None:
            total_cust = 0
            costumers = {}
            for bill in Bill.objects.filter(Q(fiscal_year=self.fiscal_year) & Q(
                    bill_type__in=(1, 2, 3)) & Q(status__in=(1, 3))):
                if bill.third_id not in costumers.keys():
                    costumers[bill.third_id] = 0
                total_excltax = bill.get_total_excltax()
                if without_reduct:
                    total_excltax += bill.get_reduce_excltax()
                if bill.bill_type == 2:
                    costumers[bill.third_id] -= total_excltax
                    total_cust -= total_excltax
                else:
                    costumers[bill.third_id] += total_excltax
                    total_cust += total_excltax
            for cust_id in costumers.keys():
                try:
                    ratio = "%.2f %%" % (100 * costumers[cust_id] / total_cust)
                except ZeroDivisionError:
                    ratio = "---"
                cust_list.append((six.text_type(Third.objects.get(id=cust_id)), format_devise(costumers[cust_id], 5), ratio, costumers[cust_id]))
            cust_list.sort(key=lambda cust_item: (-1 * cust_item[3], cust_item[0]))
            cust_list.append(("{[b]}%s{[/b]}" % _('total'), "{[b]}%s{[/b]}" % format_devise(total_cust, 5), "{[b]}%.2f %%{[/b]}" % 100, total_cust))
        return cust_list

    def get_statistics_article(self, without_reduct):
        art_list = []
        if self.fiscal_year is not None:
            total_art = 0
            articles = {}
            for det in Detail.objects.filter(Q(bill__fiscal_year=self.fiscal_year) & Q(
                    bill__bill_type__in=(1, 2, 3)) & Q(bill__status__in=(1, 3))):
                if det.article_id not in articles.keys():
                    articles[det.article_id] = [0, 0]
                total_excltax = det.get_total_excltax()
                if without_reduct:
                    total_excltax += det.get_reduce_excltax()
                if det.bill.bill_type == 2:
                    articles[det.article_id][0] -= total_excltax
                    articles[det.article_id][1] -= float(det.quantity)
                    total_art -= total_excltax
                else:
                    articles[det.article_id][0] += total_excltax
                    articles[det.article_id][1] += float(det.quantity)
                    total_art += total_excltax
            for art_id in articles.keys():
                if art_id is None:
                    art_text = "---"
                else:
                    art_text = six.text_type(Article.objects.get(id=art_id))
                if abs(articles[art_id][1]) > 0.0001:
                    try:
                        ratio = "%.2f %%" % (100 * articles[art_id][0] / total_art)
                    except ZeroDivisionError:
                        ratio = "---"
                    art_list.append((art_text, format_devise(articles[art_id][0], 5), "%.2f" % articles[art_id][1],
                                     format_devise(articles[art_id][0] / articles[art_id][1], 5), ratio, articles[art_id][0]))
            art_list.sort(key=lambda art_item: art_item[5], reverse=True)
            art_list.append(("{[b]}%s{[/b]}" % _('total'), "{[b]}%s{[/b]}" % format_devise(total_art, 5),
                             "{[b]}---{[/b]}", "{[b]}---{[/b]}", "{[b]}%.2f %%{[/b]}" % 100, total_art))
        return art_list

    def get_statistics_month(self, without_reduct):
        month_list = []
        if self.fiscal_year is not None:
            nb_month = (self.fiscal_year.end.year - self.fiscal_year.begin.year) * 12 + self.fiscal_year.end.month - self.fiscal_year.begin.month + 1
            months = []
            total_month = 0.0
            for current_month in range(nb_month):
                begin_date = same_day_months_after(self.fiscal_year.begin, months=current_month)
                begin_date = begin_date - timedelta(days=begin_date.day - 1)
                end_date = same_day_months_after(begin_date, months=1) - timedelta(days=1)
                amount_sum = 0.0
                for bill in Bill.objects.filter(Q(date__gte=begin_date) & Q(date__lte=end_date) & Q(bill_type__in=(1, 3)) & Q(status__in=(1, 3))):
                    total_excltax = bill.get_total_excltax()
                    if without_reduct:
                        total_excltax += bill.get_reduce_excltax()
                    if bill.bill_type == 2:
                        amount_sum -= total_excltax
                        total_month -= total_excltax
                    else:
                        amount_sum += total_excltax
                        total_month += total_excltax
                months.append((begin_date, amount_sum))
            for begin_date, amount_sum in months:
                try:
                    ratio = "%.2f %%" % (100 * amount_sum / total_month)
                except ZeroDivisionError:
                    ratio = "---"
                month_list.append((DateFormat(begin_date).format('F Y'), format_devise(amount_sum, 5), ratio))
        return month_list

    def support_validated(self, validate_date):
        if (self.bill_type == 2) or (self.status != 1):
            raise LucteriosException(
                IMPORTANT, _("This item can't be validated!"))
        if (self.bill_type == 0):
            new_bill = self.convert_to_bill()
            new_bill.date = validate_date
            new_bill.save()
            if (new_bill is None) or (new_bill.get_info_state() != ''):
                raise LucteriosException(IMPORTANT, _("This item can't be validated!"))
            new_bill.valid()
        else:
            new_bill = self
        return new_bill

    def get_tax(self):
        try:
            return currency_round(self.get_tax_sum() * self.get_total_rest_topay() / self.get_total_incltax())
        except ZeroDivisionError:
            return None

    def get_payable_without_tax(self):
        if (self.bill_type == 2) or (self.status != 1):
            return 0
        else:
            return self.get_total_rest_topay() - self.get_tax()

    def payoff_have_payment(self):
        return (self.bill_type != 2) and (self.status == 1) and (self.get_total_rest_topay() > 0.001)

    def get_document_filename(self):
        billtype = get_value_if_choices(
            self.bill_type, self.get_field_by_name('bill_type'))
        return remove_accent("%s_%s_%s" % (billtype, self.num_txt, six.text_type(self.third)))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        for detail in self.detail_set.all():
            if detail.define_autoreduce():
                detail.save()
        return Supporting.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('bill')
        verbose_name_plural = _('bills')
        ordering = ['-date', 'status']


class Detail(LucteriosModel):
    bill = models.ForeignKey(
        Bill, verbose_name=_('bill'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(
        Article, verbose_name=_('article'), null=True, default=None, db_index=True, on_delete=models.PROTECT)
    designation = models.TextField(verbose_name=_('designation'))
    price = models.DecimalField(verbose_name=_('price'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    unit = models.CharField(
        verbose_name=_('unit'), null=True, default='', max_length=10)
    quantity = models.DecimalField(verbose_name=_('quantity'), max_digits=12, decimal_places=3, default=1.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    reduce = models.DecimalField(verbose_name=_('reduce'), max_digits=10, decimal_places=3, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    vta_rate = models.DecimalField(_('vta rate'), max_digits=6, decimal_places=4, default=0.0, validators=[
        MinValueValidator(0.0), MaxValueValidator(1.0)])
    storagearea = models.ForeignKey(StorageArea, verbose_name=_('storage area'), null=True, default=None, db_index=True, on_delete=models.PROTECT)

    def __init__(self, *args, **kwargs):
        LucteriosModel.__init__(self, *args, **kwargs)
        self.filter_thirdid = 0
        self.filter_ref = ''

    def set_context(self, xfer):
        qty_field = self.get_field_by_name('quantity')
        if self.article_id is not None:
            qty_field.decimal_places = self.article.qtyDecimal
        else:
            qty_field.decimal_places = 3
        self.filter_thirdid = xfer.getparam('third', 0)
        self.filter_ref = xfer.getparam('reference', '')
        self.filter_cat = xfer.getparam('cat_filter', ())
        self.filter_lib = xfer.getparam('ref_filter', '')

    @property
    def article_query(self):
        artfilter = Q(isdisabled=False)
        artfilter &= ~Q(stockable=2)
        if self.filter_thirdid != 0:
            artfilter &= Q(provider__third_id=self.filter_thirdid)
        if self.filter_ref != '':
            artfilter &= Q(provider__reference__icontains=self.filter_ref)
        if self.filter_lib != '':
            artfilter &= Q(reference__icontains=self.filter_lib) | Q(designation__icontains=self.filter_lib)
        items = Article.objects.filter(artfilter).distinct()
        if len(self.filter_cat) > 0:
            for cat_item in Category.objects.filter(id__in=self.filter_cat).distinct():
                items = items.filter(categories__in=[cat_item]).distinct()
        return items

    def __str__(self):
        return "[%s] %s:%s" % (six.text_type(self.article), six.text_type(self.designation), self.price_txt)

    @classmethod
    def get_default_fields(cls):
        return ["article", "designation", (_('price'), "price_txt"), "unit", "quantity", "storagearea", (_('reduce'), "reduce_txt"), (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ["article", "designation", ("price", "reduce"), ("quantity", "unit"), "storagearea"]

    @classmethod
    def get_show_fields(cls):
        return ["article", "designation", (_('price'), "price_txt"), "unit", "quantity", (_('reduce'), "reduce_txt"), "storagearea"]

    @classmethod
    def get_print_fields(cls):
        res = cls.get_default_fields()
        last = res[-1]
        del res[-1]
        res.append((_('reduce amount'), "reduce_amount_txt"))
        res.append((_('reduce ratio'), "reduce_ratio_txt"))
        res.append(last)
        return res

    @classmethod
    def get_search_fields(cls):
        fieldnames = ["designation", "price", "unit", "quantity"]
        for fieldname in Article.get_search_fields():
            fieldnames.append(cls.convert_field_for_search("article", fieldname))
        return fieldnames

    @classmethod
    def create_for_bill(cls, bill, article, qty=1, reduce=0.0, designation=None):
        newdetail = cls(bill=bill, article=article, designation=article.designation if (designation is None) else designation,
                        price=article.price, unit=article.unit, quantity=qty, reduce=reduce)
        newdetail.editor.before_save(None)
        newdetail.save()
        return newdetail

    def get_price(self):
        if (Params.getvalue("invoice-vat-mode") == 2) and (self.vta_rate > 0.001):
            return currency_round(self.price * self.vta_rate)
        if (Params.getvalue("invoice-vat-mode") == 1) and (self.vta_rate < -0.001):
            return currency_round(self.price * -1 * self.vta_rate / (1 - self.vta_rate))
        return float(self.price)

    def get_reduce(self):
        if (Params.getvalue("invoice-vat-mode") == 2) and (self.vta_rate > 0.001):
            return currency_round(self.reduce * self.vta_rate)
        if (Params.getvalue("invoice-vat-mode") == 1) and (self.vta_rate < -0.001):
            return currency_round(self.reduce * -1 * self.vta_rate / (1 - self.vta_rate))
        return float(self.reduce)

    @property
    def price_txt(self):
        return format_devise(self.get_price(), 5)

    @property
    def reduce_amount_txt(self):
        if self.reduce > 0.0001:
            return format_devise(self.get_reduce(), 5)
        else:
            return None

    @property
    def reduce_ratio_txt(self):
        if self.reduce > 0.0001:
            try:
                red_ratio = "%.2f%%" % (100 * self.get_reduce() / (self.get_price() * float(self.quantity)),)
            except ZeroDivisionError:
                red_ratio = ''
            return red_ratio
        else:
            return None

    @property
    def reduce_txt(self):
        if self.reduce > 0.0001:
            if Params.getvalue('invoice-reduce-with-ratio'):
                red_ratio = self.reduce_ratio_txt
                if red_ratio != '':
                    red_ratio = "(%s)" % red_ratio
            else:
                red_ratio = ''
            return "%s%s" % (self.reduce_amount_txt, red_ratio)
        else:
            return None

    @property
    def total(self):
        if Params.getvalue("invoice-vat-mode") == 2:
            return self.total_incltax
        elif Params.getvalue("invoice-vat-mode") == 1:
            return self.total_excltax
        else:
            return format_devise(self.get_total(), 5)

    def get_total(self):
        return currency_round(self.price * self.quantity - self.reduce)

    def get_total_excltax(self):
        if self.vta_rate < -0.001:
            return self.get_total() - self.get_vta()
        else:
            return self.get_total()

    def get_reduce_vat(self):
        if self.vta_rate < -0.001:
            return currency_round(self.reduce * -1 * self.vta_rate / (1 - self.vta_rate))
        elif self.vta_rate > 0.001:
            return currency_round(self.reduce * self.vta_rate)
        else:
            return 0

    def get_reduce_excltax(self):
        if self.vta_rate < -0.001:
            return currency_round(self.reduce) - self.get_reduce_vat()
        else:
            return currency_round(self.reduce)

    @property
    def total_excltax(self):
        return format_devise(self.get_total_excltax(), 5)

    def get_total_incltax(self):
        if self.vta_rate > 0.001:
            return self.get_total() + self.get_vta()
        else:
            return self.get_total()

    @property
    def total_incltax(self):
        return format_devise(self.get_total_incltax(), 5)

    def get_vta(self):
        val = 0
        if self.vta_rate > 0.001:
            val = currency_round(self.price * self.quantity * self.vta_rate)
        elif self.vta_rate < -0.001:
            val = currency_round(
                self.price * self.quantity * -1 * self.vta_rate / (1 - self.vta_rate))
        val -= self.get_reduce_vat()
        return val

    @property
    def price_vta(self):
        return format_devise(self.get_vta(), 5)

    def define_autoreduce(self):
        if (self.bill.third_id is not None) and (self.bill.bill_type in (0, 1, 3)) and (self.bill.status in (0, 1)) and (float(self.reduce) < 0.0001):
            for red_item in AutomaticReduce.objects.all():
                self.reduce = max(float(self.reduce), red_item.calcul_reduce(self))
            return float(self.reduce) > 0.0001
        return False

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None, check_autoreduce=True):
        if check_autoreduce:
            self.define_autoreduce()
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('detail')
        verbose_name_plural = _('details')
        default_permissions = []


class StorageSheet(LucteriosModel):
    sheet_type = models.IntegerField(verbose_name=_('sheet type'),
                                     choices=((0, _('stock receipt')), (1, _('stock exit')), (2, _('stock transfer'))), null=False, default=0, db_index=True)
    date = models.DateField(verbose_name=_('date'), null=False)
    storagearea = models.ForeignKey(StorageArea, verbose_name=_('storage area'), null=False, db_index=True, on_delete=models.PROTECT)
    comment = models.TextField(_('comment'))
    status = FSMIntegerField(verbose_name=_('status'),
                             choices=((0, _('building')), (1, _('valid'))), null=False, default=0, db_index=True)

    provider = models.ForeignKey(Third, verbose_name=_('provider'), null=True, default=None, on_delete=models.PROTECT)
    bill_reference = models.CharField(_('bill reference'), blank=True, max_length=50)
    bill_date = models.DateField(verbose_name=_('bill date'), null=True)

    def __str__(self):
        sheettype = get_value_if_choices(self.sheet_type, self.get_field_by_name('sheet_type'))
        sheetstatus = get_value_if_choices(self.status, self.get_field_by_name('status'))
        return "%s - %s [%s]" % (sheettype, get_value_converted(self.date), sheetstatus)

    @classmethod
    def get_default_fields(cls):
        return ["sheet_type", "status", "date", "storagearea", "comment"]

    @classmethod
    def get_edit_fields(cls):
        return [("sheet_type", ), ("date", "storagearea"), ("provider", "bill_date"), ("bill_reference"), ("comment", )]

    @classmethod
    def get_show_fields(cls):
        return [("sheet_type", "status"), ("date", "storagearea"), ("provider", "bill_date"), ("bill_reference"), ("comment", ), ("storagedetail_set", ), ((_('total amount'), 'total'),)]

    @property
    def provider_query(self):
        thirdfilter = Q(accountthird__code__regex=current_system_account().get_provider_mask())
        return Third.objects.filter(thirdfilter).distinct()

    def can_delete(self):
        if self.status > 0:
            return _('"%s" cannot be deleted!') % six.text_type(self)
        return ''

    @property
    def total(self):
        value = 0.0
        for detail in self.storagedetail_set.all():
            value += float(detail.quantity) * float(detail.price)
        return format_devise(value, 5)

    def get_info_state(self):
        info = []
        for detail in self.storagedetail_set.all():
            if detail.article.stockable == 0:
                info.append(_("Article %s is not stockable") % six.text_type(detail.article))
            elif (self.sheet_type != 0) and not detail.article.has_sufficiently(self.storagearea_id, detail.quantity):
                info.append(_("Article %s is not sufficiently stocked") % six.text_type(detail.article))
        return "{[br/]}".join(info)

    @transition(field=status, source=0, target=1, conditions=[lambda item:item.get_info_state() == ''])
    def valid(self):
        if self.sheet_type == 1:
            for detail in self.storagedetail_set.all():
                detail.quantity = -1 * abs(detail.quantity)
                detail.save()

    def create_oposit(self, target_area):
        other = StorageSheet()
        other.status = 0
        other.date = self.date
        other.comment = self.comment
        other.sheet_type = 0
        other.storagearea_id = target_area
        other.save()
        for detail in self.storagedetail_set.all():
            detail.id = None
            detail.storagesheet_id = other.id
            detail.save()
        return other

    class Meta(object):
        verbose_name = _('storage sheet')
        verbose_name_plural = _('storage sheets')
        ordering = ['-date', 'status']


class StorageDetail(LucteriosModel):
    storagesheet = models.ForeignKey(StorageSheet, verbose_name=_('storage sheet'), null=False, db_index=True, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, verbose_name=_('article'), null=False, db_index=True, on_delete=models.PROTECT)
    price = models.DecimalField(verbose_name=_('buying price'), max_digits=10, decimal_places=3, default=0.0,
                                validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    quantity = models.DecimalField(verbose_name=_('quantity'), max_digits=12, decimal_places=3, default=1.0,
                                   validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])

    def __str__(self):
        return "%s %d" % (self.article_id, self.quantity)

    @classmethod
    def get_default_fields(cls):
        return ["article", (_('buying price'), "price_txt"), (_('quantity'), "quantity_txt")]

    @classmethod
    def get_edit_fields(cls):
        return ["article", "price", "quantity"]

    @classmethod
    def get_show_fields(cls):
        return ["article", (_('buying price'), "price_txt"), (_('quantity'), "quantity_txt")]

    @property
    def price_txt(self):
        if self.quantity > 0:
            return format_devise(self.price, 5)
        else:
            return None

    @property
    def quantity_txt(self):
        if self.article_id is not None:
            format_txt = "%%.%df" % self.article.qtyDecimal
            return format_txt % float(self.quantity)
        else:
            return abs(self.quantity)

    def set_context(self, xfer):
        qty_field = self.get_field_by_name('quantity')
        if self.article_id is not None:
            qty_field.decimal_places = self.article.qtyDecimal
        else:
            qty_field.decimal_places = 3
        self.filter_thirdid = xfer.getparam('third', 0)
        self.filter_ref = xfer.getparam('reference', '')
        self.filter_cat = xfer.getparam('cat_filter', ())
        self.filter_lib = xfer.getparam('ref_filter', '')

    @property
    def article_query(self):
        artfilter = Q(isdisabled=False)
        artfilter &= Q(stockable__in=(1, 2))
        if self.filter_thirdid != 0:
            artfilter &= Q(provider__third_id=self.filter_thirdid)
        if self.filter_ref != '':
            artfilter &= Q(provider__reference__icontains=self.filter_ref)
        if self.filter_lib != '':
            artfilter &= Q(reference__icontains=self.filter_lib) | Q(designation__icontains=self.filter_lib)
        items = Article.objects.filter(artfilter).distinct()
        if len(self.filter_cat) > 0:
            for cat_item in Category.objects.filter(id__in=self.filter_cat).distinct():
                items = items.filter(categories__in=[cat_item]).distinct()
        return items

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (self.storagesheet.status == 0) and (int(self.storagesheet.sheet_type) == 2):
            art = self.article
            art.show_storagearea = self.storagesheet.storagearea_id
            stock_val = art.get_stockage_values()
            if (len(stock_val) > 1) and (stock_val[0][0] == self.storagesheet.storagearea_id):
                self.price = stock_val[0][3] / stock_val[0][2]
            else:
                self.price = 0.0
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('storage detail')
        verbose_name_plural = _('storage details')
        default_permissions = []


class AutomaticReduce(LucteriosModel):
    name = models.CharField(_('name'), max_length=250, blank=False)
    category = models.ForeignKey(Category, verbose_name=_('category'), null=False, on_delete=models.PROTECT)
    mode = models.IntegerField(verbose_name=_('mode'), choices=((0, _('by value')), (1, _('by percentage')), (2, _('by overall percentage sold'))), null=False, default=0)
    amount = models.DecimalField(verbose_name=_('amount'), max_digits=10, decimal_places=3, default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(9999999.999)])
    occurency = models.IntegerField(verbose_name=_('occurency'), default=0, validators=[MinValueValidator(0), MaxValueValidator(1000)])
    filtercriteria = models.ForeignKey(SavedCriteria, verbose_name=_('filter criteria'), null=True, on_delete=models.PROTECT)

    def __str__(self):
        return self.name

    @classmethod
    def get_default_fields(cls):
        return ["name", "category", "mode", (_('amount'), "amount_txt"), "occurency", "filtercriteria"]

    @classmethod
    def get_edit_fields(cls):
        return ["name", "category", "mode", "amount", "occurency", "filtercriteria"]

    @classmethod
    def get_show_fields(cls):
        return ["name", "category", "mode", (_('amount'), "amount_txt"), "occurency", "filtercriteria"]

    @property
    def filtercriteria_query(self):
        return SavedCriteria.objects.filter(modelname=Third.get_long_name())

    def _get_nb_sold(self, reduce_query, detail):
        nb_sold = 0.0
        if self.occurency != 0:
            qty_val = Detail.objects.filter(reduce_query).aggregate(data_sum=Sum('quantity'))
            if qty_val['data_sum'] is not None:
                nb_sold = float(qty_val['data_sum'])
            nb_sold += float(detail.quantity)
        else:
            nb_sold = float(detail.quantity)
            self.occurency = 1
        return nb_sold

    def _reduce_for_mode2(self, reduce_query, detail):
        amount_sold = 0.0
        amount_val = Detail.objects.filter(reduce_query).aggregate(data_sum=Sum(F('quantity') * F('price')))
        if amount_val['data_sum'] is not None:
            amount_sold = float(amount_val['data_sum'])
        reduce_sold = 0.0
        reduce_val = Detail.objects.filter(reduce_query).aggregate(data_sum=Sum('reduce'))
        if reduce_val['data_sum'] is not None:
            reduce_sold = float(reduce_val['data_sum'])
        amount_sold += float(detail.quantity) * float(detail.price)
        return amount_sold * float(self.amount) / 100.0 - reduce_sold

    def check_filtercriteria(self, third_id):
        if self.filtercriteria_id is not None:
            from lucterios.framework.xfersearch import get_search_query_from_criteria
            filter_result, _desc = get_search_query_from_criteria(self.filtercriteria.criteria, Third)
            third_list = Third.objects.filter(filter_result).distinct()
            return third_list.filter(id=third_id).exists()
        return True

    def calcul_reduce(self, detail):
        val_reduce = 0.0
        if (detail.bill.third_id is not None) and (detail.bill.bill_type in (0, 1, 3)) and (detail.bill.status in (0, 1)) and (
                detail.article_id is not None) and self.category.article_set.filter(id=detail.article_id).exists() and self.check_filtercriteria(detail.bill.third_id):
            current_year = FiscalYear.get_current()
            reduce_query = Q(bill__third=detail.bill.third) & Q(article__categories=self.category)
            reduce_query &= (Q(bill__bill_type__in=(1, 3)) & Q(bill__status__in=(0, 1, 3))) | (Q(bill__bill_type=0) & Q(bill__status__in=(0, 1)))
            reduce_query &= Q(bill__date__gte=current_year.begin) & Q(bill__date__lte=current_year.end)
            if detail.id is not None:
                reduce_query &= ~ Q(id=detail.id)
            nb_sold = self._get_nb_sold(reduce_query, detail)
            if self.occurency <= nb_sold:
                qty_reduce = min(float(detail.quantity), nb_sold - self.occurency + 1)
                if self.mode == 0:
                    val_reduce = qty_reduce * float(self.amount)
                elif self.mode == 1:
                    val_reduce = qty_reduce * float(detail.price) * float(self.amount) / 100.0
                else:
                    val_reduce = self._reduce_for_mode2(reduce_query, detail)
        return min(val_reduce, float(detail.quantity) * float(detail.price))

    @property
    def amount_txt(self):
        if self.mode == 0:
            return format_devise(self.amount, 5)
        else:
            return "%.2f%%" % self.amount

    class Meta(object):
        verbose_name = _('automatic reduce')
        verbose_name_plural = _('automatic reduces')
        default_permissions = []


def get_or_create_customer(contact_id):
    try:
        third = Third.objects.get(contact_id=contact_id)
    except ObjectDoesNotExist:
        third = Third.objects.create(
            contact_id=contact_id, status=0)
        AccountThird.objects.create(
            third=third, code=Params.getvalue("invoice-account-third"))
    return third


def convert_articles():
    for art in Article.objects.filter(Q(accountposting__isnull=True) & ~Q(sell_account='')).distinct():
        accout_post, created = AccountPosting.objects.get_or_create(sell_account=art.sell_account)
        if created:
            account = ChartsAccount.get_chart_account(accout_post.sell_account)
            accout_post.name = account.name[:100]
            accout_post.save()
        art.accountposting = accout_post
        art.sell_account = ''
        art.save()


def correct_quotation_asset_account():
    nb_quotation_correct = 0
    nb_asset_correct = 0
    for bill in Bill.objects.filter(Q(bill_type__in=(0, 2)) and Q(entry__close=False)):
        if bill.bill_type == 0:
            corrected = False
            if bill.entry_id is not None:
                entry = bill.entry
                bill.entry = None
                bill.save()
                entry.delete()
                corrected = True
            for payoff in bill.payoff_set.filter(Q(entry__isnull=True) | Q(entry__close=False)):
                payoff.delete()
                corrected = True
            if corrected:
                nb_quotation_correct += 1
        elif bill.bill_type == 2:
            corrected = False
            if not bill.entry.is_asset:
                bill.entry.reverse_entry()
                corrected = True
            for payoff in bill.payoff_set.filter(Q(entry__close=False)):
                if not payoff.entry.is_asset:
                    payoff.entry.reverse_entry()
                    corrected = True
            if corrected:
                nb_asset_correct += 1
    if (nb_quotation_correct > 0) or (nb_asset_correct > 0):
        six.print_(" * account correction assert = %d / quotation = %s" % (nb_asset_correct, nb_quotation_correct))


def convert_asset_and_revenue():
    nb_correct = 0
    for bill in Bill.objects.filter(Q(bill_type__in=(0, 2)) & Q(is_revenu=True)):
        bill.is_revenu = bill.payoff_is_revenu()
        bill.save()
        nb_correct += 1
    if nb_correct > 0:
        six.print_(" * asset & revenue correction = %d" % nb_correct)
        correct_quotation_asset_account()


@Signal.decorate('checkparam')
def invoice_checkparam():
    Parameter.check_and_create(name='invoice-default-sell-account', typeparam=0, title=_("invoice-default-sell-account"),
                               args="{'Multi':False}", value='', meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='invoice-reduce-account', typeparam=0, title=_("invoice-reduce-account"),
                               args="{'Multi':False}", value='', meta='("accounting","ChartsAccount", Q(type_of_account=3) & Q(year__is_actif=True), "code", True)')
    Parameter.check_and_create(name='invoice-vat-mode', typeparam=4, title=_("invoice-vat-mode"),
                               args="{'Enum':3}", value='0', param_titles=(_("invoice-vat-mode.0"), _("invoice-vat-mode.1"), _("invoice-vat-mode.2")))
    Parameter.check_and_create(name="invoice-account-third", typeparam=0, title=_("invoice-account-third"),
                               args="{'Multi':False}", value='',
                               meta='("accounting","ChartsAccount","import diacamma.accounting.tools;django.db.models.Q(code__regex=diacamma.accounting.tools.current_system_account().get_customer_mask()) & django.db.models.Q(year__is_actif=True)", "code", True)')
    convert_articles()
    Parameter.check_and_create(name='invoice-article-with-picture', typeparam=3, title=_("invoice-article-with-picture"), args="{}", value='False')
    Parameter.check_and_create(name='invoice-reduce-with-ratio', typeparam=3, title=_("invoice-reduce-with-ratio"), args="{}", value='True')
    Parameter.check_and_create(name='invoice-reduce-allow-article-empty', typeparam=3, title=_("invoice-reduce-allow-article-empty"), args="{}", value='True')
    convert_asset_and_revenue()
