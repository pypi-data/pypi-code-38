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
(at your option) any later version.

Lucterios is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Lucterios.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import unicode_literals

from datetime import date, timedelta
from os.path import join, isfile
from re import match
from csv import DictReader
from _csv import QUOTE_NONE

from django.db import models
from django.db.models import Q
from django.db.models.query import QuerySet
from django.db.models.aggregates import Sum, Max
from django.template import engines
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import ugettext_lazy as _
from django.utils import six
from django.db.models.signals import pre_save
from django_fsm import FSMIntegerField, transition

from lucterios.framework.models import LucteriosModel, get_value_converted, get_value_if_choices
from lucterios.framework.error import LucteriosException, IMPORTANT, GRAVE
from lucterios.framework.filetools import read_file, xml_validator, save_file, get_user_path
from lucterios.framework.signal_and_lock import RecordLocker, Signal
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.contacts.models import AbstractContact, CustomField, CustomizeObject

from diacamma.accounting.tools import get_amount_sum, format_devise, current_system_account, currency_round, correct_accounting_code
import re


class ThirdCustomField(LucteriosModel):
    third = models.ForeignKey('Third', verbose_name=_('third'), null=False, on_delete=models.CASCADE)
    field = models.ForeignKey(CustomField, verbose_name=_('field'), null=False, on_delete=models.CASCADE)
    value = models.TextField(_('value'), default="")

    class Meta(object):
        verbose_name = _('custom field value')
        verbose_name_plural = _('custom field values')
        default_permissions = []


class Third(LucteriosModel, CustomizeObject):
    CustomFieldClass = ThirdCustomField
    FieldName = 'third'

    contact = models.ForeignKey('contacts.AbstractContact', verbose_name=_('contact'), null=False, on_delete=models.CASCADE)
    status = FSMIntegerField(verbose_name=_('status'), choices=((0, _('Enable')), (1, _('Disable'))))

    def __str__(self):
        return six.text_type(self.contact.get_final_child())

    @classmethod
    def get_default_fields(cls):
        return ["contact", "accountthird_set"]

    @classmethod
    def get_other_fields(cls):
        return ["contact", "accountthird_set", (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        result = []
        return result

    @classmethod
    def get_show_fields(cls):
        fields_desc = ["status", "accountthird_set", ((_('total'), 'total'),)]
        fields_desc.extend(cls.get_fields_to_show())
        return {'': ['contact'], _('001@AccountThird information'): fields_desc}

    @classmethod
    def get_print_fields(cls):
        fields_desc = cls.get_other_fields()
        for custom_fields in cls.get_fields_to_show():
            for custom_field in custom_fields:
                fields_desc.append(custom_field)
        return fields_desc

    @classmethod
    def get_search_fields(cls):
        result = []
        for field_name in AbstractContact.get_search_fields():
            result.append(cls.convert_field_for_search('contact', field_name))
        for cf_name, cf_model in CustomField.get_fields(cls):
            result.append((cf_name, cf_model.get_field(), 'thirdcustomfield__value', Q(thirdcustomfield__field__id=cf_model.id)))
        result.extend(["status", "accountthird_set.code"])
        return result

    def get_total(self, current_date=None, strict=True):
        current_filter = Q(third=self)
        if current_date is not None:
            if strict:
                current_filter &= Q(entry__date_value__lte=current_date)
            else:
                current_filter &= Q(entry__date_value__lt=current_date)
        active_sum = get_amount_sum(EntryLineAccount.objects.filter(current_filter & Q(account__type_of_account=0)).aggregate(Sum('amount')))
        passive_sum = get_amount_sum(EntryLineAccount.objects.filter(current_filter & Q(account__type_of_account=1)).aggregate(Sum('amount')))
        other_sum = get_amount_sum(EntryLineAccount.objects.filter(current_filter & Q(account__type_of_account__gt=1)).aggregate(Sum('amount')))
        return passive_sum - active_sum + other_sum

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    def merge_objects(self, alias_objects=[]):
        LucteriosModel.merge_objects(self, alias_objects=alias_objects)
        last_code = []
        for sub_account in self.accountthird_set.all():
            if sub_account.code in last_code:
                sub_account.delete()
            else:
                last_code.append(sub_account.code)

    transitionname__disabled = _('Disabled')

    @transition(field=status, source=0, target=1)
    def disabled(self):
        pass

    transitionname__enabled = _("Enabled")

    @transition(field=status, source=1, target=0)
    def enabled(self):
        pass

    def get_account(self, fiscal_year, mask):
        accounts = self.accountthird_set.filter(code__regex=mask)
        if len(accounts) == 0:
            raise LucteriosException(IMPORTANT, _("third has not correct account"))
        third_account = ChartsAccount.get_account(accounts[0].code, fiscal_year)
        if third_account is None:
            raise LucteriosException(IMPORTANT, _("third has not correct account"))
        return third_account

    class Meta(object):
        verbose_name = _('third')
        verbose_name_plural = _('thirds')


class AccountThird(LucteriosModel):
    third = models.ForeignKey(
        Third, verbose_name=_('third'), null=False, on_delete=models.CASCADE)
    code = models.CharField(_('code'), max_length=50)

    def __str__(self):
        return self.code

    def can_delete(self):
        if self.total > 0.0001:
            return _('This account is not nul!')
        else:
            return ''

    @classmethod
    def get_default_fields(cls):
        return ["code", (_('total'), 'total_txt')]

    @classmethod
    def get_edit_fields(cls):
        return ["code"]

    @property
    def current_charts(self):
        try:
            return ChartsAccount.objects.get(code=self.code, year=FiscalYear.get_current())
        except (ObjectDoesNotExist, LucteriosException):
            return None

    @property
    def total_txt(self):
        chart = self.current_charts
        if chart is not None:
            return format_devise(chart.credit_debit_way() * self.total, 2)
        else:
            return format_devise(0, 2)

    @property
    def total(self):
        return get_amount_sum(EntryLineAccount.objects.filter(third=self.third, account__code=self.code).aggregate(Sum('amount')))

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = correct_accounting_code(self.code)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('account')
        verbose_name_plural = _('accounts')
        default_permissions = []


class FiscalYear(LucteriosModel):
    begin = models.DateField(verbose_name=_('begin'))
    end = models.DateField(verbose_name=_('end'))
    status = models.IntegerField(verbose_name=_('status'), choices=((0, _('building')), (1, _('running')), (2, _('finished'))), default=0)
    is_actif = models.BooleanField(verbose_name=_('actif'), default=False, db_index=True)
    last_fiscalyear = models.ForeignKey('FiscalYear', verbose_name=_(
        'last fiscal year'), related_name='next_fiscalyear', null=True, on_delete=models.SET_NULL)

    def init_dates(self):
        fiscal_years = FiscalYear.objects.order_by('end')
        if len(fiscal_years) == 0:
            self.begin = date.today()
        else:
            last_fiscal_year = fiscal_years[len(fiscal_years) - 1]
            self.begin = last_fiscal_year.end + timedelta(days=1)
        try:
            self.end = date(self.begin.year + 1, self.begin.month, self.begin.day) - timedelta(days=1)
        except ValueError:
            self.end = date(self.begin.year + 1, self.begin.month, self.begin.day - 1)

    def can_delete(self):
        fiscal_years = FiscalYear.objects.order_by('end')
        if (len(fiscal_years) != 0) and (fiscal_years[len(fiscal_years) - 1].id != self.id):
            return _('This fiscal year is not the last!')
        elif self.status == 2:
            return _('Fiscal year finished!')
        else:
            return ''

    def delete(self, using=None):
        self.entryaccount_set.all().delete()
        LucteriosModel.delete(self, using=using)

    def set_has_actif(self):
        EntryAccount.clear_ghost()
        all_year = FiscalYear.objects.all()
        for year_item in all_year:
            year_item.is_actif = False
            year_item.save()
        self.is_actif = True
        self.save()

    @classmethod
    def get_default_fields(cls):
        return ['begin', 'end', 'status', 'is_actif']

    @classmethod
    def get_edit_fields(cls):
        return ['status', 'begin', 'end']

    @property
    def total_revenue(self):
        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=3, account__year=self,
                                                              entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_expense(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=4, account__year=self,
                                                              entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_cash(self):

        return get_amount_sum(EntryLineAccount.objects.filter(account__code__regex=current_system_account().get_cash_mask(),
                                                              account__year=self, entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_cash_close(self):

        return get_amount_sum(EntryLineAccount.objects.filter(entry__close=True, account__code__regex=current_system_account().get_cash_mask(),
                                                              account__year=self, entry__date_value__gte=self.begin, entry__date_value__lte=self.end).aggregate(Sum('amount')))

    @property
    def total_result_text(self):
        value = {}
        value['revenue'] = format_devise(self.total_revenue, 5)
        value['expense'] = format_devise(self.total_expense, 5)
        value['result'] = format_devise(
            self.total_revenue - self.total_expense, 5)
        value['cash'] = format_devise(self.total_cash, 5)
        value['closed'] = format_devise(self.total_cash_close, 5)
        res_text = _(
            '{[b]}Revenue:{[/b]} %(revenue)s - {[b]}Expense:{[/b]} %(expense)s = {[b]}Result:{[/b]} %(result)s{[br/]}{[b]}Cash:{[/b]} %(cash)s - {[b]}Closed:{[/b]} %(closed)s')
        return res_text % value

    @property
    def has_no_lastyear_entry(self):
        val = get_amount_sum(EntryLineAccount.objects.filter(entry__journal__id=1, account__year=self).aggregate(Sum('amount')))
        return abs(val) < 0.0001

    def import_charts_accounts(self):
        if self.last_fiscalyear is None:
            raise LucteriosException(
                IMPORTANT, _("This fiscal year has not a last fiscal year!"))
        if self.status == 2:
            raise LucteriosException(IMPORTANT, _('Fiscal year finished!'))
        for last_charts_account in self.last_fiscalyear.chartsaccount_set.all():
            try:
                self.chartsaccount_set.get(
                    code=correct_accounting_code(last_charts_account.code))
            except ObjectDoesNotExist:
                ChartsAccount.objects.create(year=self, code=last_charts_account.code, name=last_charts_account.name,
                                             type_of_account=last_charts_account.type_of_account)

    def run_report_lastyear(self, import_result):
        if self.last_fiscalyear is None:
            raise LucteriosException(IMPORTANT, _("This fiscal year has not a last fiscal year!"))
        if self.status != 0:
            raise LucteriosException(IMPORTANT, _("This fiscal year is not 'in building'!"))
        current_system_account().import_lastyear(self, import_result)

    def getorcreate_chartaccount(self, code, name=None):
        code = correct_accounting_code(code)
        try:
            return self.chartsaccount_set.get(code=code)
        except ObjectDoesNotExist:
            descript, typeaccount = current_system_account().new_charts_account(
                code)
            if name is None:
                name = descript
            return ChartsAccount.objects.create(year=self, code=code, name=name, type_of_account=typeaccount)

    def move_entry_noclose(self):
        if self.status == 1:
            next_ficalyear = None
            for entry_noclose in EntryAccount.objects.filter(close=False, entrylineaccount__account__year=self).distinct():
                if next_ficalyear is None:
                    try:
                        next_ficalyear = FiscalYear.objects.get(
                            last_fiscalyear=self)
                    except BaseException:
                        raise LucteriosException(IMPORTANT, _(
                            "This fiscal year has entries not closed and not next fiscal year!"))
                for entryline in entry_noclose.entrylineaccount_set.all():
                    entryline.account = next_ficalyear.getorcreate_chartaccount(
                        entryline.account.code, entryline.account.name)
                    entryline.save()
                entry_noclose.year = next_ficalyear
                entry_noclose.date_value = next_ficalyear.begin
                entry_noclose.save()

    @classmethod
    def get_current(cls, select_year=None):
        if select_year is None:
            try:
                year = FiscalYear.objects.get(
                    is_actif=True)
            except ObjectDoesNotExist:
                raise LucteriosException(
                    IMPORTANT, _('No fiscal year define!'))
        else:
            year = FiscalYear.objects.get(
                id=select_year)
        return year

    def get_account_list(self, num_cpt_txt, num_cpt):
        account_list = []
        first_account = None
        current_account = None
        for account in self.chartsaccount_set.all().filter(code__startswith=num_cpt_txt).order_by('code'):
            account_list.append((account.id, six.text_type(account)))
            if first_account is None:
                first_account = account
            if account.id == num_cpt:
                current_account = account
        if current_account is None:
            current_account = first_account

        return account_list, current_account

    def get_context(self):
        entries_by_journal = []
        for journal in Journal.objects.all():
            entries = self.entryaccount_set.filter(journal=journal, close=True)
            if len(entries) > 0:
                entries_by_journal.append((journal, entries))
        if len(entries_by_journal) == 0:
            raise LucteriosException(IMPORTANT, _('This fiscal year has no validated entrie !'))
        return {'year': self, 'entries_by_journal': entries_by_journal}

    def get_xml_export(self):
        file_name = "fiscalyear_export_%s.xml" % six.text_type(self.id)
        xmlfiles = current_system_account().get_export_xmlfiles()
        if xmlfiles is None:
            raise LucteriosException(IMPORTANT, _('No export for this accounting system!'))
        xml_file, xsd_file = xmlfiles
        template = engines['django'].from_string(read_file(xml_file).decode('utf-8'))
        fiscal_year_xml = six.text_type(template.render(self.get_context()))
        res_val = xml_validator(fiscal_year_xml, xsd_file)
        if res_val is not None:
            raise LucteriosException(GRAVE, res_val)
        save_file(get_user_path("accounting", file_name), fiscal_year_xml)
        return join("accounting", file_name)

    def get_identify(self):
        if self.begin.year != self.end.year:
            return "%d/%d" % (self.begin.year, self.end.year)
        else:
            return six.text_type(self.begin.year)

    def __str__(self):
        status = get_value_if_choices(self.status, self._meta.get_field(
            'status'))
        return _("Fiscal year from %(begin)s to %(end)s [%(status)s]") % {'begin': get_value_converted(self.begin), 'end': get_value_converted(self.end), 'status': status}

    @property
    def letter(self):
        nb_year = FiscalYear.objects.filter(id__lt=self.id).count()
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        res = ''
        while nb_year >= 26:
            div, mod = divmod(nb_year, 26)
            res = letters[mod] + res
            nb_year = int(div) - 1
        return letters[nb_year] + res

    def _check_annexe(self):
        total = 0
        for chart in self.chartsaccount_set.filter(type_of_account=5):
            total += chart.get_current_total()
        if abs(total) > 0.0001:
            raise LucteriosException(IMPORTANT, _("The sum of annexe account must be null!"))

    def check_to_close(self):
        if self.status == 0:
            raise LucteriosException(IMPORTANT, _("This fiscal year is not 'in running'!"))
        EntryAccount.clear_ghost()
        self._check_annexe()
        nb_entry_noclose = EntryAccount.objects.filter(close=False, entrylineaccount__account__year=self).distinct().count()
        if (nb_entry_noclose > 0) and (FiscalYear.objects.filter(last_fiscalyear=self).count() == 0):
            raise LucteriosException(IMPORTANT, _("This fiscal year has entries not closed and not next fiscal year!"))
        return nb_entry_noclose

    def closed(self):
        for cost in CostAccounting.objects.filter(year=self):
            cost.close()
        self._check_annexe()
        self.move_entry_noclose()
        current_system_account().finalize_year(self)
        self.status = 2
        self.save()

    class Meta(object):
        verbose_name = _('fiscal year')
        verbose_name_plural = _('fiscal years')


class CostAccounting(LucteriosModel):
    name = models.CharField(_('name'), max_length=150, unique=True)
    description = models.CharField(_('description'), max_length=200)
    status = models.IntegerField(verbose_name=_('status'), choices=((0, _('opened')), (1, _('closed'))), default=0)
    last_costaccounting = models.ForeignKey('CostAccounting', verbose_name=_(
        'last cost accounting'), related_name='next_costaccounting', null=True, on_delete=models.SET_NULL)
    is_default = models.BooleanField(verbose_name=_('default'), default=False)
    is_protected = models.BooleanField(verbose_name=_('default'), default=False)
    year = models.ForeignKey('FiscalYear', verbose_name=_('fiscal year'), null=True, default=None, on_delete=models.PROTECT, db_index=True)

    def __str__(self):
        return self.name

    def can_delete(self):
        if self.status == 2:
            return _('This cost accounting is closed!')
        if self.is_protected:
            return _("This cost accounting is protected by other modules!")
        return ""

    @classmethod
    def get_default_fields(cls):
        return ['name', 'description', 'year', (_('total revenue'), 'total_revenue'), (_('total expense'), 'total_expense'), (_('result'), 'total_result'), 'status', 'is_default']

    @classmethod
    def get_edit_fields(cls):
        return ['name', 'description', 'year', 'last_costaccounting']

    @property
    def total_revenue(self):
        return format_devise(self.get_total_revenue(), 5)

    def get_total_revenue(self):
        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=3, costaccounting=self).aggregate(Sum('amount')))

    @property
    def total_expense(self):
        return format_devise(self.get_total_expense(), 5)

    def get_total_expense(self):
        return get_amount_sum(EntryLineAccount.objects.filter(account__type_of_account=4, costaccounting=self).aggregate(Sum('amount')))

    @property
    def total_result(self):
        return format_devise(self.get_total_revenue() - self.get_total_expense(), 5)

    def close(self):
        self.check_before_close()
        self.is_default = False
        self.status = 1
        self.save()

    def change_has_default(self):
        if self.status == 0:
            if self.is_default:
                self.is_default = False
                self.save()
            else:
                all_cost = CostAccounting.objects.all()
                for cost_item in all_cost:
                    cost_item.is_default = False
                    cost_item.save()
                self.is_default = True
                self.save()

    def check_before_close(self):
        EntryAccount.clear_ghost()
        if self.entrylineaccount_set.filter(entry__close=False).count() > 0:
            raise LucteriosException(IMPORTANT, _('The cost accounting "%s" has some not validated entry!') % self)
        if self.modelentry_set.all().count() > 0:
            raise LucteriosException(IMPORTANT, _('The cost accounting "%s" is include in a model of entry!') % self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (self.id is not None) and (self.year is not None):
            entries = EntryAccount.objects.filter(entrylineaccount__costaccounting=self).exclude(year=self.year)
            if len(entries) > 0:
                raise LucteriosException(IMPORTANT, _('This cost accounting have entry with another year!'))
        res = LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)
        for budget_item in self.budget_set.all():
            budget_item.year = self.year
            budget_item.save()
        return res

    class Meta(object):
        verbose_name = _('cost accounting')
        verbose_name_plural = _('costs accounting')
        default_permissions = []
        ordering = ['name']


class ChartsAccount(LucteriosModel):
    code = models.CharField(_('code'), max_length=50, db_index=True)
    name = models.CharField(_('name'), max_length=200)
    year = models.ForeignKey('FiscalYear', verbose_name=_('fiscal year'), null=False, on_delete=models.CASCADE, db_index=True)
    type_of_account = models.IntegerField(verbose_name=_('type of account'),
                                          choices=((0, _('Asset')), (1, _('Liability')), (2, _('Equity')), (3, _('Revenue')), (4, _('Expense')), (5, _('Contra-accounts'))), null=True, db_index=True)

    @classmethod
    def get_default_fields(cls):
        return ['code', 'name', (_('total of last year'), 'last_year_total'),
                (_('total current'), 'current_total'), (_('total validated'), 'current_validated')]

    @classmethod
    def get_edit_fields(cls):
        return ['code', 'name', 'type_of_account']

    @classmethod
    def get_show_fields(cls):
        return ['code', 'name', 'type_of_account']

    @classmethod
    def get_print_fields(cls):
        return ['code', 'name', (_('total of last year'), 'last_year_total'),
                (_('total current'), 'current_total'), (_('total validated'), 'current_validated'), 'entrylineaccount_set']

    def __str__(self):
        return "[%s] %s" % (self.code, self.name)

    def get_name(self):
        return "[%s] %s" % (correct_accounting_code(self.code), self.name)

    def get_last_year_total(self):
        return get_amount_sum(self.entrylineaccount_set.filter(entry__journal__id=1).aggregate(Sum('amount')))

    def get_current_total(self):
        return get_amount_sum(self.entrylineaccount_set.all().aggregate(Sum('amount')))

    def get_current_validated(self):
        return get_amount_sum(self.entrylineaccount_set.filter(entry__close=True).aggregate(Sum('amount')))

    def credit_debit_way(self):
        if self.type_of_account in [0, 4]:
            return -1
        else:
            return 1

    @property
    def last_year_total(self):
        return format_devise(self.credit_debit_way() * self.get_last_year_total(), 2)

    @property
    def current_total(self):
        return format_devise(self.credit_debit_way() * self.get_current_total(), 2)

    @property
    def current_validated(self):
        return format_devise(self.credit_debit_way() * self.get_current_validated(), 2)

    @property
    def is_third(self):
        return match(current_system_account().get_third_mask(), self.code) is not None

    @property
    def is_cash(self):
        return match(current_system_account().get_cash_mask(), self.code) is not None

    @classmethod
    def get_account(cls, code, year):
        accounts = ChartsAccount.objects.filter(year=year, code=code)
        if len(accounts) == 0:
            return None
        else:
            return accounts[0]

    @classmethod
    def get_chart_account(cls, code):
        current_year = FiscalYear.get_current()
        code = correct_accounting_code(code)
        try:
            chart = current_year.chartsaccount_set.get(code=code)
        except ObjectDoesNotExist:
            descript, typeaccount = current_system_account().new_charts_account(code)
            chart = ChartsAccount(year=current_year, code=code, name=descript, type_of_account=typeaccount)
        return chart

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        try:
            self.code = correct_accounting_code(self.code)
            exist_account = ChartsAccount.objects.get(
                code=self.code, year=self.year)
            if exist_account.id != self.id:
                raise LucteriosException(
                    IMPORTANT, _('Account already exists for this fiscal year!'))
        except ObjectDoesNotExist:
            pass
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    @classmethod
    def import_initial(cls, year, account_item):
        if isfile(account_item):
            with open(account_item, 'r', encoding='UTF-8') as fcsv:
                csv_read = DictReader(fcsv, delimiter=';', quotechar='', quoting=QUOTE_NONE)
                for row in csv_read:
                    new_code = correct_accounting_code(row['code'])
                    if cls.get_account(new_code, year) is None:
                        account_desc = current_system_account().new_charts_account(new_code)
                        if account_desc[1] >= 0:
                            ChartsAccount.objects.create(year=year, code=new_code, name=row['name'], type_of_account=account_desc[1])

    class Meta(object):
        verbose_name = _('charts of account')
        verbose_name_plural = _('charts of accounts')
        ordering = ['year', 'code']


class Journal(LucteriosModel):
    name = models.CharField(_('name'), max_length=50, unique=True)

    def __str__(self):
        return self.name

    def can_delete(self):
        if self.id in [1, 2, 3, 4, 5]:
            return _('journal reserved!')
        else:
            return ''

    @classmethod
    def get_default_fields(cls):
        return ["name"]

    class Meta(object):

        verbose_name = _('accounting journal')
        verbose_name_plural = _('accounting journals')
        default_permissions = []


class AccountLink(LucteriosModel):
    def __str__(self):
        return self.letter

    @property
    def letter(self):
        year = self.entrylineaccount_set.all()[0].entry.year
        nb_link = AccountLink.objects.filter(entrylineaccount__entry__year=year, id__lt=self.id).count()
        letters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        res = ''
        while nb_link >= 26:
            div, mod = divmod(nb_link, 26)
            res = letters[mod] + res
            nb_link = int(div) - 1
        return letters[nb_link] + res

    def is_validity(self):
        third_info = None
        sum_amount = 0.0
        entrylines = self.entrylineaccount_set.all()
        is_valid = len(entrylines) > 0
        for entryline in entrylines:
            if third_info is None:
                third_info = (entryline.account.code, entryline.third_id)
            elif (third_info[0] != entryline.account.code) or (third_info[1] != entryline.third_id):
                is_valid = False
            sum_amount += float(entryline.amount)
        if abs(sum_amount) > 0.0001:
            is_valid = False
        return is_valid

    def check_validity(self):
        if not self.is_validity():
            self.delete()

    @classmethod
    def create_link(cls, entrylines, check_year=True):
        regex_third = re.compile(current_system_account().get_third_mask())
        year = None
        third_info = None
        sum_amount = 0.0
        for entryline in entrylines:
            entryline = EntryLineAccount.objects.get(id=entryline.id)
            if regex_third.match(entryline.account.code) is None:
                raise LucteriosException(IMPORTANT, _("An entry line is not third!"))
            # if check_year and (entryline.entry.year.status == 2):
            #    raise LucteriosException(IMPORTANT, _("Fiscal year finished!"))
            if year is None:
                year = entryline.entry.year
            elif year != entryline.entry.year:
                raise LucteriosException(IMPORTANT, _("This entries are not in same fiscal year!"))
            if third_info is None:
                third_info = (entryline.account.code, entryline.third_id)
            elif (third_info[0] != entryline.account.code) or (third_info[1] != entryline.third_id):
                raise LucteriosException(IMPORTANT, _("This entry lines are not in same third!"))
            sum_amount += float(entryline.amount)
            entryline.unlink()
        if abs(sum_amount) > 0.0001:
            raise LucteriosException(IMPORTANT, _("The input lines are not balanced!"))
        for entryline in entrylines:
            entryline = EntryLineAccount.objects.get(id=entryline.id)
            entryline.unlink()
        new_link = AccountLink.objects.create()
        for entryline in entrylines:
            entryline.link = new_link
            entryline.save()

    class Meta(object):

        verbose_name = _('letter')
        verbose_name_plural = _('letters')
        default_permissions = []


class EntryAccount(LucteriosModel):
    year = models.ForeignKey('FiscalYear', verbose_name=_('fiscal year'), null=False, on_delete=models.CASCADE)
    num = models.IntegerField(verbose_name=_('numeros'), null=True)
    journal = models.ForeignKey('Journal', verbose_name=_('journal'), null=False, default=0, on_delete=models.PROTECT)
    link = models.ForeignKey('AccountLink', verbose_name=_('link'), null=True, on_delete=models.SET_NULL)
    date_entry = models.DateField(verbose_name=_('date entry'), null=True)
    date_value = models.DateField(verbose_name=_('date value'), null=False, db_index=True)
    designation = models.CharField(_('name'), max_length=200)
    costaccounting = models.ForeignKey('CostAccounting', verbose_name=_('cost accounting'), null=True, on_delete=models.PROTECT)
    close = models.BooleanField(verbose_name=_('close'), default=False, db_index=True)

    @classmethod
    def get_default_fields(cls):
        return ['num', 'date_entry', 'date_value', (_('description'), 'description')]

    @classmethod
    def get_edit_fields(cls):
        return ['journal', 'date_value', 'designation']

    @classmethod
    def get_show_fields(cls):
        return ['num', 'journal', 'date_entry', 'date_value', 'designation']

    @classmethod
    def get_print_fields(cls):
        return cls.get_show_fields()

    @classmethod
    def get_search_fields(cls):
        result = ['year', 'date_value', 'num', 'designation', 'date_entry', 'entrylineaccount_set.costaccounting']
        result.append(('entrylineaccount_set.amount', models.DecimalField(_('amount')), 'entrylineaccount__amount__abs', Q()))
        result.extend(['entrylineaccount_set.account.code', 'entrylineaccount_set.account.name',
                       'entrylineaccount_set.account.type_of_account', 'entrylineaccount_set.reference'])
        for fieldname in Third.get_search_fields():
            result.append("entrylineaccount_set.third." + fieldname)
        return result

    @classmethod
    def clear_ghost(cls):
        if not RecordLocker.has_item_lock(cls):
            for entry in cls.objects.filter(close=False):
                if len(entry.entrylineaccount_set.all()) == 0:
                    entry.delete()

    @property
    def description(self):
        res = self.designation
        res += "{[br/]}"
        res += "{[table style='min-width:200px;']}"
        for line in self.entrylineaccount_set.all():
            res += "{[tr]}"
            res += "{[td]}%s{[/td]}" % line.entry_account
            res += "{[td]}%s{[/td]}" % line.debit
            res += "{[td]}%s{[/td]}" % line.credit
            res += "{[td]}%s{[/td]}" % (line.costaccounting if line.costaccounting is not None else '---',)
            res += "{[td]}%s{[/td]}" % (line.link if line.link is not None else '---',)
            if (line.reference is not None) and (line.reference != ''):
                res += "{[td]}%s{[/td]}" % line.reference
            res += "{[/tr]}"
        res += "{[/table]}"
        return res

    @property
    def is_asset(self):
        sum_customer = get_amount_sum(self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_third_mask()).aggregate(Sum('amount')))
        return ((sum_customer < 0) and not self.has_cash) or ((sum_customer > 0) and self.has_cash)

    def reverse_entry(self):
        for line in self.entrylineaccount_set.all():
            line.amount = -1 * line.amount
            line.save()

    def can_delete(self):
        if self.close:
            return _('entry of account closed!')
        else:
            return ''

    def check_date(self):
        if self.date_value is None:
            self.date_value = date.today()
        if isinstance(self.date_value, date):
            self.date_value = self.date_value.isoformat()
        if self.journal_id == 1:
            self.date_value = self.year.begin.isoformat()
        if self.date_value > self.year.end.isoformat():
            self.date_value = self.year.end.isoformat()
        if self.date_value < self.year.begin.isoformat():
            self.date_value = self.year.begin.isoformat()
        return

    def delete(self):
        self.unlink()
        for entryline in self.entrylineaccount_set.all():
            entryline.unlink()
        LucteriosModel.delete(self)

    def get_serial(self, entrylines=None):
        if entrylines is None:
            entrylines = self.entrylineaccount_set.all()
        serial_val = ''
        for line in entrylines:
            if serial_val != '':
                serial_val += '\n'
            serial_val += line.get_serial()
        return serial_val

    def get_entrylineaccounts(self, serial_vals):
        res = QuerySet(model=EntryLineAccount)
        res._result_cache = []
        for serial_val in serial_vals.split('\n'):
            if serial_val != '':
                new_line = EntryLineAccount.get_entrylineaccount(serial_val)
                new_line.entry = self
                res._result_cache.append(new_line)
        return res

    def save_entrylineaccounts(self, serial_vals):
        if not self.close:
            self.entrylineaccount_set.all().delete()
            for line in self.get_entrylineaccounts(serial_vals):
                if line.id < 0:
                    line.id = None
                line.save()
            for line in self.entrylineaccount_set.all():
                if line.link_id is not None:
                    line.link.check_validity()

    def remove_entrylineaccounts(self, serial_vals, entrylineid):
        lines = self.get_entrylineaccounts(serial_vals)
        line_idx = -1
        for idx in range(len(lines)):
            if lines[idx].id == entrylineid:
                line_idx = idx
        del lines._result_cache[line_idx]
        return self.get_serial(lines)

    def add_new_entryline(self, serial_entry, entrylineaccount, num_cpt, credit_val, debit_val, third, costaccounting, reference):
        if self.journal.id == 1:
            charts = ChartsAccount.objects.get(id=num_cpt)
            if match(current_system_account().get_revenue_mask(), charts.code) or \
                    match(current_system_account().get_expence_mask(), charts.code):
                raise LucteriosException(IMPORTANT, _('This kind of entry is not allowed for this journal!'))
        if entrylineaccount != 0:
            serial_entry = self.remove_entrylineaccounts(serial_entry, entrylineaccount)
        if serial_entry != '':
            serial_entry += '\n'
        serial_entry += EntryLineAccount.add_serial(num_cpt, debit_val, credit_val, third, costaccounting, reference)
        return serial_entry

    def serial_control(self, serial_vals):
        total_credit = 0
        total_debit = 0
        serial = self.get_entrylineaccounts(serial_vals)
        current = self.entrylineaccount_set.all()
        no_change = len(serial) > 0
        if len(serial) == len(current):
            for idx in range(len(serial)):
                total_credit += serial[idx].get_credit()
                total_debit += serial[idx].get_debit()
                no_change = no_change and current[idx].equals(serial[idx])
        else:
            no_change = False
            for idx in range(len(serial)):
                total_credit += serial[idx].get_credit()
                total_debit += serial[idx].get_debit()
        return no_change, currency_round(max(0, total_credit - total_debit)), currency_round(max(0, total_debit - total_credit))

    def closed(self, check_balance=True):
        if (self.year.status != 2) and not self.close:
            if check_balance:
                _no_change, debit_rest, credit_rest = self.serial_control(self.get_serial())
                if abs(debit_rest - credit_rest) >= 0.001:
                    raise LucteriosException(GRAVE, "Account entry not balanced: sum credit=%.3f / sum debit=%.3f" % (debit_rest, credit_rest))
            if Params.getvalue("accounting-needcost"):
                for entryline in self.entrylineaccount_set.all():
                    if (entryline.account.type_of_account in (3, 4, 5)) and (entryline.costaccounting_id is None):
                        raise LucteriosException(IMPORTANT, _("Cost accounting is mandatory !"))
            self.close = True
            val = self.year.entryaccount_set.all().aggregate(Max('num'))
            if val['num__max'] is None:
                self.num = 1
            else:
                self.num = val['num__max'] + 1
            self.date_entry = date.today()
            self.save()

    def unlink(self):
        if (self.year.status != 2) and (self.link_id is not None):
            for entry in self.link.entryaccount_set.all():
                entry.link = None
                if not entry.delete_if_ghost_entry():
                    entry.save()
            self.link.delete()
            self.link = None

    def delete_if_ghost_entry(self):
        if (self.id is not None) and (len(self.entrylineaccount_set.all()) == 0) and not RecordLocker.is_lock(self):
            self.delete()
            return True
        else:
            return False

    def create_linked(self):
        if (self.year.status != 2) and (self.link is None):
            paym_journ = Journal.objects.get(id=4)
            paym_desig = _('payment of %s') % self.designation
            new_entry = EntryAccount.objects.create(
                year=self.year, journal=paym_journ, designation=paym_desig, date_value=date.today())
            serial_val = ''
            for line in self.entrylineaccount_set.all():
                if line.account.is_third:
                    if serial_val != '':
                        serial_val += '\n'
                    serial_val += line.create_clone_inverse()
            return new_entry, serial_val

    def add_entry_line(self, amount, code, name=None, third=None, reference=None):
        if abs(amount) > 0.0001:
            new_entry_line = EntryLineAccount()
            new_entry_line.entry = self
            new_entry_line.account = self.year.getorcreate_chartaccount(code, name)
            new_entry_line.amount = amount
            new_entry_line.third = third
            new_entry_line.reference = reference
            new_entry_line.save()
            return new_entry_line

    def get_thirds(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_third_mask()).distinct()

    @property
    def has_third(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_third_mask()).count() > 0

    @property
    def has_customer(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_customer_mask()).count() > 0

    @property
    def has_cash(self):
        return self.entrylineaccount_set.filter(account__code__regex=current_system_account().get_cash_mask()).count() > 0

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (self.costaccounting is not None) and (self.costaccounting.year_id is not None) and (self.costaccounting.year_id != self.year_id):
            self.costaccounting_id = None
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('entry of account')
        verbose_name_plural = _('entries of account')
        ordering = ['date_value']


class EntryLineAccount(LucteriosModel):
    account = models.ForeignKey('ChartsAccount', verbose_name=_('account'), null=False, on_delete=models.PROTECT)
    entry = models.ForeignKey('EntryAccount', verbose_name=_('entry'), null=False, on_delete=models.CASCADE)
    amount = models.FloatField(_('amount'), db_index=True)
    reference = models.CharField(_('reference'), max_length=200, null=True)
    third = models.ForeignKey('Third', verbose_name=_('third'), null=True, on_delete=models.PROTECT, db_index=True)
    costaccounting = models.ForeignKey('CostAccounting', verbose_name=_('cost accounting'), null=True, on_delete=models.PROTECT)
    link = models.ForeignKey('AccountLink', verbose_name=_('link'), null=True, on_delete=models.SET_NULL)

    def __str__(self):
        res = ""
        try:
            res = "%s %s" % (self.entry_account, format_devise(self.account.credit_debit_way() * self.amount, 2))
            if (self.reference is not None) and (self.reference != ''):
                res += " (%s)" % self.reference
        except BaseException:
            res = "???"
        return res

    @classmethod
    def get_other_fields(cls):
        return [(_('account'), 'entry_account'), (_('debit'), 'debit'), (_('credit'), 'credit'), 'reference', 'costaccounting', 'link']

    @classmethod
    def get_default_fields(cls):
        return ['entry.num', 'entry.date_entry', 'entry.date_value', (_('name'), 'designation_ref'), (_('account'), 'entry_account'),
                (_('debit'), 'debit'), (_('credit'), 'credit'), 'costaccounting', 'link']

    def get_color_ref(self):
        return self.entry_id

    @classmethod
    def get_edit_fields(cls):
        return ['entry.date_entry', 'entry.date_value', 'entry.designation',
                ((_('account'), 'entry_account'),), ((_('debit'), 'debit'),), ((_('credit'), 'credit'),)]

    @classmethod
    def get_show_fields(cls):
        return ['entry.date_entry', 'entry.date_value', 'entry.designation',
                ((_('account'), 'entry_account'),), ((_('debit'), 'debit'),), ((_('credit'), 'credit'),)]

    @classmethod
    def get_print_fields(cls):
        return ['entry', (_('account'), 'entry_account'), (_('debit'), 'debit'), (_('credit'), 'credit'), 'reference', 'third.contact.str', 'costaccounting.name']

    @classmethod
    def get_search_fields(cls):
        result = ['entry.year', 'entry.date_value', 'account.code']
        result.append(('amount', models.FloatField(_('amount')), 'amount__abs', Q()))
        result.extend(['reference', 'entry.num', 'entry.designation', 'entry.date_entry', 'costaccounting', 'account.name', 'account.type_of_account'])
        for fieldname in Third.get_search_fields():
            result.append(cls.convert_field_for_search('third', fieldname))
        return result

    @property
    def entry_account(self):
        if self.third is None:
            return six.text_type(self.account)
        else:
            return "[%s %s]" % (self.account.code, six.text_type(self.third))

    @property
    def designation_ref(self):
        val = self.entry.designation
        if (self.reference is not None) and (self.reference != ''):
            val = "%s{[br/]}%s" % (val, self.reference)
        return val

    def get_debit(self):
        try:
            return max((0, -1 * self.account.credit_debit_way() * self.amount))
        except ObjectDoesNotExist:
            return 0.0

    @property
    def debit(self):
        return format_devise(min(0, self.account.credit_debit_way() * self.amount), 6)

    def get_credit(self):
        try:
            return max((0, self.account.credit_debit_way() * self.amount))
        except ObjectDoesNotExist:
            return 0.0

    @property
    def credit(self):
        return format_devise(self.get_credit(), 6)

    def set_montant(self, debit_val, credit_val):
        if debit_val > 0:
            self.amount = -1 * debit_val * self.account.credit_debit_way()
        elif credit_val > 0:
            self.amount = credit_val * self.account.credit_debit_way()
        else:
            self.amount = 0

    def equals(self, other):
        res = self.id == other.id
        res = res and (self.account.id == other.account.id)
        res = res and (abs(self.amount - other.amount) < 0.0001)
        res = res and (self.reference == other.reference)
        if self.third is None:
            res = res and (other.third is None)
        else:
            res = res and (self.third.id == other.third.id)
        if self.costaccounting is None:
            res = res and (other.costaccounting is None)
        else:
            res = res and (self.costaccounting.id == other.costaccounting.id)
        return res

    def get_serial(self):
        # return serial information: "<id>|<accound id>|<third id> or 0|<amount>|<cost id> or 0|<link id> or 0|<reference> or None"
        if self.third is None:
            third_id = 0
        else:
            third_id = self.third.id
        if self.reference is None:
            reference = 'None'
        else:
            reference = self.reference
        if self.costaccounting is None:
            costaccounting_id = 0
        else:
            costaccounting_id = self.costaccounting.id
        if self.link is None:
            link_id = 0
        else:
            link_id = self.link.id
        return "%d|%d|%d|%f|%d|%d|%s|" % (self.id, self.account.id, third_id, self.amount, costaccounting_id, link_id, reference)

    @classmethod
    def add_serial(cls, num_cpt, debit_val, credit_val, thirdid=0, costaccountingid=0, reference=None):
        import time
        new_entry_line = cls()
        new_entry_line.id = -1 * int(time.time() * 60)
        new_entry_line.account = ChartsAccount.objects.get(id=num_cpt)
        if thirdid == 0:
            new_entry_line.third = None
        else:
            new_entry_line.third = Third.objects.get(id=thirdid)
        if (costaccountingid == 0) or (new_entry_line.account.type_of_account not in (3, 4, 5)):
            new_entry_line.costaccounting = None
        else:
            new_entry_line.costaccounting = CostAccounting.objects.get(id=costaccountingid)
        new_entry_line.set_montant(debit_val, credit_val)
        if reference == "None":
            new_entry_line.reference = None
        else:
            new_entry_line.reference = reference
        return new_entry_line.get_serial()

    @classmethod
    def get_entrylineaccount(cls, serial_val):
        serial_vals = serial_val.split('|')
        new_entry_line = cls()
        new_entry_line.id = int(serial_vals[0])
        new_entry_line.account = ChartsAccount.objects.get(id=int(serial_vals[1]))
        if int(serial_vals[2]) == 0:
            new_entry_line.third = None
        else:
            new_entry_line.third = Third.objects.get(id=int(serial_vals[2]))
        new_entry_line.amount = float(serial_vals[3])
        if (int(serial_vals[4]) == 0) or (new_entry_line.account.type_of_account not in (3, 4, 5)):
            new_entry_line.costaccounting = None
        else:
            new_entry_line.costaccounting = CostAccounting.objects.get(id=int(serial_vals[4]))
        if int(serial_vals[5]) == 0:
            new_entry_line.link = None
        else:
            new_entry_line.link = AccountLink.objects.get(id=int(serial_vals[5]))
        new_entry_line.reference = "".join(serial_vals[6:-1])
        if new_entry_line.reference.startswith("None"):
            new_entry_line.reference = None
        return new_entry_line

    def create_clone_inverse(self):
        import time
        new_entry_line = EntryLineAccount()
        new_entry_line.id = -1 * int(time.time() * 60)
        new_entry_line.account = self.account
        if self.third:
            new_entry_line.third = self.third
        else:
            new_entry_line.third = None
        new_entry_line.amount = -1 * self.amount
        if self.costaccounting:
            new_entry_line.costaccounting = self.costaccounting
        else:
            new_entry_line.costaccounting = None
        new_entry_line.reference = self.reference
        return new_entry_line.get_serial()

    @property
    def has_account(self):
        try:
            return self.account is not None
        except ObjectDoesNotExist:
            return False

    def unlink(self):
        if (self.entry.year.status != 2) and (self.link_id is not None):
            old_link = self.link
            for entryline in self.link.entrylineaccount_set.all():
                entryline.link = None
                if not entryline.entry.delete_if_ghost_entry():
                    entryline.save()
            if (old_link is not None) and (old_link.id is not None):
                old_link.delete()
            self.link = None

    def delete(self):
        self.unlink()
        LucteriosModel.delete(self)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (self.account.type_of_account not in (3, 4, 5)) and (self.costaccounting is not None):
            self.costaccounting = None
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('entry line of account')
        verbose_name_plural = _('entry lines of account')
        default_permissions = []
        ordering = ['entry__date_value', 'entry__id', 'account__code', 'third']


class ModelEntry(LucteriosModel):
    journal = models.ForeignKey('Journal', verbose_name=_('journal'), null=False, default=0, on_delete=models.PROTECT)
    designation = models.CharField(_('name'), max_length=200)
    costaccounting = models.ForeignKey('CostAccounting', verbose_name=_('cost accounting'), null=True,
                                       default=None, on_delete=models.SET_NULL)

    def __str__(self):
        return "[%s] %s (%s)" % (self.journal, self.designation, self.total)

    @classmethod
    def get_default_fields(cls):
        return ['journal', 'designation', (_('total'), 'total')]

    @classmethod
    def get_edit_fields(cls):
        return ['journal', 'designation', 'costaccounting']

    @classmethod
    def get_show_fields(cls):
        return ['journal', 'designation', 'costaccounting', ((_('total'), 'total'),), 'modellineentry_set']

    def get_total(self):
        try:
            value = 0.0
            for line in self.modellineentry_set.all():
                value += line.get_credit()
            return value
        except LucteriosException:
            return 0.0

    @property
    def total(self):
        return format_devise(self.get_total(), 5)

    def get_serial_entry(self, factor, year, costaccounting=None):
        entry_lines = []
        num = 0
        for line in self.modellineentry_set.all():
            entry_lines.append(line.get_entry_line(factor, num, year, costaccounting))
            num += 1
        return EntryAccount().get_serial(entry_lines)

    class Meta(object):

        verbose_name = _('Model of entry')
        verbose_name_plural = _('Models of entry')
        default_permissions = []


class ModelLineEntry(LucteriosModel):
    model = models.ForeignKey('ModelEntry', verbose_name=_('model'), null=False, default=0, on_delete=models.CASCADE)
    code = models.CharField(_('code'), max_length=50)
    third = models.ForeignKey('Third', verbose_name=_('third'), null=True, on_delete=models.PROTECT)
    amount = models.FloatField(_('amount'), default=0)

    @classmethod
    def get_default_fields(cls):
        return ['code', 'third', (_('debit'), 'debit'), (_('credit'), 'credit')]

    @classmethod
    def get_edit_fields(cls):
        return ['code']

    def credit_debit_way(self):
        chart_account = current_system_account().new_charts_account(self.code)
        if chart_account[0] == '':
            raise LucteriosException(IMPORTANT, _("Invalid code"))
        if chart_account[1] in [0, 4]:
            return -1
        else:
            return 1

    def get_debit(self):
        try:
            return max((0, -1 * self.credit_debit_way() * self.amount))
        except LucteriosException:
            return 0.0

    @property
    def debit(self):
        return format_devise(self.get_debit(), 0)

    def get_credit(self):
        try:
            return max((0, self.credit_debit_way() * self.amount))
        except LucteriosException:
            return 0.0

    @property
    def credit(self):
        return format_devise(self.get_credit(), 0)

    def set_montant(self, debit_val, credit_val):
        if debit_val > 0:
            self.amount = -1 * debit_val * self.credit_debit_way()
        elif credit_val > 0:
            self.amount = credit_val * self.credit_debit_way()
        else:
            self.amount = 0

    def get_entry_line(self, factor, num, year, costaccounting=None):
        import time
        try:
            new_entry_line = EntryLineAccount()
            new_entry_line.id = -1 * int(time.time() * 60) + (num * 15)
            new_entry_line.account = ChartsAccount.objects.get(year=year, code=correct_accounting_code(self.code))
            new_entry_line.third = self.third
            new_entry_line.amount = currency_round(self.amount * factor)
            if (costaccounting is not None) and (new_entry_line.account.type_of_account in (3, 4, 5)):
                new_entry_line.costaccounting = costaccounting
            new_entry_line.reference = None
            return new_entry_line
        except ObjectDoesNotExist:
            raise LucteriosException(IMPORTANT, _('Account code "%s" unknown for this fiscal year!') % self.code)

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        self.code = correct_accounting_code(self.code)
        return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    class Meta(object):
        verbose_name = _('Model line')
        verbose_name_plural = _('Model lines')
        default_permissions = []


class Budget(LucteriosModel):
    year = models.ForeignKey('FiscalYear', verbose_name=_('fiscal year'), null=True, default=None, on_delete=models.CASCADE)
    cost_accounting = models.ForeignKey('CostAccounting', verbose_name=_('cost accounting'), null=True, default=None, on_delete=models.PROTECT)
    code = models.CharField(_('account'), max_length=50)
    amount = models.FloatField(_('amount'), default=0)

    @property
    def budget(self):
        chart = ChartsAccount.get_chart_account(self.code)
        return six.text_type(chart)

    @classmethod
    def get_default_fields(cls):
        return [(_('code'), 'budget'), (_('amount'), 'montant')]

    @classmethod
    def get_edit_fields(cls):
        return ['code']

    def credit_debit_way(self):
        chart_account = current_system_account().new_charts_account(self.code)
        if chart_account[0] == '':
            raise LucteriosException(IMPORTANT, _("Invalid code"))
        if chart_account[1] in [0, 4]:
            return -1
        else:
            return 1

    @property
    def montant(self):
        return format_devise(self.credit_debit_way() * self.amount, 2)

    def get_debit(self):
        try:
            return max((0, -1 * self.credit_debit_way() * self.amount))
        except LucteriosException:
            return 0.0

    def get_credit(self):
        try:
            return max((0, self.credit_debit_way() * self.amount))
        except LucteriosException:
            return 0.0

    def set_montant(self, debit_val, credit_val):
        if debit_val > 0:
            self.amount = -1 * debit_val * self.credit_debit_way()
        elif credit_val > 0:
            self.amount = credit_val * self.credit_debit_way()
        else:
            self.amount = 0

    @classmethod
    def get_total(cls, year, cost):
        budget_filter = Q()
        if year is not None:
            budget_filter &= Q(year_id=year)
        if cost is not None:
            budget_filter &= Q(cost_accounting_id=cost)
        total_revenue = get_amount_sum(cls.objects.filter(budget_filter & Q(code__regex=current_system_account().get_revenue_mask())).aggregate(Sum('amount')))
        total_expense = get_amount_sum(cls.objects.filter(budget_filter & Q(code__regex=current_system_account().get_expence_mask())).aggregate(Sum('amount')))
        return total_revenue - total_expense

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if (self.cost_accounting is not None) and (self.cost_accounting.year_id is not None):
            self.year = self.cost_accounting.year
        if six.text_type(self.id)[0] == 'C':
            value = self.amount
            year = self.year_id
            chart_code = self.code
            self.delete()
            for current_budget in Budget.objects.filter(year_id=year, code=chart_code):
                value -= current_budget.amount
            if abs(value) > 0.001:
                Budget.objects.create(code=chart_code, amount=value, year_id=year)
        else:
            return LucteriosModel.save(self, force_insert=force_insert, force_update=force_update, using=using, update_fields=update_fields)

    def delete(self, using=None):
        if six.text_type(self.id)[0] == 'C':
            for budget_line in Budget.objects.filter(Q(year_id=self.year_id) & Q(code=self.code)):
                if budget_line.cost_accounting_id is None:
                    budget_line.delete()
        else:
            LucteriosModel.delete(self, using=using)

    class Meta(object):
        verbose_name = _('Budget line')
        verbose_name_plural = _('Budget lines')
        ordering = ['code']


def check_accountingcost():
    for entry in EntryAccount.objects.filter(costaccounting_id__gt=0, year__status__lt=2):
        try:
            if (entry.costaccounting.status == 1) and not entry.close:
                entry.costaccounting = None
                entry.save()
        except ObjectDoesNotExist:
            entry.costaccounting = None
            entry.save()
    entryline_cmp = 0
    for entryline in EntryLineAccount.objects.filter(costaccounting_id__isnull=True, entry__costaccounting_id__isnull=False, account__type_of_account__in=(3, 4, 5)).distinct():
        entryline.costaccounting_id = entryline.entry.costaccounting_id
        entryline.save()
        entryline_cmp += 1
    if entryline_cmp > 0:
        six.print_(' * convert costaccounting: nb=%d' % entryline_cmp)


def check_accountlink():
    new_link = 0
    old_link = 0
    account_link_list = list(AccountLink.objects.filter(entryaccount__isnull=False))
    for account_link in account_link_list:
        entryline_by_third = {}
        for entry_linked in account_link.entryaccount_set.all():
            for entryline_third in entry_linked.get_thirds():
                third_id = (entryline_third.account.code, entryline_third.third_id)
                if third_id not in entryline_by_third.keys():
                    entryline_by_third[third_id] = []
                entryline_by_third[third_id].append(entryline_third)
        for entrylines in entryline_by_third.values():
            try:
                AccountLink.create_link(set(entrylines), check_year=False)
                new_link += 1
            except LucteriosException as lct_ext:
                six.print_('!!! check_accountlink Error:', lct_ext, ' - lines:', entrylines)
        old_link += 1
        account_link.delete()
    if old_link > 0:
        from django.utils.module_loading import import_module
        from django.apps.registry import apps
        if apps.is_installed("diacamma.invoice"):
            invoice_model = import_module('diacamma.invoice.models')
            invoice_model.correct_quotation_asset_account()
        if apps.is_installed("diacamma.payoff"):
            payoff_model = import_module('diacamma.payoff.models')
            addon_linked = payoff_model.check_accountlink_from_supporting()
        else:
            addon_linked = 0
        six.print_(' * convert AccountLink: old= %d / new= %d + %d' % (old_link, new_link, addon_linked))


def pre_save_datadb(sender, **kwargs):
    if (sender == EntryAccount) and ('instance' in kwargs):
        if kwargs['instance'].costaccounting_id == 0:
            six.print_('* Convert EntryAccount #%d' % kwargs['instance'].id)
            kwargs['instance'].costaccounting_id = None


@Signal.decorate('checkparam')
def accounting_checkparam():
    Parameter.check_and_create(name='accounting-devise', typeparam=0, title=_("accounting-devise"), args="{'Multi':False}", value='€')
    Parameter.check_and_create(name='accounting-devise-iso', typeparam=0, title=_("accounting-devise-iso"), args="{'Multi':False}", value='EUR')
    Parameter.check_and_create(name='accounting-devise-prec', typeparam=1, title=_("accounting-devise-prec"), args="{'Min':0, 'Max':4}", value='2')
    Parameter.check_and_create(name='accounting-system', typeparam=0, title=_("accounting-system"), args="{'Multi':False}", value='')
    Parameter.check_and_create(name='accounting-sizecode', typeparam=1, title=_("accounting-sizecode"), args="{'Min':3, 'Max':50}", value='3')
    Parameter.check_and_create(name='accounting-needcost', typeparam=3, title=_("accounting-needcost"), args="{}", value='False')
    Parameter.check_and_create(name='accounting-code-report-filter', typeparam=0, title=_("accounting-code-report-filter"), args="{'Multi':False}", value='')
    check_accountingcost()
    check_accountlink()


pre_save.connect(pre_save_datadb)
