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
from importlib import import_module
from base64 import b64decode

from django.utils import six

from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr, fill_entries_fr, set_accounting_system, add_entry
from diacamma.accounting.views_accounts import ChartsAccountList, ChartsAccountDel, ChartsAccountShow, ChartsAccountAddModify, ChartsAccountListing, ChartsAccountImportFiscalYear
from diacamma.accounting.views_accounts import FiscalYearBegin, FiscalYearClose, FiscalYearReportLastYear
from diacamma.accounting.views_entries import EntryAccountEdit, EntryAccountList
from diacamma.accounting.models import FiscalYear
from diacamma.accounting.views import ThirdList
from diacamma.accounting.views_budget import BudgetList, BudgetAddModify, BudgetDel
from diacamma.payoff.test_tools import PaymentTest


class ChartsAccountTest(LucteriosTest):

    def setUp(self):
        LucteriosTest.setUp(self)
        set_accounting_system()
        initial_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)
        rmtree(get_user_dir(), True)

    def test_all(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_grid_equal('chartsaccount', {"code": "code", "name": "nom", "last_year_total": "total de l'exercice précédent", "current_total": "total exercice", "current_validated": "total validé"}, 17)  # nb=5
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 230.62€ - {[b]}Charge :{[/b]} 348.60€ = {[b]}Résultat :{[/b]} -117.98€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')

    def test_asset(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 3)
        self.assert_json_equal('', 'chartsaccount/@0/code', '411')
        self.assert_json_equal('', 'chartsaccount/@0/name', '411')
        self.assert_json_equal('', 'chartsaccount/@0/last_year_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_total', '{[font color="blue"]}Débit: 159.98€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_validated', '{[font color="blue"]}Débit: 125.97€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@1/code', '512')
        self.assert_json_equal('', 'chartsaccount/@1/name', '512')
        self.assert_json_equal('', 'chartsaccount/@1/last_year_total', '{[font color="blue"]}Débit: 1135.93€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@1/current_total', '{[font color="blue"]}Débit: 1130.29€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@1/current_validated', '{[font color="blue"]}Débit: 1130.29€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@2/code', '531')
        self.assert_json_equal('', 'chartsaccount/@2/name', '531')
        self.assert_json_equal('', 'chartsaccount/@2/last_year_total', '{[font color="blue"]}Débit: 114.45€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@2/current_total', '{[font color="green"]}Crédit: 79.63€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@2/current_validated', '{[font color="blue"]}Débit: 114.45€{[/font]}')

    def test_liability(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 1)
        self.assert_json_equal('', 'chartsaccount/@0/code', '401')
        self.assert_json_equal('', 'chartsaccount/@0/name', '401')
        self.assert_json_equal('', 'chartsaccount/@0/last_year_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_total', '{[font color="green"]}Crédit: 78.24€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_validated', '{[font color="green"]}Crédit: 0.00€{[/font]}')

    def test_equity(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 5)
        self.assert_json_equal('', 'chartsaccount/@0/code', '106')
        self.assert_json_equal('', 'chartsaccount/@0/name', '106')
        self.assert_json_equal('', 'chartsaccount/@0/last_year_total', '{[font color="green"]}Crédit: 1250.38€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_total', '{[font color="green"]}Crédit: 1250.38€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_validated', '{[font color="green"]}Crédit: 1250.38€{[/font]}')

    def test_revenue(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '3'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 3)
        self.assert_json_equal('', 'chartsaccount/@2/code', '707')
        self.assert_json_equal('', 'chartsaccount/@2/name', '707')
        self.assert_json_equal('', 'chartsaccount/@2/last_year_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@2/current_total', '{[font color="green"]}Crédit: 230.62€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@2/current_validated', '{[font color="green"]}Crédit: 196.61€{[/font]}')

    def test_expense(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '4'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 5)
        self.assert_json_equal('', 'chartsaccount/@0/code', '601')
        self.assert_json_equal('', 'chartsaccount/@0/name', '601')
        self.assert_json_equal('', 'chartsaccount/@0/last_year_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_total', '{[font color="blue"]}Débit: 78.24€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_validated', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@1/code', '602')
        self.assert_json_equal('', 'chartsaccount/@1/name', '602')
        self.assert_json_equal('', 'chartsaccount/@1/last_year_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@1/current_total', '{[font color="blue"]}Débit: 63.94€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@1/current_validated', '{[font color="blue"]}Débit: 63.94€{[/font]}')

    def test_contraaccounts(self):
        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '5'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 0)

    def test_show(self):
        self.factory.xfer = ChartsAccountShow()
        self.calljson('/diacamma.accounting/chartsAccountShow',
                      {'year': '1', 'type_of_account': '-1', 'chartsaccount': '10'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountShow')
        self.assert_count_equal('', 5)
        self.assert_json_equal('LABELFORM', 'code', '707')
        self.assert_json_equal('LABELFORM', 'name', '707')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Produit')
        self.assert_grid_equal('entryaccount', {"num": "N°", "date_entry": "date d'écriture", "date_value": "date de pièce", "description": "description"}, 3)  # nb=5
        self.assert_json_equal('', 'entryaccount/@0/num', '4')
        self.assert_json_equal('', 'entryaccount/@0/date_value', '2015-02-21')
        description = self.json_data['entryaccount'][0]['description']
        self.assertTrue('vente 1' in description, description)
        self.assertTrue('70.64€' in description, description)

        self.assert_json_equal('', 'entryaccount/@1/num', '6')
        self.assert_json_equal('', 'entryaccount/@1/date_value', '2015-02-21')
        description = self.json_data['entryaccount'][1]['description']
        self.assertTrue('vente 2' in description, description)
        self.assertTrue('125.97€' in description, description)

        self.assert_json_equal('', 'entryaccount/@2/num', '---')
        self.assert_json_equal('', 'entryaccount/@2/date_value', '2015-02-24')
        description = self.json_data['entryaccount'][2]['description']
        self.assertTrue('vente 3' in description, description)
        self.assertTrue('34.01€' in description, description)

    def test_delete(self):
        self.factory.xfer = ChartsAccountDel()
        self.calljson('/diacamma.accounting/chartsAccountDel',
                      {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '5', 'chartsaccount': '10'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'chartsAccountDel')
        self.assert_json_equal('', 'message', "Impossible de supprimer cet enregistrement: il est associé avec d'autres sous-enregistrements")
        self.factory.xfer = ChartsAccountDel()
        self.calljson('/diacamma.accounting/chartsAccountDel',
                      {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '5', 'chartsaccount': '9'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'chartsAccountDel')

    def test_add(self):
        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '')
        self.assert_json_equal('EDIT', 'name', '')
        self.assert_json_equal('LABELFORM', 'type_of_account', '---')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'code': '2301'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '2301')
        self.assert_json_equal('EDIT', 'name', 'Immobilisations en cours')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Actif')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'code': '3015'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '3015!')
        self.assert_json_equal('EDIT', 'name', '')
        self.assert_json_equal('LABELFORM', 'type_of_account', '---')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}Code invalide !{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'code': 'abcd'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', 'abcd!')
        self.assert_json_equal('EDIT', 'name', '')
        self.assert_json_equal('LABELFORM', 'type_of_account', '---')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}Code invalide !{[/font]}{[/center]}")

    def test_modify(self):
        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'chartsaccount': '10'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '707')
        self.assert_json_equal('EDIT', 'name', '707')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Produit')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'chartsaccount': '10', 'code': '7061'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '7061')
        self.assert_json_equal('EDIT', 'name', '707')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Produit')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'chartsaccount': '10', 'code': '3015'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '3015!')
        self.assert_json_equal('EDIT', 'name', '707')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Produit')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}Code invalide !{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'chartsaccount': '10', 'code': 'abcd'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', 'abcd!')
        self.assert_json_equal('EDIT', 'name', '707')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Produit')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}Code invalide !{[/font]}{[/center]}")

        self.factory.xfer = ChartsAccountAddModify()
        self.calljson('/diacamma.accounting/chartsAccountAddModify',
                      {'year': '1', 'type_of_account': '-1', 'chartsaccount': '10', 'code': '6125'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountAddModify')
        self.assert_count_equal('', 5)
        self.assert_json_equal('EDIT', 'code', '6125!')
        self.assert_json_equal('EDIT', 'name', '707')
        self.assert_json_equal('LABELFORM', 'type_of_account', 'Produit')
        self.assert_json_equal('LABELFORM', 'error_code', "{[center]}{[font color='red']}Changement non permis !{[/font]}{[/center]}")

    def test_listing(self):
        self.factory.xfer = ChartsAccountListing()
        self.calljson('/diacamma.accounting/chartsAccountListing',
                      {'year': '1', 'type_of_account': '-1', 'PRINT_MODE': '4', 'MODEL': 6}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'chartsAccountListing')
        csv_value = b64decode(
            six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 25, str(content_csv))
        self.assertEqual(content_csv[1].strip()[:27], '"Liste de plan comptable - ')
        self.assertEqual(content_csv[4].strip(), '"code";"nom";"total de l\'exercice précédent";"total exercice";"total validé";')
        self.assertEqual(content_csv[5].strip(), '"106";"106";"Crédit: 1250.38€";"Crédit: 1250.38€";"Crédit: 1250.38€";')
        self.assertEqual(content_csv[12].strip(), '"512";"512";"Débit: 1135.93€";"Débit: 1130.29€";"Débit: 1130.29€";')
        self.assertEqual(content_csv[13].strip(), '"531";"531";"Débit: 114.45€";"Crédit: 79.63€";"Débit: 114.45€";')

        self.factory.xfer = ChartsAccountListing()
        self.calljson('/diacamma.accounting/chartsAccountListing',
                      {'year': '1', 'type_of_account': '4', 'PRINT_MODE': '4', 'MODEL': 6}, False)
        self.assert_observer('core.print', 'diacamma.accounting', 'chartsAccountListing')
        csv_value = b64decode(
            six.text_type(self.response_json['print']['content'])).decode("utf-8")
        content_csv = csv_value.split('\n')
        self.assertEqual(len(content_csv), 13, str(content_csv))

    def test_budget(self):
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

        self.factory.xfer = BudgetAddModify()
        self.calljson('/diacamma.accounting/budgetAddModify', {'year': '1', 'budget_expense': 'C602'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetAddModify')
        self.assert_count_equal('', 4)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_json_equal('', 'code', '602')
        self.assert_json_equal('', 'debit_val', '7.35')
        self.assert_json_equal('', 'credit_val', '0.00')

        self.factory.xfer = BudgetAddModify()
        self.calljson('/diacamma.accounting/budgetAddModify', {'year': '1', 'budget_expense': 'C602', 'code': '602', 'debit_val': '19.64', 'credit_val': '0.00', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetAddModify')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('budget_expense', 3)
        self.assert_json_equal('', 'budget_expense/@1/budget', '[602] 602')
        self.assert_json_equal('', 'budget_expense/@1/montant', '{[font color="blue"]}Débit: 19.64€{[/font]}')
        self.assert_json_equal('LABELFORM', 'result', '157.27€')

        self.factory.xfer = BudgetAddModify()
        self.calljson('/diacamma.accounting/budgetAddModify', {'year': '1', 'code': '607', 'debit_val': '92.73', 'credit_val': '0.00', 'SAVE': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetAddModify')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('budget_expense', 4)
        self.assert_json_equal('', 'budget_expense/@3/budget', '[607] 607')
        self.assert_json_equal('', 'budget_expense/@3/montant', '{[font color="blue"]}Débit: 92.73€{[/font]}')
        self.assert_json_equal('LABELFORM', 'result', '64.54€')

        self.factory.xfer = BudgetDel()
        self.calljson('/diacamma.accounting/budgetDel', {'year': '1', 'budget_expense': 'C604', 'CONFIRME': 'YES'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'budgetDel')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('budget_expense', 3)
        self.assert_json_equal('LABELFORM', 'result', '70.78€')

        self.factory.xfer = BudgetList()
        self.calljson('/diacamma.accounting/budgetList', {'year': '1', 'readonly': True}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'budgetList')
        self.assert_count_equal('', 6)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_count_equal('budget_revenue', 2)
        self.assert_count_equal('#budget_revenue/actions', 0)
        self.assert_count_equal('budget_expense', 3)
        self.assert_count_equal('#budget_expense/actions', 0)
        self.assert_json_equal('LABELFORM', 'result', '70.78€')


class FiscalYearWorkflowTest(PaymentTest):

    def setUp(self):
        # BudgetList.url_text
        LucteriosTest.setUp(self)
        set_accounting_system()
        initial_thirds_fr()
        default_compta_fr()
        fill_entries_fr(1)
        rmtree(get_user_dir(), True)

    def test_begin_simple(self):
        self.assertEqual(
            FiscalYear.objects.get(id=1).status, 0)

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_action_equal(self.json_actions[0], ('Commencer', 'images/ok.png', 'diacamma.accounting', 'fiscalYearBegin', 0, 1, 1))

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.dialogbox', 'diacamma.accounting', 'fiscalYearBegin')
        self.assert_json_equal('', 'text', "Voulez-vous commencer 'Exercice du 1 janvier 2015 au 31 décembre 2015", True)

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assertEqual(len(self.json_actions), 4)
        self.assert_action_equal(self.json_actions[0], ('Clôture', 'images/ok.png', 'diacamma.accounting', 'fiscalYearClose', 0, 1, 1))

    def test_begin_lastyearnovalid(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)
        new_entry = add_entry(1, 1, '2015-04-11', 'Report à nouveau aussi', '-1|1|0|37.61|0|0|None|\n-2|2|0|-37.61|0|0|None|', False)

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearBegin')
        self.assert_json_equal('', 'message', "Des écritures de report à nouveau ne sont pas validées !")

        new_entry.closed()

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)

    def test_begin_withbenef(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)
        add_entry(1, 1, '2015-04-11', 'Report à nouveau bénèf', '-1|16|0|123.45|0|0|None|\n-2|2|0|123.45|0|0|None|', True)

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('chartsaccount', 5)
        self.assert_json_equal('', 'chartsaccount/@0/code', '106')
        self.assert_json_equal('', 'chartsaccount/@0/last_year_total', '{[font color="green"]}Crédit: 1250.38€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@3/code', '120')
        self.assert_json_equal('', 'chartsaccount/@3/last_year_total', '{[font color="green"]}Crédit: 123.45€{[/font]}')

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearBegin')
        self.assert_count_equal('', 4)
        self.assert_json_equal('LABELFORM', 'info', "{[i]}Vous avez un bénéfice de 123.45€.{[br/]}", True)
        self.assert_json_equal('SELECT', 'profit_account', '5')
        self.assert_select_equal('profit_account', 3)  # nb=3
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'profit_account': '5', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '1', 'type_of_account': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('chartsaccount', 5)
        self.assert_json_equal('', 'chartsaccount/@0/code', '106')
        self.assert_json_equal('', 'chartsaccount/@0/last_year_total', '{[font color="green"]}Crédit: 1250.38€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@0/current_total', '{[font color="green"]}Crédit: 1373.83€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@3/code', '120')
        self.assert_json_equal('', 'chartsaccount/@3/last_year_total', '{[font color="green"]}Crédit: 123.45€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@3/current_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')

    def test_begin_dont_add_report(self):
        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin',
                      {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 4)
        self.assert_select_equal('journal', 4)  # nb=4
        self.assert_json_equal('SELECT', 'journal', '2')
        self.assertEqual(len(self.json_actions), 2)

    def test_import_charsaccount(self):
        import_module("diacamma.asso.views")
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0,
                                  last_fiscalyear=FiscalYear.objects.get(id=1))
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)
        self.assertEqual(FiscalYear.objects.get(id=2).status, 0)

        self.factory.xfer = ChartsAccountImportFiscalYear()
        self.calljson('/diacamma.accounting/chartsAccountImportFiscalYear',
                      {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'chartsAccountImportFiscalYear')
        self.assert_json_equal('', 'message', "Cet exercice n'a pas d'exercice précédent !")

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList', {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('chartsaccount', 17)
        self.assert_count_equal('#chartsaccount/actions', 5)

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList', {'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('chartsaccount', 0)
        self.assert_count_equal('#chartsaccount/actions', 6)
        self.assert_action_equal('#chartsaccount/actions/@3',
                                 ('importer', None, 'diacamma.accounting', 'chartsAccountImportFiscalYear', 0, 1, 1))

        self.factory.xfer = ChartsAccountImportFiscalYear()
        self.calljson('/diacamma.accounting/chartsAccountImportFiscalYear',
                      {'CONFIRME': 'YES', 'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'chartsAccountImportFiscalYear')

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('chartsaccount', 17)

        self.factory.xfer = ChartsAccountImportFiscalYear()
        self.calljson('/diacamma.accounting/chartsAccountImportFiscalYear',
                      {'CONFIRME': 'YES', 'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'chartsAccountImportFiscalYear')

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList',
                      {'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('chartsaccount', 17)

    def test_close(self):
        self.assertEqual(FiscalYear.objects.get(id=1).status, 0)
        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose', {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearClose')
        self.assert_json_equal('', 'message', "Cet exercice n'est pas 'en cours' !")

        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin', {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)

        self.factory.xfer = ThirdList()
        self.calljson('/diacamma.accounting/thirdList', {'show_filter': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'thirdList')
        self.assert_json_equal('', 'third/@1/contact', 'Dalton Jack')
        self.assert_json_equal('', 'third/@1/total', '0.00€')
        self.assert_json_equal('', 'third/@3/contact', 'Dalton William')
        self.assert_json_equal('', 'third/@3/total', '-125.97€')
        self.assert_json_equal('', 'third/@6/contact', 'Minimum')
        self.assert_json_equal('', 'third/@6/total', '-34.01€')
        self.check_account(1, '411', 159.98)
        self.check_account(1, '401', 78.24)

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose', {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'fiscalYearClose')
        self.assert_json_equal('', 'message', "Cet exercice a des écritures non-validées et pas d'exercice suivant !")

        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=FiscalYear.objects.get(id=1))

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose', {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'fiscalYearClose')
        text_value = self.json_data['info']

        self.assertTrue('Voulez-vous cloturer cet exercice ?' in text_value, text_value)
        self.assertTrue('4 écritures ne sont pas validées' in text_value, text_value)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 23)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 230.62€ - {[b]}Charge :{[/b]} 348.60€ = {[b]}Résultat :{[/b]} -117.98€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '2', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose', {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 18)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 196.61€ - {[b]}Charge :{[/b]} 76.28€ = {[b]}Résultat :{[/b]} 120.33€{[br/]}{[b]}Trésorerie :{[/b]} 1244.74€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '5', 'filter': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 5)
        self.assert_json_equal('', 'entryline/@2/designation_ref', "Cloture d'exercice - Résultat")
        self.assert_json_equal('', 'entryline/@2/entry_account', "[120] 120")
        self.assert_json_equal('', 'entryline/@2/credit', "{[font color=\"green\"]}120.33€{[/font]}")
        self.assert_json_equal('', 'entryline/@2/link', "---")

        self.assert_json_equal('', 'entryline/@3/designation_ref', "Cloture d'exercice - Tiers")
        self.assert_json_equal('', 'entryline/@3/entry_account', "[411] 411")
        self.assert_json_equal('', 'entryline/@3/debit', "{[font color=\"blue\"]}125.97€{[/font]}")
        self.assert_json_equal('', 'entryline/@3/link', "---")
        self.assert_json_equal('', 'entryline/@4/designation_ref', "Cloture d'exercice - Tiers{[br/]}vente 2")
        self.assert_json_equal('', 'entryline/@4/entry_account', "[411 Dalton William]")
        self.assert_json_equal('', 'entryline/@4/credit', "{[font color=\"green\"]}125.97€{[/font]}")
        self.assert_json_equal('', 'entryline/@4/link', "E")

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '2', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 8)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 34.01€ - {[b]}Charge :{[/b]} 272.32€ = {[b]}Résultat :{[/b]} -238.31€{[br/]}{[b]}Trésorerie :{[/b]} -194.08€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList', {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assert_count_equal('chartsaccount', 17)
        self.assert_json_equal('', 'chartsaccount/@3/code', '120')
        self.assert_json_equal('', 'chartsaccount/@3/current_total', '{[font color="green"]}Crédit: 120.33€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@5/code', '401')
        self.assert_json_equal('', 'chartsaccount/@5/current_total', '{[font color="green"]}Crédit: 0.00€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@6/code', '411')
        self.assert_json_equal('', 'chartsaccount/@6/current_total', '{[font color="blue"]}Débit: 125.97€{[/font]}')

    def test_import_lastyear(self):
        FiscalYear.objects.create(begin='2016-01-01', end='2016-12-31', status=0, last_fiscalyear=FiscalYear.objects.get(id=1))
        self.factory.xfer = FiscalYearBegin()
        self.calljson('/diacamma.accounting/fiscalYearBegin', {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearBegin')
        self.assertEqual(FiscalYear.objects.get(id=1).status, 1)
        self.factory.xfer = FiscalYearClose()
        self.calljson('/diacamma.accounting/fiscalYearClose', {'CONFIRME': 'YES', 'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearClose')

        self.assertEqual(FiscalYear.objects.get(id=1).status, 2)
        self.assertEqual(FiscalYear.objects.get(id=2).status, 0)

        self.factory.xfer = FiscalYearReportLastYear()
        self.calljson('/diacamma.accounting/fiscalYearReportLastYear', {'CONFIRME': 'YES', 'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'fiscalYearReportLastYear')
        self.assertEqual(FiscalYear.objects.get(id=2).status, 0)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '2', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 15)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 34.01€ - {[b]}Charge :{[/b]} 272.32€ = {[b]}Résultat :{[/b]} -238.31€{[br/]}{[b]}Trésorerie :{[/b]} 1050.66€ - {[b]}Validé :{[/b]} 1244.74€{[/center]}')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '2', 'journal': '1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 7)

        self.assert_json_equal('', 'entryline/@0/designation_ref', "Report à nouveau - Bilan")
        self.assert_json_equal('', 'entryline/@0/entry_account', "[106] 106")
        self.assert_json_equal('', 'entryline/@0/link', "---")
        self.assert_json_equal('', 'entryline/@1/designation_ref', "Report à nouveau - Bilan")
        self.assert_json_equal('', 'entryline/@1/entry_account', "[120] 120")
        self.assert_json_equal('', 'entryline/@1/link', "---")
        self.assert_json_equal('', 'entryline/@2/designation_ref', "Report à nouveau - Bilan")
        self.assert_json_equal('', 'entryline/@2/entry_account', "[411] 411")
        self.assert_json_equal('', 'entryline/@2/link', "---")
        self.assert_json_equal('', 'entryline/@3/designation_ref', "Report à nouveau - Bilan")
        self.assert_json_equal('', 'entryline/@3/entry_account', "[512] 512")
        self.assert_json_equal('', 'entryline/@3/link', "---")
        self.assert_json_equal('', 'entryline/@4/designation_ref', "Report à nouveau - Bilan")
        self.assert_json_equal('', 'entryline/@4/entry_account', "[531] 531")
        self.assert_json_equal('', 'entryline/@4/link', "---")

        self.assert_json_equal('', 'entryline/@5/designation_ref', "Report à nouveau - Dette tiers")
        self.assert_json_equal('', 'entryline/@5/entry_account', "[411] 411")
        self.assert_json_equal('', 'entryline/@5/credit', "{[font color=\"green\"]}125.97€{[/font]}")
        self.assert_json_equal('', 'entryline/@5/link', "---")
        self.assert_json_equal('', 'entryline/@6/designation_ref', "Report à nouveau - Dette tiers{[br/]}vente 2")
        self.assert_json_equal('', 'entryline/@6/entry_account', "[411 Dalton William]")
        self.assert_json_equal('', 'entryline/@6/debit', "{[font color=\"blue\"]}125.97€{[/font]}")
        self.assert_json_equal('', 'entryline/@6/link', "---")

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList', {'year': '2', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assert_count_equal('', 8)
        self.assertEqual(len(self.json_actions), 4)
        self.assert_count_equal('chartsaccount', 9)
        self.assert_json_equal('', 'chartsaccount/@1/code', '120')
        self.assert_json_equal('', 'chartsaccount/@1/current_total', '{[font color="green"]}Crédit: 120.33€{[/font]}')
        self.assert_json_equal('', 'chartsaccount/@3/code', '411')
        self.assert_json_equal('', 'chartsaccount/@3/current_total', '{[font color="blue"]}Débit: 159.98€{[/font]}')

        self.factory.xfer = ChartsAccountList()
        self.calljson('/diacamma.accounting/chartsAccountList', {'year': '1', 'type_of_account': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'chartsAccountList')
        self.assertEqual(len(self.json_actions), 3)
