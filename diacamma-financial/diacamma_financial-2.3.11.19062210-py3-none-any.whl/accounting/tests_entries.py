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
from datetime import date

from django.utils import formats

from lucterios.framework.test import LucteriosTest
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.views_entries import EntryAccountList, \
    EntryAccountEdit, EntryAccountAfterSave, EntryLineAccountAdd, \
    EntryLineAccountEdit, EntryAccountValidate, EntryAccountClose, \
    EntryAccountReverse, EntryAccountCreateLinked, EntryAccountLink, \
    EntryAccountDel, EntryAccountOpenFromLine, EntryAccountShow, \
    EntryLineAccountDel, EntryAccountUnlock
from diacamma.accounting.test_tools import default_compta_fr, initial_thirds_fr,\
    fill_entries_fr
from diacamma.accounting.models import EntryAccount, CostAccounting
from diacamma.accounting.views_other import CostAccountingAddModify


class EntryTest(LucteriosTest):

    def setUp(self):
        initial_thirds_fr()
        LucteriosTest.setUp(self)
        default_compta_fr()
        rmtree(get_user_dir(), True)

    def test_empty_list(self):
        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {}, False)
        self.assert_observer(
            'core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_json_equal('SELECT', 'year', '1')
        self.assert_select_equal('year', 1)  # nb=1
        self.assert_json_equal('SELECT', 'journal', '4')
        self.assert_select_equal('journal', 6)  # nb=6
        self.assert_json_equal('SELECT', 'filter', '1')
        self.assert_select_equal('filter', 5)  # nb=5
        self.assert_count_equal('entryline', 0)
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_add_entry(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 4)
        self.assert_json_equal('SELECT', 'journal', '2')
        self.assert_json_equal('DATE', 'date_value', '2015-12-31')
        self.assert_json_equal('EDIT', 'designation', '')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountAfterSave")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['entryaccount'], 1)
        self.assertEqual(len(self.json_context), 4)
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")
        self.assertEqual(self.json_context['date_value'], "2015-02-13")
        self.assertEqual(self.json_context['designation'], "un plein cadie")

        self.factory.xfer = EntryAccountAfterSave()
        self.calljson('/diacamma.accounting/entryAccountAfterSave', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                     'date_value': '2015-02-13', 'designation': 'un plein cadie', 'entryaccount': "1"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountAfterSave')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(self.response_json['action']['params'], None)
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], "1")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")

    def test_add_entry_bad_date(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2017-04-20', 'designation': 'Truc'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.assertEqual(self.response_json['action']['params']['entryaccount'], 1)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)
        self.assert_json_equal('SELECT', 'journal', '2')
        self.assert_json_equal('DATE', 'date_value', '2015-12-31')
        self.assert_json_equal('EDIT', 'designation', 'Truc')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2010-04-20', 'designation': 'Machin'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.assertEqual(self.response_json['action']['params']['entryaccount'], 2)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)
        self.assert_json_equal('SELECT', 'journal', '2')
        self.assert_json_equal('DATE', 'date_value', '2015-01-01')
        self.assert_json_equal('EDIT', 'designation', 'Machin')
        self.assertEqual(len(self.json_actions), 2)

    def test_add_line_third(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)

        self.assert_json_equal('SELECT', 'journal', '2')
        self.assert_json_equal('DATE', 'date_value', '2015-02-13')
        self.assert_json_equal('EDIT', 'designation', 'un plein cadie')
        self.assert_count_equal('entrylineaccount_serial', 0)
        self.assert_json_equal('EDIT', 'num_cpt_txt', '')
        self.assert_json_equal('SELECT', 'num_cpt', 'None')
        self.assert_select_equal('num_cpt', 0)  # nb=0
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'num_cpt_txt': '401'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 16)

        self.assert_json_equal('EDIT', 'num_cpt_txt', '401')
        self.assert_json_equal('SELECT', 'num_cpt', '4')
        self.assert_select_equal('num_cpt', 1)  # nb=1
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assert_json_equal('SELECT', 'third', '0')
        self.assert_select_equal('third', 5)  # nb=5
        self.assert_count_equal('entrylineaccount_serial', 0)
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '2', 'entryaccount': '1', 'num_cpt_txt': '401',
                                                                   'num_cpt': '4', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], "1")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)

        self.assert_count_equal('entrylineaccount_serial', 1)
        self.assert_json_equal('', 'entrylineaccount_serial/@0/entry_account', '[401] 401')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/debit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/costaccounting', '---')
        self.assertEqual(len(self.json_actions), 2)

    def test_add_line_revenue(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|", 'num_cpt_txt': '60'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 16)

        self.assert_count_equal('entrylineaccount_serial', 1)
        self.assert_json_equal('EDIT', 'num_cpt_txt', '60')
        self.assert_json_equal('SELECT', 'num_cpt', '11')
        self.assert_select_equal('num_cpt', 4)  # nb=4
        self.assert_json_equal('FLOAT', 'debit_val', '152.34')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|",
                                                                   'num_cpt_txt': '60', 'num_cpt': '12', 'debit_val': '152.34', 'credit_val': '0.0'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], '1')
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|\n-2|12|0|152.340000|0|0|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)

        self.assert_count_equal('entrylineaccount_serial', 2)
        self.assert_json_equal('', 'entrylineaccount_serial/@0/entry_account', '[401] 401')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/debit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/debit', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/credit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/reference', '---')
        self.assertEqual(len(self.json_actions), 2)
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryAccountValidate")

    def test_add_line_payoff(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '3',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '3', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 16)

        self.assert_count_equal('entrylineaccount_serial', 1)
        self.assert_json_equal('EDIT', 'num_cpt_txt', '5')
        self.assert_json_equal('SELECT', 'num_cpt', '2')
        self.assert_select_equal('num_cpt', 2)  # nb=2
        self.assert_json_equal('FLOAT', 'debit_val', '152.34')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assert_json_equal('EDIT', 'reference', '')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '3', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|",
                                                                   'num_cpt_txt': '5', 'num_cpt': '3', 'debit_val': '152.34', 'credit_val': '0.0', 'reference': 'aaabbb'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], '1')
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "3")

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|0|152.340000|0|0|None|\n-2|3|0|152.340000|0|0|aaabbb|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)

        self.assert_count_equal('entrylineaccount_serial', 2)
        self.assert_json_equal('', 'entrylineaccount_serial/@0/entry_account', '[401] 401')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/debit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/costaccounting', '---')

        self.assert_json_equal('', 'entrylineaccount_serial/@1/entry_account', '[531] 531')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/debit', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/credit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/reference', 'aaabbb')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/costaccounting', '---')
        self.assertEqual(len(self.json_actions), 2)
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryAccountValidate")

    def test_change_line_third(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryLineAccountEdit()
        self.calljson('/diacamma.accounting/entryLineAccountEdit', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                    'serial_entry': "-1|4|0|152.340000|0|0|None|\n-2|12|0|152.340000|0|0|None|", 'entrylineaccount_serial': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryLineAccountEdit')
        self.assert_count_equal('', 5)

        self.assert_json_equal('LABELFORM', 'account', '[401] 401')
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')
        self.assert_json_equal('FLOAT', 'credit_val', '152.34')
        self.assert_json_equal('SELECT', 'third', '0')
        self.assert_select_equal('third', 5)  # nb=5
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryLineAccountAdd")
        self.assertEqual(len(self.json_actions[0]['params']), 1)
        self.assertEqual(self.json_actions[0]['params']['num_cpt'], 4)

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                   'serial_entry': "-1|4|0|152.340000|0|0|None|\n-2|12|0|152.340000|0|0|None|", 'debit_val': '0.0',
                                                                   'credit_val': '152.34', 'entrylineaccount_serial': '-1', 'third': '3', 'num_cpt': '4'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], '1')
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|0|0|None|\n-3|4|3|152.340000|0|0|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)

        self.assert_count_equal('entrylineaccount_serial', 2)
        self.assert_json_equal('', 'entrylineaccount_serial/@0/entry_account', '[602] 602')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/debit', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/credit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/debit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/costaccounting', '---')
        self.assertEqual(len(self.json_actions), 2)
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryAccountValidate")

        self.factory.xfer = EntryLineAccountEdit()
        self.calljson('/diacamma.accounting/entryLineAccountEdit', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                    'serial_entry': "-1|4|3|152.340000|0|0|None|\n-2|12|0|152.340000|0|0|None|", 'entrylineaccount_serial': '-1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryLineAccountEdit')
        self.assert_count_equal('', 5)

        self.assert_json_equal('LABELFORM', 'account', '[401] 401')
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')
        self.assert_json_equal('FLOAT', 'credit_val', '152.34')
        self.assert_json_equal('SELECT', 'third', '3')
        self.assert_select_equal('third', 5)  # nb=5
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryLineAccountAdd")
        self.assertEqual(len(self.json_actions[0]['params']), 1)
        self.assertEqual(self.json_actions[0]['params']['num_cpt'], 4)

    def test_edit_line(self):
        CostAccounting.objects.create(name='close', description='Close cost', status=1, is_default=False)
        CostAccounting.objects.create(name='open', description='Open cost', status=0, is_default=True)
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-1|4|2|87.230000|0|0|None|\n-2|11|0|87.230000|2|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryLineAccountEdit()
        self.calljson('/diacamma.accounting/entryLineAccountEdit', {'year': 1, 'debit_val': 0, 'date_value': '2015-02-13', 'num_cpt_txt': '', 'credit_val': 0,
                                                                    'entrylineaccount_serial': -2,
                                                                    'serial_entry': '-1|4|2|87.230000|0|0|None|\n-2|11|0|87.230000|2|0|None|',
                                                                    'journal': 2, 'designation': 'un plein cadie', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryLineAccountEdit')
        self.assert_count_equal('', 5)
        self.assert_json_equal('LABELFORM', 'account', '[601] 601')
        self.assert_json_equal('FLOAT', 'debit_val', '87.23')
        self.assert_json_equal('FLOAT', 'credit_val', '0')
        self.assert_json_equal('SELECT', 'costaccounting', '2')
        self.assert_select_equal('costaccounting', 2)  # nb=2
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryLineAccountAdd")
        self.assertEqual(len(self.json_actions[0]['params']), 1)
        self.assertEqual(self.json_actions[0]['params']['num_cpt'], 11)

    def test_change_line_payoff(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '3',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryLineAccountEdit()
        self.calljson('/diacamma.accounting/entryLineAccountEdit', {'year': '1', 'journal': '3', 'entryaccount': '1', 'reference': '',
                                                                    'serial_entry': "-1|4|0|152.340000|0|0|None|\n-2|3|0|152.340000|0|0|aaabbb|", 'entrylineaccount_serial': '-2'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryLineAccountEdit')
        self.assert_count_equal('', 5)

        self.assert_json_equal('LABELFORM', 'account', '[531] 531')
        self.assert_json_equal('FLOAT', 'debit_val', '152.34')
        self.assert_json_equal('FLOAT', 'credit_val', '0.00')
        self.assert_json_equal('EDIT', 'reference', 'aaabbb')
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryLineAccountAdd")
        self.assertEqual(len(self.json_actions[0]['params']), 1)
        self.assertEqual(self.json_actions[0]['params']['num_cpt'], 3)

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '3', 'entryaccount': '1',
                                                                   'serial_entry': "-1|4|0|152.340000|0|0|None|\n-2|3|0|152.340000|0|0|aaabbb|", 'debit_val': '152.34',
                                                                   'credit_val': '0.0', 'entrylineaccount_serial': '-2', 'reference': 'ccdd', 'num_cpt': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], '1')
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "3")
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        serial_value = self.response_json['action']['params']['serial_entry']
        self.assertEqual(serial_value[-25:], "|3|0|152.340000|0|0|ccdd|")

    def test_valid_entry(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|0|0|None|\n-3|4|3|152.340000|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-02-13')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entryline/@1/link', '---')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 152.34€ = {[b]}Résultat :{[/b]} -152.34€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountOpenFromLine()
        self.calljson('/diacamma.accounting/entryAccountOpenFromLine',
                      {'year': '1', 'journal': '2', 'filter': '0', 'entryline': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountOpenFromLine')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(self.response_json['action']['params'], None)
        self.assertEqual(len(self.json_context), 5)
        self.assertEqual(self.json_context['filter'], "0")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")
        self.assertEqual(self.json_context['entryaccount'], 1)

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', 'journal': '2', "entryline": "1"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '2', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry.num', '1')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', date.today())
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-02-13')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 152.34€ = {[b]}Résultat :{[/b]} -152.34€{[br/]}{[b]}Trésorerie :{[/b]} 0.00€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountOpenFromLine()
        self.calljson('/diacamma.accounting/entryAccountOpenFromLine',
                      {'year': '1', 'journal': '2', 'filter': '0', 'entryline': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountOpenFromLine')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountShow")
        self.assertEqual(self.response_json['action']['params'], None)
        self.assertEqual(len(self.json_context), 5)
        self.assertEqual(self.json_context['filter'], "0")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")
        self.assertEqual(self.json_context['entryaccount'], 1)

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '2', 'filter': '0', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'num', '1')
        self.assert_json_equal('LABELFORM', 'journal', 'Achats')
        self.assert_json_equal('LABELFORM', 'date_entry', formats.date_format(date.today(), "DATE_FORMAT"))
        self.assert_json_equal('LABELFORM', 'date_value', '13 février 2015')
        self.assert_json_equal('LABELFORM', 'designation', 'un plein cadie')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', '---')
        self.assert_count_equal('#entrylineaccount/actions', 0)
        self.assertEqual(len(self.json_actions), 2)
        self.assertEqual(self.json_actions[0]['id'], "diacamma.accounting/entryAccountCreateLinked")

        self.factory.xfer = CostAccountingAddModify()
        self.calljson('/diacamma.accounting/costAccountingAddModify', {"SAVE": "YES", 'name': 'aaa', 'description': 'aaa', 'year': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'costAccountingAddModify')  # id = 3

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '2', 'filter': '0', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', '---')
        self.assert_count_equal('#entrylineaccount/actions', 1)
        self.assertEqual(len(self.json_actions), 2)

    def test_show_close_cost(self):
        fill_entries_fr(1)
        self.factory.xfer = EntryAccountOpenFromLine()
        self.calljson('/diacamma.accounting/entryAccountOpenFromLine',
                      {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '23'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountOpenFromLine')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountShow")
        self.assertEqual(self.response_json['action']['params'], None)
        self.assertEqual(len(self.json_context), 5)
        self.assertEqual(self.json_context['filter'], "0")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "-1")
        self.assertEqual(self.json_context['entryaccount'], 11)

        self.factory.xfer = EntryAccountShow()
        self.calljson('/diacamma.accounting/entryAccountShow',
                      {'year': '1', 'journal': '-1', 'filter': '0', 'entryaccount': '11'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountShow')
        self.assert_count_equal('', 8)
        self.assert_json_equal('LABELFORM', 'num', '7')
        self.assert_json_equal('LABELFORM', 'journal', 'Opérations diverses')
        self.assert_json_equal('LABELFORM', 'date_value', '20 février 2015')
        self.assert_json_equal('LABELFORM', 'designation', 'Frais bancaire')
        self.assert_count_equal('entrylineaccount', 2)
        self.assert_json_equal('', 'entrylineaccount/@0/entry_account', '[512] 512')
        self.assert_json_equal('', 'entrylineaccount/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount/@1/entry_account', '[627] 627')
        self.assert_json_equal('', 'entrylineaccount/@1/costaccounting', 'close')
        self.assert_count_equal('#entrylineaccount/actions', 0)
        self.assertEqual(len(self.json_actions), 1)

    def test_inverse_entry(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|0|0|None|\n-3|4|3|152.340000|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)

        self.assertEqual(len(self.json_actions), 5)
        self.assertEqual(self.json_actions[1]['id'], "diacamma.accounting/entryAccountClose")
        self.assertEqual(self.json_actions[2]['id'], "diacamma.accounting/entryAccountCreateLinked")
        self.assertEqual(self.json_actions[3]['id'], "diacamma.accounting/entryAccountReverse")

        self.factory.xfer = EntryAccountReverse()
        self.calljson('/diacamma.accounting/entryAccountReverse',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountReverse')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 14)

        self.assert_json_equal('LABELFORM', 'asset_warning', "{[center]}{[i]}écriture d'un avoir{[/i]}{[/center]}")

    def test_valid_payment(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|0|0|None|\n-3|4|3|152.340000|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountCreateLinked()
        self.calljson('/diacamma.accounting/entryAccountCreateLinked',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCreateLinked')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(len(self.response_json['action']['params']), 5)
        self.assertEqual(self.response_json['action']['params']['entryaccount'], 2)
        self.assertEqual(self.response_json['action']['params']['linked_entryaccount'], 1)
        self.assertEqual(self.response_json['action']['params']['serial_entry'][-26:-1], "|4|3|-152.340000|0|0|None")
        self.assertEqual(self.response_json['action']['params']['num_cpt_txt'], "5")
        self.assertEqual(self.response_json['action']['params']['journal'], "4")
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], "1")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '4', 'entryaccount': '2', 'linked_entryaccount': '1',
                                                                'serial_entry': "-3|4|3|-152.340000|0|0|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 16)
        self.assert_json_equal('SELECT', 'journal', '4')
        self.assert_json_equal('DATE', 'date_value', '2015-12-31')
        self.assert_json_equal('EDIT', 'designation', 'règlement de un plein cadie')

        self.assert_count_equal('entrylineaccount_serial', 1)
        self.assert_json_equal('EDIT', 'num_cpt_txt', '5')
        self.assert_json_equal('SELECT', 'num_cpt', '2')
        self.assert_select_equal('num_cpt', 2)  # nb=2
        self.assert_json_equal('FLOAT', 'debit_val', '0.00')
        self.assert_json_equal('FLOAT', 'credit_val', '152.34')
        self.assert_json_equal('EDIT', 'reference', '')

        self.assert_count_equal('entrylineaccount_serial', 1)
        self.assert_json_equal('', 'entrylineaccount_serial/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/debit', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/credit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/costaccounting', '---')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '2', 'entryaccount': '2', 'linked_entryaccount': '1',
                                                                'serial_entry': "-3|4|3|-152.340000|0|0|None|\n-4|2|0|-152.340000|0|0|Ch N°12345|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)
        self.assert_count_equal('entrylineaccount_serial', 2)
        self.assert_json_equal('', 'entrylineaccount_serial/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/debit', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/credit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/reference', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@0/costaccounting', '---')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/entry_account', '[512] 512')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/debit', '{[font color="green"]}{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/reference', 'Ch N°12345')
        self.assert_json_equal('', 'entrylineaccount_serial/@1/costaccounting', '---')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate', {'year': '1', 'journal': '2', 'entryaccount': '2', 'linked_entryaccount': '1',
                                                                    'serial_entry': "-3|4|3|-152.340000|0|0|None||\n-4|2|0|-152.340000|0|0|Ch N°12345|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 4)

        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-02-13')
        self.assert_json_equal('', 'entryline/@0/link', 'A')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entryline/@1/link', '---')

        self.assert_json_equal('', 'entryline/@2/entry.num', '---')
        self.assert_json_equal('', 'entryline/@2/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@2/entry.date_value', '2015-12-31')
        self.assert_json_equal('', 'entryline/@2/link', 'A')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entryline/@2/debit', '{[font color="blue"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@3/link', '---')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 152.34€ = {[b]}Résultat :{[/b]} -152.34€{[br/]}{[b]}Trésorerie :{[/b]} -152.34€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

    def test_valid_payment_canceled(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-02-13', 'designation': 'un plein cadie'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-2|12|0|152.340000|0|0|None|\n-3|4|3|152.340000|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.assertEqual(1, EntryAccount.objects.all().count())

        self.factory.xfer = EntryAccountCreateLinked()
        self.calljson('/diacamma.accounting/entryAccountCreateLinked',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountCreateLinked')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(len(self.response_json['action']['params']), 5)
        self.assertEqual(self.response_json['action']['params']['serial_entry'][-26:-1], "|4|3|-152.340000|0|0|None")
        self.assertEqual(len(self.json_context), 3)

        self.assertEqual(2, EntryAccount.objects.all().count())

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'year': '1', 'journal': '4', 'entryaccount': '2', 'linked_entryaccount': '1',
                                                                'serial_entry': "-3|4|3|-152.340000|0|0|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 16)

        self.factory.xfer = EntryAccountUnlock()
        self.calljson('/diacamma.accounting/entryAccountUnlock', {'year': '1', 'journal': '4', 'entryaccount': '2', 'linked_entryaccount': '1',
                                                                  'serial_entry': "-3|4|3|-152.340000|0|0|None|", 'num_cpt_txt': '5'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountUnlock')

        self.assertEqual(1, EntryAccount.objects.all().count())

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-02-13')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[401 Luke Lucky]')
        self.assert_json_equal('', 'entryline/@0/credit', '{[font color="green"]}152.34€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[602] 602')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')

    def test_link_unlink_entries(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-04-27', 'designation': 'Une belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                    'serial_entry': "-6|9|0|364.91|0|0|None|\n-7|1|5|364.91|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '4', 'date_value': '2015-05-03',
                                                                'designation': 'Règlement de belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate', {'year': '1', 'journal': '4', 'entryaccount': '2',
                                                                    'serial_entry': "-9|1|5|-364.91|0|0|None|\n-8|2|0|364.91|0|0|BP N°987654|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '5',
                                                                'date_value': '2015-04-27', 'designation': 'divers'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate', {'year': '1', 'journal': '2', 'entryaccount': '3',
                                                                    'serial_entry': "-11|1|6|-364.91|0|0|None|\n-12|1|5|250.61|0|0|None|\n-13|1|7|114.30|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 7)

        self.assert_json_equal('', 'entryline/@0/id', '2')
        self.assert_json_equal('', 'entryline/@0/entry.num', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@0/entry.date_value', '2015-04-27')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@0/debit', '{[font color="blue"]}364.91€{[/font]}')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@1/id', '1')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[706] 706')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')

        self.assert_json_equal('', 'entryline/@2/id', '6')
        self.assert_json_equal('', 'entryline/@2/entry_account', "[411 Dalton William]")
        self.assert_json_equal('', 'entryline/@2/debit', "{[font color=\"blue\"]}250.61€{[/font]}")
        self.assert_json_equal('', 'entryline/@3/id', '5')
        self.assert_json_equal('', 'entryline/@3/entry_account', "[411 Dalton Jack]")
        self.assert_json_equal('', 'entryline/@3/credit', "{[font color=\"green\"]}364.91€{[/font]}")
        self.assert_json_equal('', 'entryline/@4/id', '7')
        self.assert_json_equal('', 'entryline/@4/entry_account', "[411 Dalton Joe]")
        self.assert_json_equal('', 'entryline/@4/debit', "{[font color=\"blue\"]}114.30€{[/font]}")

        self.assert_json_equal('', 'entryline/@5/id', '3')
        self.assert_json_equal('', 'entryline/@5/entry.num', '---')
        self.assert_json_equal('', 'entryline/@5/entry.date_entry', '---')
        self.assert_json_equal('', 'entryline/@5/entry.date_value', '2015-05-03')
        self.assert_json_equal('', 'entryline/@5/link', '---')
        self.assert_json_equal('', 'entryline/@5/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@5/credit', '{[font color="green"]}364.91€{[/font]}')
        self.assert_json_equal('', 'entryline/@5/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@6/id', '4')
        self.assert_json_equal('', 'entryline/@6/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@6/designation_ref', 'Règlement de belle facture{[br/]}BP N°987654')
        self.assert_json_equal('', 'entryline/@6/costaccounting', '---')

        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 364.91€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 364.91€{[br/]}{[b]}Trésorerie :{[/b]} 364.91€ - {[b]}Validé :{[/b]} 0.00€{[/center]}')

        self.factory.xfer = EntryAccountLink()
        self.calljson('/diacamma.accounting/entryAccountLink', {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '2;3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountLink')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 7)
        self.assert_json_equal('', 'entryline/@0/id', '2')
        self.assert_json_equal('', 'entryline/@0/link', 'A')
        self.assert_json_equal('', 'entryline/@1/id', '1')
        self.assert_json_equal('', 'entryline/@1/link', '---')
        self.assert_json_equal('', 'entryline/@5/id', '3')
        self.assert_json_equal('', 'entryline/@5/link', 'A')
        self.assert_json_equal('', 'entryline/@6/id', '4')
        self.assert_json_equal('', 'entryline/@6/link', '---')

        self.factory.xfer = EntryAccountLink()
        self.calljson('/diacamma.accounting/entryAccountLink', {'CONFIRME': 'YES', 'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountLink')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList', {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 7)
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@1/link', '---')
        self.assert_json_equal('', 'entryline/@2/link', '---')
        self.assert_json_equal('', 'entryline/@3/link', '---')

        self.factory.xfer = EntryAccountLink()
        self.calljson('/diacamma.accounting/entryAccountLink', {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '1;2'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryAccountLink')
        self.assert_json_equal('', 'message', "Une ligne d'écriture n'a pas un code de tiers !")

        self.factory.xfer = EntryAccountLink()
        self.calljson('/diacamma.accounting/entryAccountLink', {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '2;5'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryAccountLink')
        self.assert_json_equal('', 'message', "Ces lignes d'écritures n'ont pas le même tiers !")

        self.factory.xfer = EntryAccountLink()
        self.calljson('/diacamma.accounting/entryAccountLink', {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '2;6'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryAccountLink')
        self.assert_json_equal('', 'message', "Ces lignes d'écritures ne s'équilibrent pas !")

    def test_delete_lineentry(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-04-27', 'designation': 'Une belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-6|9|0|364.91|0|0|None|\n-7|1|5|364.91|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)
        self.assert_count_equal('entrylineaccount_serial', 2)
        self.assertEqual(len(self.json_actions), 5)

        self.factory.xfer = EntryLineAccountDel()
        self.calljson('/diacamma.accounting/entryLineAccountDel', {'year': '1', 'journal': '2', 'entryaccount': '1',
                                                                   'serial_entry': "1|9|0|364.91|0|0|None|\n2|1|5|364.91|0|0|None|", "entrylineaccount_serial": '2'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountDel')
        self.assertEqual(self.response_json['action']['id'], "diacamma.accounting/entryAccountEdit")
        self.assertEqual(len(self.response_json['action']['params']), 1)
        self.assertEqual(self.response_json['action']['params']['serial_entry'], "1|9|0|364.910000|0|0|None|")
        self.assertEqual(len(self.json_context), 3)
        self.assertEqual(self.json_context['entryaccount'], "1")
        self.assertEqual(self.json_context['year'], "1")
        self.assertEqual(self.json_context['journal'], "2")

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', "entrylineaccount_serial": '2', 'serial_entry': "1|9|0|364.91|0|0|None|"}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountEdit')
        self.assert_count_equal('', 13)
        self.assert_count_equal('entrylineaccount_serial', 1)
        self.assertEqual(len(self.json_actions), 2)

    def test_delete_entries(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '2',
                                                                'date_value': '2015-04-27', 'designation': 'Une belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '2', 'entryaccount': '1', 'serial_entry': "-6|9|0|364.91|0|0|None|\n-7|1|5|364.91|0|0|None|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '4',
                                                                'date_value': '2015-05-03', 'designation': 'Règlement de belle facture'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')
        self.factory.xfer = EntryAccountValidate()
        self.calljson('/diacamma.accounting/entryAccountValidate',
                      {'year': '1', 'journal': '4', 'entryaccount': '2', 'serial_entry': "-9|1|5|-364.91|0|0|None|\n-8|2|0|364.91|0|0|BP N°987654|"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountValidate')

        self.factory.xfer = EntryAccountLink()
        self.calljson('/diacamma.accounting/entryAccountLink',
                      {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '2;3'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountLink')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 4)
        self.assert_json_equal('', 'entryline/@0/link', 'A')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@0/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@1/link', '---')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[706] 706')
        self.assert_json_equal('', 'entryline/@1/costaccounting', '---')

        self.assert_json_equal('', 'entryline/@2/link', 'A')
        self.assert_json_equal('', 'entryline/@2/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@2/costaccounting', '---')
        self.assert_json_equal('', 'entryline/@3/link', '---')
        self.assert_json_equal('', 'entryline/@3/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@3/costaccounting', '---')

        self.factory.xfer = EntryAccountDel()
        self.calljson('/diacamma.accounting/entryAccountDel',
                      {'CONFIRME': 'YES', 'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '1'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountDel')

        self.factory.xfer = EntryAccountClose()
        self.calljson('/diacamma.accounting/entryAccountClose',
                      {'CONFIRME': 'YES', 'year': '1', 'journal': '-1', 'filter': '0', "entryline": "3"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountClose')

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('', 7)
        self.assert_count_equal('entryline', 2)
        self.assert_json_equal('', 'entryline/@0/entry.num', '1')
        self.assert_json_equal('', 'entryline/@0/link', '---')
        self.assert_json_equal('', 'entryline/@0/entry_account', '[411 Dalton William]')
        self.assert_json_equal('', 'entryline/@1/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@1/debit', '{[font color="blue"]}364.91€{[/font]}')
        self.assert_json_equal('', 'entryline/@1/designation_ref', 'Règlement de belle facture{[br/]}BP N°987654')
        self.assert_json_equal('LABELFORM', 'result', '{[center]}{[b]}Produit :{[/b]} 0.00€ - {[b]}Charge :{[/b]} 0.00€ = {[b]}Résultat :{[/b]} 0.00€{[br/]}{[b]}Trésorerie :{[/b]} 364.91€ - {[b]}Validé :{[/b]} 364.91€{[/center]}')

        self.factory.xfer = EntryAccountDel()
        self.calljson('/diacamma.accounting/entryAccountDel',
                      {'year': '1', 'journal': '-1', 'filter': '0', 'entryline': '3'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryAccountDel')
        self.assert_json_equal('', 'message', 'écriture validée !')

    def test_buyingselling_in_report(self):
        self.factory.xfer = EntryAccountEdit()
        self.calljson('/diacamma.accounting/entryAccountEdit', {'SAVE': 'YES', 'year': '1', 'journal': '1',
                                                                'date_value': '2015-03-21', 'designation': 'mauvais report'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryAccountEdit')

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '1', 'entryaccount': '1', 'num_cpt_txt': '70',
                                                                   'num_cpt': '9', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_json_equal('', 'message', "Ce type d'écriture n'est pas permis dans ce journal !")

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '1', 'entryaccount': '1', 'num_cpt_txt': '60',
                                                                   'num_cpt': '13', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.exception', 'diacamma.accounting', 'entryLineAccountAdd')
        self.assert_json_equal('', 'message', "Ce type d'écriture n'est pas permis dans ce journal !")

        self.factory.xfer = EntryLineAccountAdd()
        self.calljson('/diacamma.accounting/entryLineAccountAdd', {'year': '1', 'journal': '1', 'entryaccount': '1', 'num_cpt_txt': '401',
                                                                   'num_cpt': '4', 'third': 0, 'debit_val': '0.0', 'credit_val': '152.34'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.accounting', 'entryLineAccountAdd')
