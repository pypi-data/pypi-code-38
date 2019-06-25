# -*- coding: utf-8 -*-
'''
Describe test for Django

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
from shutil import rmtree
from os.path import exists
from base64 import b64decode
from datetime import date

from django.utils import six, formats
from django.db.models import Q

from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir, get_user_path
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params
from lucterios.CORE.views import StatusMenu
from lucterios.contacts.models import CustomField

from diacamma.accounting.views_entries import EntryAccountList, EntryAccountListing, EntryAccountEdit, EntryAccountShow, \
    EntryAccountClose, EntryAccountCostAccounting, EntryAccountSearch
from diacamma.accounting.test_tools import default_compta_fr, initial_thirds_fr, fill_entries_fr, add_entry
from diacamma.accounting.views_other import CostAccountingList, CostAccountingClose, CostAccountingAddModify
from diacamma.accounting.views_reports import FiscalYearBalanceSheet, FiscalYearIncomeStatement, FiscalYearLedger, FiscalYearTrialBalance,\
    CostAccountingTrialBalance, CostAccountingLedger, CostAccountingIncomeStatement,\
    FiscalYearReportPrint
from diacamma.accounting.views_admin import FiscalYearExport
from diacamma.accounting.models import FiscalYear, Third
from diacamma.accounting.tools_reports import get_totalaccount_for_query, get_totalbudget_for_query
from diacamma.accounting.views_budget import BudgetList, BudgetAddModify, BudgetDel, BudgetImport


class CompletedEntryTest(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr(with8=True)
        rmtree(get_user_dir(), True)
        fill_entries_fr(1)
        add_entry(1, 5, '2015-12-31', 'Bénévolat', '-1|19|0|-1234.000000|0|0|None|\n-2|18|0|1234.000000|0|0|None|', True)
        last_year = FiscalYear.objects.create(begin='2014-01-01', end='2014-12-31', status=2)  # id=2
        current_year = FiscalYear.objects.get(id=1)
        current_year.last_fiscalyear = last_year
        current_year.save()

    def _goto_entrylineaccountlist(self, journal, filterlist, nb_line):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': journal, 'filter': filterlist}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', nb_line)

    def test_lastyear(self):
        self._goto_entrylineaccountlist(1, 0, 3)
        self.assert_json_equal('', 'entryline/@0/entry.num', '1')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[106] 106')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}1250.38€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@1/debit', '{[font color="blue"]}1135.93€{[/font]}')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[531] 531')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}114.45€{[/font]}')

    def test_buying(self):
        self._goto_entrylineaccountlist(2, 0, 6)
        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/link', 'C')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}194.08€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[607] 607')

        self.assert_json_equal('', 'entryline/@2/entry.num', '2')
        self.assert_json_equal('', 'entryline/@2/link', 'A')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@2/credit', '{[font color="green"]}63.94€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[602] 602')

        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/link', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@4/credit', '{[font color="green"]}78.24€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[601] 601')

    def test_selling(self):
        self._goto_entrylineaccountlist(3, 0, 6)
        self.assert_json_equal('', 'entryline/@0/entry.num', '4')
        self.assert_json_equal('', 'entryline/@0/link', 'E')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}70.64€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry.num', '4')
        self.assert_json_equal('', 'entryline/@1/link', '---')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[707] 707')

        self.assert_json_equal('', 'entryline/@2/entry.num', '6')
        self.assert_json_equal('', 'entryline/@2/link', '---')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}125.97€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry.num', '6')
        self.assert_json_equal('', 'entryline/@3/link', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[707] 707')

        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/link', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[411 Minimum]')
        self.assert_json_equal('', 'entryline/@4/debit', '{[font color="blue"]}34.01€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry.num', '---')
        self.assert_json_equal('', 'entryline/@5/link', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[707] 707')

    def test_payment(self):
        self._goto_entrylineaccountlist(4, 0, 6)
        self.assert_json_equal('', 'entryline/@0/entry.num', '3')
        self.assert_json_equal('', 'entryline/@0/link', 'A')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}63.94€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[512] 512')

        self.assert_json_equal('', 'entryline/@2/entry.num', '---')
        self.assert_json_equal('', 'entryline/@2/link', 'C')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}194.08€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[531] 531')

        self.assert_json_equal('', 'entryline/@4/entry.num', '5')
        self.assert_json_equal('', 'entryline/@4/link', 'E')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[411 Dalton Joe]')
        self.assert_json_equal('', 'entryline/@4/credit', '{[font color="green"]}70.64€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[512] 512')

    def test_other(self):
        self._goto_entrylineaccountlist(5, 0, 4)
        self.assert_json_equal('', 'entryline/@0/entry.num', '7')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}12.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[627] 627')

    def _check_result(self):
        return self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 230.62€ - {[b]}Charge :{[/b]} 348.60€ = {[b]}Résultat :{[/b]} -117.98€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')

    def _check_result_with_filter(self):
        return self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 34.01€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 34.01€{[br/]}{[b]}Trésorerie :{[/b]} 70.64€ - {[b]}Validé :{[/b]} 70.64€{[/center]}')

    def test_all(self):
        self._goto_entrylineaccountlist(-1, 0, 25)
        self._check_result()

    def test_noclose(self):
        self._goto_entrylineaccountlist(-1, 1, 8)

    def test_close(self):
        self._goto_entrylineaccountlist(-1, 2, 17)

    def test_letter(self):
        self._goto_entrylineaccountlist(-1, 3, 12)

    def test_noletter(self):
        self._goto_entrylineaccountlist(-1, 4, 13)

    def test_summary(self):
        self.factory.xfer = StatusMenu()
        self.calljson('/CORE/statusMenu', {}, False)
        self.assert_observer('core.custom', 'CORE', 'statusMenu')
        self.assert_json_equal('LABELFORM', 'accounting_year',
                               "{[center]}Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]{[/center]}")
        self.assert_json_equal('LABELFORM', 'accounting_result',
                               '{[center]}{[b]}Produit :{[/b]} 230.62€ - {[b]}Charge :{[/b]} 348.60€ = {[b]}Résultat :{[/b]} -117.98€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')
        self.assert_json_equal('LABELFORM', 'accountingtitle', "{[center]}{[u]}{[b]}Comptabilité{[/b]}{[/u]}{[/center]}")

    def test_listing(self):
        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 33, str(content_csv))
        self.assertEqual(content_csv[1].strip()[:20], '"Liste d\'écritures -')
        self.assertEqual(content_csv[4].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[5].strip(), '"1";"%s";"1 février 2015";"[106] 106";"Report à nouveau";"";"1250.38€";"";' % formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[9].strip(), '"---";"---";"13 février 2015";"[607] 607";"depense 2";"194.08€";"";"";')

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '1'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 16, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '2'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 25, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '3'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 20, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '4'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(
            six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 21, str(content_csv))

        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '4', 'filter': '0'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(
            six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 14, str(content_csv))

    def test_search(self):
        self.factory.xfer = EntryAccountSearch()
        self.calljson('/diacamma.accounting/entryAccountSearch',
                      {'year': '1', 'journal': '-1', 'filter': '0', 'CRITERIA': 'entry.year||8||1//account.code||6||7'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountSearch')
        self.assert_count_equal('', 21)
        self.assert_count_equal('entryline', 3)

    def test_listing_search(self):
        self.factory.xfer = EntryAccountListing()
        self.calljson('/diacamma.accounting/entryAccountListing',
                      {'PRINT_MODE': '4', 'MODEL': 7, 'year': '1', 'journal': '-1', 'filter': '0', 'CRITERIA': 'entry.year||8||1//account.code||6||7'}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'entryAccountListing')
        csv_value = b64decode(six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 11, str(content_csv))
        self.assertEqual(content_csv[1].strip()[:20], '"Liste d\'écritures -')
        self.assertEqual(content_csv[4].strip(), '"N°";"date d\'écriture";"date de pièce";"compte";"nom";"débit";"crédit";"lettrage";')
        self.assertEqual(content_csv[5].strip(), '"4";"%s";"21 février 2015";"[707] 707";"vente 1";"";"70.64€";"";' % formats.date_format(date.today(), "DATE_FORMAT"))
        self.assertEqual(content_csv[7].strip(), '"---";"---";"24 février 2015";"[707] 707";"vente 3";"";"34.01€";"";')

    def test_report_tool(self):
        values, total = get_totalaccount_for_query(Q(account__type_of_account=0) & Q(entry__year_id=1))
        self.assertAlmostEqual(1050.66 + 159.98, total, delta=0.0001)
        self.assertEqual(3, len(values), values)
        self.assertAlmostEqual(159.98, values['411'][0], delta=0.0001)
        self.assertAlmostEqual(1130.29, values['512'][0], delta=0.0001)
        self.assertAlmostEqual(-79.63, values['531'][0], delta=0.0001)
        self.assertEqual('[411] 411', values['411'][1])
        self.assertEqual('[512] 512', values['512'][1])
        self.assertEqual('[531] 531', values['531'][1])

        values, total = get_totalaccount_for_query(Q(account__code__regex=r'^4[0-9][0-9][0-9a-zA-Z]*$') & Q(entry__year_id=1), 1, True)
        self.assertAlmostEqual(78.24, total, delta=0.0001)
        self.assertEqual(1, len(values), values)
        self.assertAlmostEqual(78.24, values['401#2'][0], delta=0.0001)
        self.assertEqual('[401 Maximum]', values['401#2'][1])

        values, total = get_totalaccount_for_query(Q(account__code__regex=r'^4[0-9][0-9][0-9a-zA-Z]*$') & Q(entry__year_id=1), -1, True)
        self.assertAlmostEqual(159.98, total, delta=0.0001)
        self.assertEqual(2, len(values), values)
        self.assertAlmostEqual(34.01, values['411#4'][0], delta=0.0001)
        self.assertAlmostEqual(125.97, values['411#5'][0], delta=0.0001)
        self.assertEqual('[411 Minimum]', values['411#4'][1])
        self.assertEqual('[411 Dalton William]', values['411#5'][1])

        values, total = get_totalaccount_for_query(Q(account__type_of_account=3) & Q(entry__year_id=1))
        self.assertAlmostEqual(230.62, total, delta=0.0001)
        self.assertEqual(1, len(values), values)
        self.assertAlmostEqual(230.62, values['707'][0], delta=0.0001)
        self.assertEqual('[707] 707', values['707'][1])

        values, total = get_totalbudget_for_query(Q(code__regex=r'^6.*$') & Q(year_id=1))
        self.assertAlmostEqual(21.78, total, delta=0.0001)
        self.assertAlmostEqual(8.19, values['601'][0], delta=0.0001)
        self.assertEqual('[601] 601', values['601'][1])
        self.assertAlmostEqual(7.35, values['602'][0], delta=0.0001)
        self.assertEqual('[602] 602', values['602'][1])
        self.assertAlmostEqual(6.24, values['604'][0], delta=0.0001)
        self.assertEqual('[604] 604', values['604'][1])

    def test_costaccounting(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 4)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '2', 'entryaccount': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('', 10)
        self.assert_json_equal('LABELFORM', 'designation', 'depense 1')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[401 Minimum]')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', 'open')
        self.assert_count_equal('#entrylineaccount/actions', 1)
        self.assertEqual(len(self.json_actions), 1)

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '2', 'entryaccount': '11'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'designation', 'Frais bancaire')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[512] 512')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[627] 627')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', 'close')
        self.assert_count_equal('#entrylineaccount/actions', 0)
        self.assertEqual(len(self.json_actions), 1)

    def test_costaccounting_list(self):
        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('', 5)
        self.assert_count_equal('costaccounting', 1)
        self.assert_json_equal('', 'costaccounting/@0/name', 'open')
        self.assert_json_equal('', 'costaccounting/@0/description', 'Open cost')
        self.assert_json_equal('', 'costaccounting/@0/year', '---')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '258.02€')
        self.assert_json_equal('', 'costaccounting/@0/total_result', '-187.38€')
        self.assert_json_equal('', 'costaccounting/@0/status', 'ouverte')
        self.assert_json_equal('', 'costaccounting/@0/is_default', '1')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 1)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)

        self.factory.xfer = CostAccountingClose()
        self.calljson('/diacamma.accounting/costAccountingClose',
                      {'costaccounting': 2}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'costAccountingClose')
        self.assert_json_equal('', 'message', 'La comptabilité  "open" a des écritures non validées !')

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', 'journal': '2', "entryline": "8"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = CostAccountingClose()
        self.calljson('/diacamma.accounting/costAccountingClose',
                      {'CONFIRME': 'YES', 'costaccounting': 2}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingClose')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 0)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)

    def test_costaccouting_budget(self):
        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('#budget_revenue/actions', 2)
        self.assert_json_equal('', 'budget_revenue/@0/budget', '[701] 701')
        self.assert_json_equal('', 'budget_revenue/@0/montant', '{[font color="green"]}Crédit: 67.89€{[/font]}')
        self.assert_json_equal('', 'budget_revenue/@1/budget', '[707] 707')
        self.assert_json_equal('', 'budget_revenue/@1/montant', '{[font color="green"]}Crédit: 123.45€{[/font]}')
        self.assert_count_equal('budget_expense', 3)
        self.assert_json_equal('', 'budget_expense/@0/budget', '[601] 601')
        self.assert_json_equal('', 'budget_expense/@0/montant', '{[font color="blue"]}Débit: 8.19€{[/font]}')
        self.assert_json_equal('', 'budget_expense/@1/budget', '[602] 602')
        self.assert_json_equal('', 'budget_expense/@1/montant', '{[font color="blue"]}Débit: 7.35€{[/font]}')
        self.assert_json_equal('', 'budget_expense/@2/budget', '[604] 604')
        self.assert_json_equal('', 'budget_expense/@2/montant', '{[font color="blue"]}Débit: 6.24€{[/font]}')
        self.assert_count_equal('#budget_expense/actions', 2)
        self.assert_json_equal('LABELFORM', 'result', '169.56€')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'cost_accounting': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 5)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_count_equal('budget_revenue', 0)
        self.assert_count_equal('#budget_revenue/actions', 2)
        self.assert_count_equal('budget_expense', 0)
        self.assert_count_equal('#budget_expense/actions', 2)

        self.factory.xfer = BudgetAddModify()
        self.calljson('/diacamma.accounting/budgetAddModify', {'cost_accounting': '3', 'code': '602', 'debit_val': '19.64', 'credit_val': '0.00', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetAddModify')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'cost_accounting': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_count_equal('budget_revenue', 0)
        self.assert_count_equal('#budget_revenue/actions', 2)
        self.assert_count_equal('budget_expense', 1)
        self.assert_json_equal('', 'budget_expense/@0/id', '6')
        self.assert_json_equal('', 'budget_expense/@0/budget', '[602] 602')
        self.assert_json_equal('', 'budget_expense/@0/montant', '{[font color="blue"]}Débit: 19.64€{[/font]}')
        self.assert_count_equal('#budget_expense/actions', 2)
        self.assert_json_equal('LABELFORM', 'result', '-19.64€')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('budget_expense', 3)
        self.assert_json_equal('LABELFORM', 'result', '149.92€')

        self.factory.xfer = BudgetDel()
        self.calljson('/diacamma.accounting/budgetDel', {'year': '1', 'budget_expense': 'C602', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetDel')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('budget_expense', 3)
        self.assert_json_equal('LABELFORM', 'result', '157.27€')

        self.factory.xfer = BudgetDel()
        self.calljson('/diacamma.accounting/budgetDel', {'cost_accounting': '3', 'budget_expense': '6', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetDel')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('budget_expense', 2)
        self.assert_json_equal('LABELFORM', 'result', '176.91€')

    def test_costaccounting_change(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingAddModify')
        self.assert_count_equal('', 5)
        self.assert_select_equal('last_costaccounting', 3)  # nb=3
        self.assert_select_equal('year', 3)  # nb=3

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'bbb', 'description': 'bbb', 'year': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 4

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/id', '3')
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@0/year', 'Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/id', '4')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@1/year', 'Exercice du 1 janvier 2016 au 31 décembre 2016 [en création]')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/id', '2')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/year', '---')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '258.02€')

        self._goto_entrylineaccountlist(-1, 0, 25)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', '---')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountCostAccounting')
        self.assert_count_equal('', 3)
        self.assert_select_equal('cost_accounting_id', {0: None, 2: 'open', 3: 'aaa'})  # nb=3
        self.assert_json_equal('SELECT', 'cost_accounting_id', '2')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '2'}, False)  # -78.24 / +125.97
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 25)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', 'open')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', 'open')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '196.61€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '336.26€')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '0'}, False)  # - -194.08 / 0
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 25)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', '---')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '63.94€')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 25)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', 'aaa')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '125.97€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '272.32€')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '63.94€')

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'id': '3', 'year': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'costAccountingAddModify')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '4'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self._goto_entrylineaccountlist(-1, 0, 25)
        self.assert_json_equal('', 'entryline/@3/id', '9')
        self.assert_json_equal('', 'entryline/@3/entry.num', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[401 Dalton Avrel]')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@4/id', '8')
        self.assert_json_equal('', 'entryline/@4/entry.num', '---')
        self.assert_json_equal('', 'entryline/@4/entry_account', '[607] 607')
        self.assert_json_equal('', 'entryline/@4/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@11/id', '13')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[401 Maximum]')
        self.assert_json_equal('', 'entryline/@11/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@12/id', '12')
        self.assert_json_equal('', 'entryline/@12/entry.num', '---')
        self.assert_json_equal('', 'entryline/@12/entry_account', '[601] 601')
        self.assert_json_equal('', 'entryline/@12/costaccounting', 'aaa')
        self.assert_json_equal('', 'entryline/@17/id', '19')
        self.assert_json_equal('', 'entryline/@17/entry.num', '6')
        self.assert_json_equal('', 'entryline/@17/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@17/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@18/id', '18')
        self.assert_json_equal('', 'entryline/@18/entry.num', '6')
        self.assert_json_equal('', 'entryline/@18/entry_account', '[707] 707')
        self.assert_json_equal('', 'entryline/@18/costaccounting', 'aaa')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@0/total_revenue', '125.97€')
        self.assert_json_equal('', 'costaccounting/@0/total_expense', '272.32€')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@1/total_revenue', '0.00€')
        self.assert_json_equal('', 'costaccounting/@1/total_expense', '0.00€')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')
        self.assert_json_equal('', 'costaccounting/@2/total_revenue', '70.64€')
        self.assert_json_equal('', 'costaccounting/@2/total_expense', '63.94€')

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': 1, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 1)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': 3, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 1)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': -1, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 2)

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'year': 0, 'status': -1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 4)

    def test_costaccounting_needed(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'bbb', 'description': 'bbb', 'year': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 4

        self.factory.xfer = CostAccountingList()
        self.calljson('/diacamma.accounting/costAccountingList', {'status': 0}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingList')
        self.assert_count_equal('costaccounting', 3)
        self.assert_json_equal('', 'costaccounting/@0/name', 'aaa')
        self.assert_json_equal('', 'costaccounting/@1/name', 'bbb')
        self.assert_json_equal('', 'costaccounting/@2/name', 'open')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountCostAccounting')
        self.assert_count_equal('', 3)
        self.assert_select_equal('cost_accounting_id', {0: None, 2: 'open', 3: 'aaa'})  # nb=3
        self.assert_json_equal('SELECT', 'cost_accounting_id', '2')

        Parameter.change_value('accounting-needcost', '1')
        Params.clear()

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose', {'CONFIRME': 'YES', 'year': '1', 'journal': '2', 'entryline': '10;11'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose', {'CONFIRME': 'YES', 'year': '1', 'journal': '2', 'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryAccountClose')
        self.assert_json_equal('', 'message', 'La comptabilité analytique est obligatoire !')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountCostAccounting')
        self.assert_count_equal('', 3)
        self.assert_select_equal('cost_accounting_id', {2: 'open', 3: 'aaa'})  # nb=2
        self.assert_json_equal('SELECT', 'cost_accounting_id', '2')

        self.factory.xfer = EntryAccountCostAccounting()
        self.calljson('/diacamma.accounting/entryAccountCostAccounting', {"SAVE": "YES", 'entryline': '8;9;12;13;18;19', 'cost_accounting_id': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCostAccounting')

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose', {'CONFIRME': 'YES', 'year': '1', 'journal': '2', 'entryline': '8;9;12;13;18;19'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

    def test_costaccounting_incomestatement(self):
        self.factory.xfer = CostAccountingIncomeStatement()
        self.calljson('/diacamma.accounting/costAccountingIncomeStatement', {'costaccounting': '1;2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingIncomeStatement')
        self.assert_count_equal('', 2)
        self.assertFalse('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_grid_equal('report_2', {"name": "Comptabilit\u00e9 analytique", "left": "Charges", "left_n": "Valeur",
                                            "left_b": "Budget", "space": "", "right": "Produits", "right_n": "Valeur", "right_b": "Budget"}, 6 + 7 + 2)

        self.factory.xfer = CostAccountingIncomeStatement()
        self.calljson('/diacamma.accounting/costAccountingIncomeStatement', {'costaccounting': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingIncomeStatement')
        self.assert_count_equal('', 3)
        self.assertFalse('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_grid_equal('report_1', {"left": "Charges", "left_n": "Valeur", "left_b": "Budget",
                                            "space": "", "right": "Produits", "right_n": "Valeur", "right_b": "Budget"}, 6)

        self.factory.xfer = CostAccountingIncomeStatement()
        self.calljson('/diacamma.accounting/costAccountingIncomeStatement', {'costaccounting': '2', 'begin_date': '2015-02-14', 'end_date': '2015-02-20'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingIncomeStatement')
        self.assert_count_equal('', 5)
        self.assertFalse('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assert_grid_equal('report_2', {"left": "Charges", "left_n": "Valeur", "space": "", "right": "Produits", "right_n": "Valeur"}, 6)

    def test_costaccounting_importbudget(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)
        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '2', 'last_costaccounting': '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'cost_accounting': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 5)
        self.assert_count_equal('budget_revenue', 0)
        self.assert_count_equal('budget_expense', 0)

        self.factory.xfer = BudgetImport()
        self.calljson('/diacamma.accounting/budgetImport', {'cost_accounting': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetImport')
        self.assert_count_equal('', 4)
        self.assert_select_equal('costaccounting', {2: 'open'})

        self.factory.xfer = BudgetImport()
        self.calljson('/diacamma.accounting/budgetImport', {'cost_accounting': '3', 'costaccounting': '2', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetImport')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'cost_accounting': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assert_count_equal('budget_revenue', 1)
        self.assert_count_equal('budget_expense', 2)
        self.assert_json_equal('LABELFORM', 'result', '-187.38€')

    def test_costaccounting_ledger(self):
        self.factory.xfer = CostAccountingLedger()
        self.calljson('/diacamma.accounting/costAccountingLedger', {'costaccounting': '1;2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingLedger')
        self.assert_count_equal('', 2 + 2 * 2)
        self.assertTrue('__tab_2' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('report_1', 5)
        self.assert_count_equal('report_2', 15)

        self.factory.xfer = CostAccountingLedger()
        self.calljson('/diacamma.accounting/costAccountingLedger', {'costaccounting': '2', 'begin_date': '2015-02-14', 'end_date': '2015-02-20'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingLedger')
        self.assert_count_equal('', 5 + 2 * 1)
        self.assertTrue('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_2' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('report_2', 15)

    def test_costaccounting_trialbalance(self):
        self.factory.xfer = CostAccountingTrialBalance()
        self.calljson('/diacamma.accounting/costAccountingTrialBalance', {'costaccounting': '1;2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingTrialBalance')
        self.assert_count_equal('', 2 + 2 * 2)
        self.assertTrue('__tab_2' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_3' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('report_1', 1)
        self.assert_count_equal('report_2', 3)

        self.factory.xfer = CostAccountingTrialBalance()
        self.calljson('/diacamma.accounting/costAccountingTrialBalance', {'costaccounting': '2', 'begin_date': '2015-02-14', 'end_date': '2015-02-20'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'costAccountingTrialBalance')
        self.assert_count_equal('', 5 + 2 * 1)
        self.assertTrue('__tab_1' in self.json_data.keys(), self.json_data.keys())
        self.assertFalse('__tab_2' in self.json_data.keys(), self.json_data.keys())
        self.assert_count_equal('report_2', 3)

    def test_fiscalyear_balancesheet(self):
        self.factory.xfer = FiscalYearBalanceSheet()
        self.calljson('/diacamma.accounting/fiscalYearBalanceSheet', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBalanceSheet')
        self._check_result()
        self.assert_count_equal('report_1', 11)
        self.assert_json_equal('', 'report_1/@1/left', '[411] 411')
        self.assert_json_equal('', 'report_1/@1/left_n', '159.98€')
        self.assert_json_equal('', 'report_1/@1/left_n_1', '')

        self.assert_json_equal('', 'report_1/@5/left', '[512] 512')
        self.assert_json_equal('', 'report_1/@5/left_n', '1130.29€')
        self.assert_json_equal('', 'report_1/@5/left_n_1', '')

        self.assert_json_equal('', 'report_1/@6/left', '[531] 531')
        self.assert_json_equal('', 'report_1/@6/left_n', '-79.63€')
        self.assert_json_equal('', 'report_1/@6/left_n_1', '')

        self.assert_json_equal('', 'report_1/@1/right', '[106] 106')
        self.assert_json_equal('', 'report_1/@1/right_n', '1250.38€')
        self.assert_json_equal('', 'report_1/@1/right_n_1', '')

        self.assert_json_equal('', 'report_1/@5/right', '[401] 401')
        self.assert_json_equal('', 'report_1/@5/right_n', '78.24€')
        self.assert_json_equal('', 'report_1/@5/right_n_1', '')

    def test_fiscalyear_balancesheet_filter(self):
        self.factory.xfer = FiscalYearBalanceSheet()
        self.calljson('/diacamma.accounting/fiscalYearBalanceSheet', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBalanceSheet')
        self._check_result_with_filter()

    def test_fiscalyear_balancesheet_print(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'classname': 'FiscalYearBalanceSheet', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        self.save_pdf()

    def test_fiscalyear_incomestatement(self):
        self.factory.xfer = FiscalYearIncomeStatement()
        self.calljson('/diacamma.accounting/fiscalYearIncomeStatement', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearIncomeStatement')
        self._check_result()
        self.assert_count_equal('report_1', 12)

        self.assert_json_equal('', 'report_1/@0/left', '[601] 601')
        self.assert_json_equal('', 'report_1/@0/left_n', '78.24€')
        self.assert_json_equal('', 'report_1/@0/left_n_1', '')
        self.assert_json_equal('', 'report_1/@0/left_b', '8.19€')

        self.assert_json_equal('', 'report_1/@1/left', '[602] 602')
        self.assert_json_equal('', 'report_1/@1/left_n', '63.94€')
        self.assert_json_equal('', 'report_1/@1/left_n_1', '')
        self.assert_json_equal('', 'report_1/@1/left_b', '7.35€')

        self.assert_json_equal('', 'report_1/@2/left', '[604] 604')
        self.assert_json_equal('', 'report_1/@2/left_n', '0.00€')
        self.assert_json_equal('', 'report_1/@2/left_n_1', '')
        self.assert_json_equal('', 'report_1/@2/left_b', '6.24€')

        self.assert_json_equal('', 'report_1/@3/left', '[607] 607')
        self.assert_json_equal('', 'report_1/@3/left_n', '194.08€')
        self.assert_json_equal('', 'report_1/@3/left_n_1', '')
        self.assert_json_equal('', 'report_1/@3/left_b', '')

        self.assert_json_equal('', 'report_1/@4/left', '[627] 627')
        self.assert_json_equal('', 'report_1/@4/left_n', '12.34€')
        self.assert_json_equal('', 'report_1/@4/left_n_1', '')
        self.assert_json_equal('', 'report_1/@4/left_b', '')

        self.assert_json_equal('', 'report_1/@9/left', '[870] 870')
        self.assert_json_equal('', 'report_1/@9/left_n', '1234.00€')
        self.assert_json_equal('', 'report_1/@9/left_n_1', '')
        self.assert_json_equal('', 'report_1/@9/left_b', '')

        self.assert_json_equal('', 'report_1/@0/right', '[701] 701')
        self.assert_json_equal('', 'report_1/@0/right_n', '0.00€')
        self.assert_json_equal('', 'report_1/@0/right_n_1', '')
        self.assert_json_equal('', 'report_1/@0/right_b', '67.89€')

        self.assert_json_equal('', 'report_1/@1/right', '[707] 707')
        self.assert_json_equal('', 'report_1/@1/right_n', '230.62€')
        self.assert_json_equal('', 'report_1/@1/right_n_1', '')
        self.assert_json_equal('', 'report_1/@1/right_b', '123.45€')

        self.assert_json_equal('', 'report_1/@9/right', '[860] 860')
        self.assert_json_equal('', 'report_1/@9/right_n', '1234.00€')
        self.assert_json_equal('', 'report_1/@9/right_n_1', '')
        self.assert_json_equal('', 'report_1/@9/right_b', '')

    def test_fiscalyear_import_budget(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear_id=1)

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 5)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_count_equal('budget_revenue', 0)
        self.assert_count_equal('#budget_revenue/actions', 2)
        self.assert_count_equal('budget_expense', 0)
        self.assert_count_equal('#budget_expense/actions', 2)

        self.factory.xfer = BudgetImport()
        self.calljson('/diacamma.accounting/budgetImport', {'year': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetImport')
        self.assert_count_equal('', 4)
        self.assert_select_equal('currentyear', {1: 'Exercice du 1 janvier 2015 au 31 décembre 2015 [en création]', 2: 'Exercice du 1 janvier 2014 au 31 décembre 2014 [terminé]'})

        self.factory.xfer = BudgetImport()
        self.calljson('/diacamma.accounting/budgetImport', {'year': '3', 'currentyear': '1', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetImport')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assert_count_equal('budget_revenue', 1)
        self.assert_count_equal('budget_expense', 4)
        self.assert_json_equal('LABELFORM', 'result', '-117.98€')

    def test_fiscalyear_incomestatement_filter(self):
        self.factory.xfer = FiscalYearIncomeStatement()
        self.calljson('/diacamma.accounting/fiscalYearIncomeStatement', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearIncomeStatement')
        self._check_result_with_filter()

    def test_fiscalyear_incomestatement_print(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'classname': 'FiscalYearIncomeStatement', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        pdf_value = b64decode(six.text_type(self.response_json['print']["content"]))
        self.save_pdf()

    def test_fiscalyear_ledger(self):
        self.factory.xfer = FiscalYearLedger()
        self.calljson('/diacamma.accounting/fiscalYearLedger', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearLedger')
        self._check_result()

    def test_fiscalyear_ledger_filter(self):
        self.factory.xfer = FiscalYearLedger()
        self.calljson('/diacamma.accounting/fiscalYearLedger', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearLedger')
        self._check_result_with_filter()

    def test_fiscalyear_ledger_print(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'classname': 'FiscalYearLedger', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_pdf()

    def test_fiscalyear_trialbalance(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self._check_result()
        self.assert_count_equal('report_1', 12)
        self.assert_json_equal('', 'report_1/@0/designation', '[106] 106')
        self.assert_json_equal('', 'report_1/@0/total_debit', '0.00€')
        self.assert_json_equal('', 'report_1/@0/total_credit', '1250.38€')
        self.assert_json_equal('', 'report_1/@0/solde_debit', '')
        self.assert_json_equal('', 'report_1/@0/solde_credit', '1250.38€')

        self.assert_json_equal('', 'report_1/@1/designation', '[401] 401')
        self.assert_json_equal('', 'report_1/@1/total_debit', '258.02€')
        self.assert_json_equal('', 'report_1/@1/total_credit', '336.26€')
        self.assert_json_equal('', 'report_1/@1/solde_debit', '')
        self.assert_json_equal('', 'report_1/@1/solde_credit', '78.24€')

        self.assert_json_equal('', 'report_1/@2/designation', '[411] 411')
        self.assert_json_equal('', 'report_1/@2/total_debit', '230.62€')
        self.assert_json_equal('', 'report_1/@2/total_credit', '70.64€')
        self.assert_json_equal('', 'report_1/@2/solde_debit', '159.98€')
        self.assert_json_equal('', 'report_1/@2/solde_credit', '')

        self.assert_json_equal('', 'report_1/@3/designation', '[512] 512')
        self.assert_json_equal('', 'report_1/@3/total_debit', '1206.57€')
        self.assert_json_equal('', 'report_1/@3/total_credit', '76.28€')
        self.assert_json_equal('', 'report_1/@3/solde_debit', '1130.29€')
        self.assert_json_equal('', 'report_1/@3/solde_credit', '')

        self.assert_json_equal('', 'report_1/@4/designation', '[531] 531')
        self.assert_json_equal('', 'report_1/@4/total_debit', '114.45€')
        self.assert_json_equal('', 'report_1/@4/total_credit', '194.08€')
        self.assert_json_equal('', 'report_1/@4/solde_debit', '')
        self.assert_json_equal('', 'report_1/@4/solde_credit', '79.63€')

        self.assert_json_equal('', 'report_1/@5/designation', '[601] 601')
        self.assert_json_equal('', 'report_1/@5/total_debit', '78.24€')
        self.assert_json_equal('', 'report_1/@5/total_credit', '0.00€')
        self.assert_json_equal('', 'report_1/@5/solde_debit', '78.24€')
        self.assert_json_equal('', 'report_1/@5/solde_credit', '')

        self.assert_json_equal('', 'report_1/@6/designation', '[602] 602')
        self.assert_json_equal('', 'report_1/@6/total_debit', '63.94€')
        self.assert_json_equal('', 'report_1/@6/total_credit', '0.00€')
        self.assert_json_equal('', 'report_1/@6/solde_debit', '63.94€')
        self.assert_json_equal('', 'report_1/@6/solde_credit', '')

        self.assert_json_equal('', 'report_1/@7/designation', '[607] 607')
        self.assert_json_equal('', 'report_1/@7/total_debit', '194.08€')
        self.assert_json_equal('', 'report_1/@7/total_credit', '0.00€')
        self.assert_json_equal('', 'report_1/@7/solde_debit', '194.08€')
        self.assert_json_equal('', 'report_1/@7/solde_credit', '')

        self.assert_json_equal('', 'report_1/@8/designation', '[627] 627')
        self.assert_json_equal('', 'report_1/@8/total_debit', '12.34€')
        self.assert_json_equal('', 'report_1/@8/total_credit', '0.00€')
        self.assert_json_equal('', 'report_1/@8/solde_debit', '12.34€')
        self.assert_json_equal('', 'report_1/@8/solde_credit', '')

        self.assert_json_equal('', 'report_1/@9/designation', '[707] 707')
        self.assert_json_equal('', 'report_1/@9/total_debit', '0.00€')
        self.assert_json_equal('', 'report_1/@9/total_credit', '230.62€')
        self.assert_json_equal('', 'report_1/@9/solde_debit', '')
        self.assert_json_equal('', 'report_1/@9/solde_credit', '230.62€')

        self.assert_json_equal('', 'report_1/@10/designation', '[860] 860')
        self.assert_json_equal('', 'report_1/@10/total_debit', '0.00€')
        self.assert_json_equal('', 'report_1/@10/total_credit', '1234.00€')
        self.assert_json_equal('', 'report_1/@10/solde_debit', '')
        self.assert_json_equal('', 'report_1/@10/solde_credit', '1234.00€')

        self.assert_json_equal('', 'report_1/@11/designation', '[870] 870')
        self.assert_json_equal('', 'report_1/@11/total_debit', '1234.00€')
        self.assert_json_equal('', 'report_1/@11/total_credit', '0.00€')
        self.assert_json_equal('', 'report_1/@11/solde_debit', '1234.00€')
        self.assert_json_equal('', 'report_1/@11/solde_credit', '')

    def test_fiscalyear_trialbalance_filter(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {'begin': '2015-02-22', 'end': '2015-02-28'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self._check_result_with_filter()

    def test_fiscalyear_trialbalance_third(self):
        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {'filtercode': '4', 'with_third': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self.assert_count_equal('report_1', 6)

        self.factory.xfer = FiscalYearTrialBalance()
        self.calljson('/diacamma.accounting/fiscalYearTrialBalance', {'filtercode': '4', 'with_third': 1, 'only_nonull': 1}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearTrialBalance')
        self.assert_count_equal('report_1', 3)

    def test_fiscalyear_trialbalance_print(self):
        self.factory.xfer = FiscalYearReportPrint()
        self.calljson('/diacamma.accounting/fiscalYearReportPrint', {'classname': 'FiscalYearTrialBalance', "PRINT_MODE": 3}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'fiscalYearReportPrint')
        self.save_pdf()

    def test_export(self):
        self.assertFalse(exists(get_user_path('accounting', 'fiscalyear_export_1.xml')))
        self.factory.xfer = FiscalYearExport()
        self.calljson('/diacamma.accounting/fiscalYearExport', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearExport')
        self.assertTrue(exists(get_user_path('accounting', 'fiscalyear_export_1.xml')))

        self.assertFalse(exists(get_user_path('accounting', 'fiscalyear_export_2.xml')))
        self.factory.xfer = FiscalYearExport()
        self.calljson('/diacamma.accounting/fiscalYearExport', {'fiscalyear': '2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearExport')
        self.assertFalse(exists(get_user_path('accounting', 'fiscalyear_export_2.xml')))
        self.assert_json_equal('', 'code', '3')
        self.assert_json_equal('', 'message', "Cet exercice n'a pas d'écriture validée !")

    def test_search_advanced(self):
        CustomField.objects.create(modelname='accounting.Third', name='categorie', kind=4, args="{'list':['---','petit','moyen','gros']}")
        CustomField.objects.create(modelname='accounting.Third', name='value', kind=1, args="{'min':0,'max':100}")
        third = Third.objects.get(id=7)
        third.set_custom_values({'custom_2': '4'})

        self.factory.xfer = EntryAccountSearch()
        self.calljson('/diacamma.accounting/entryAccountSearch', {}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountSearch')
        self.assert_count_equal('entryline', 25)

        self.factory.xfer = EntryAccountSearch()
        self.calljson('/diacamma.accounting/entryAccountSearch', {'CRITERIA': 'third.custom_2||1||4'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountSearch')
        self.assert_count_equal('entryline', 2)
