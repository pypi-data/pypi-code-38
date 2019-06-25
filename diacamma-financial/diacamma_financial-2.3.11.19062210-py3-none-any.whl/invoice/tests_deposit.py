# -*- coding: utf-8 -*-
'''
lucterios.contacts package

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
from base64 import b64decode
from lucterios.CORE.models import Parameter
from lucterios.CORE.parameters import Params

from lucterios.framework.xfergraphic import XferContainerAcknowledge
from lucterios.framework.filetools import get_user_dir

from diacamma.accounting.test_tools import initial_thirds_fr, default_compta_fr
from diacamma.accounting.views_entries import EntryAccountList
from diacamma.invoice.test_tools import default_articles, InvoiceTest
from diacamma.payoff.views_deposit import DepositSlipList, DepositSlipAddModify,\
    DepositSlipShow, DepositDetailAddModify, DepositDetailSave, DepositSlipTransition
from diacamma.payoff.views import PayoffAddModify, PayableShow, PayableEmail
from diacamma.payoff.test_tools import default_bankaccount_fr,\
    default_paymentmethod, PaymentTest
from diacamma.invoice.views import BillShow
from django.utils import six
from lucterios.mailing.tests import configSMTP, TestReceiver
from lucterios.contacts.views_contacts import ResponsabilityModify
from diacamma.invoice.models import Bill


class DepositTest(InvoiceTest):

    def setUp(self):
        initial_thirds_fr()
        InvoiceTest.setUp(self)
        default_compta_fr()
        default_articles()
        default_bankaccount_fr()
        rmtree(get_user_dir(), True)
        self.add_bills()

    def add_bills(self):
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 1, '2015-04-01', 6, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 1, '2015-04-01', 4, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 2, '2015-04-01', 5, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 3, '2015-04-01', 7, True)

    def create_deposit(self):
        self.factory.xfer = DepositSlipAddModify()
        self.calljson('/diacamma.payoff/depositSlipAddModify',
                      {'SAVE': 'YES', 'bank_account': 1, 'reference': '123456', 'date': '2015-04-10'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositSlipAddModify')

    def create_payoff(self, bill_id, amount, payer, mode, reference):
        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': bill_id, 'amount': amount, 'payer': payer, 'date': '2015-04-03', 'mode': mode, 'reference': reference, 'bank_account': 1}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

    def test_deposit_basic(self):
        self.factory.xfer = DepositSlipList()
        self.calljson('/diacamma.payoff/depositSlipList', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipList')
        self.assert_grid_equal('depositslip', {"status": "status", "bank_account": "compte bancaire", "date": "date", "reference": "référence", "total": "total"}, 0)  # nb=5

        self.factory.xfer = DepositSlipAddModify()
        self.calljson('/diacamma.payoff/depositSlipAddModify', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipAddModify')
        self.assert_count_equal('', 4)

        self.factory.xfer = DepositSlipAddModify()
        self.calljson('/diacamma.payoff/depositSlipAddModify',
                      {'SAVE': 'YES', 'bank_account': 1, 'reference': '123456', 'date': '2015-04-10'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositSlipAddModify')

        self.factory.xfer = DepositSlipList()
        self.calljson('/diacamma.payoff/depositSlipList', {}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipList')
        self.assert_count_equal('depositslip', 1)
        self.assert_json_equal('', 'depositslip/@0/bank_account', 'My bank')
        self.assert_json_equal('', 'depositslip/@0/reference', '123456')
        self.assert_json_equal('', 'depositslip/@0/date', '2015-04-10')
        self.assert_json_equal('', 'depositslip/@0/status', 'en création')
        self.assert_json_equal('', 'depositslip/@0/total', '0.00€')

        self.factory.xfer = DepositSlipShow()
        self.calljson('/diacamma.payoff/depositSlipShow', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipShow')
        self.assert_count_equal('', 15)
        self.assertEqual(len(self.json_actions), 2)
        self.assert_grid_equal('depositdetail', {"payoff.payer": "payeur", "payoff.date": "date", "payoff.reference": "référence", "amount": "montant"}, 0)  # nb=4
        self.assert_count_equal('#depositdetail/actions', 2)
        self.assert_json_equal('LABELFORM', 'total', '0.00€')

    def test_deposit_nocheque(self):
        self.create_deposit()

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('', 7)
        self.assertEqual(len(self.json_actions), 1)
        self.assert_grid_equal('entry', {"bill": "facture", "payer": "payeur", "amount": "montant", "date": "date", "reference": "référence"}, 0)  # nb=5
        self.assert_count_equal('#entry/actions', 1)

    def test_deposit_simple(self):
        self.create_payoff(1, "75.0", "Mr Smith", 1, "ABC123")
        self.create_payoff(2, "50.0", "Mme Smith", 1, "XYZ987")
        self.create_payoff(4, "30.0", "Miss Smith", 1, "?????")
        self.create_deposit()

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 3)
        self.assert_json_equal('', 'entry/@0/bill', 'facture A-1 - 1 avril 2015')
        self.assert_json_equal('', 'entry/@0/payer', 'Mr Smith')
        self.assert_json_equal('', 'entry/@0/amount', '75.00€')
        self.assert_json_equal('', 'entry/@0/reference', 'ABC123')
        self.assert_json_equal('', 'entry/@1/bill', 'facture A-2 - 1 avril 2015')
        self.assert_json_equal('', 'entry/@1/payer', 'Mme Smith')
        self.assert_json_equal('', 'entry/@1/amount', '50.00€')
        self.assert_json_equal('', 'entry/@1/reference', 'XYZ987')
        self.assert_json_equal('', 'entry/@2/bill', 'reçu A-1 - 1 avril 2015')
        self.assert_json_equal('', 'entry/@2/payer', 'Miss Smith')
        self.assert_json_equal('', 'entry/@2/amount', '30.00€')
        self.assert_json_equal('', 'entry/@2/reference', '?????')
        id1 = self.get_json_path("entry/@0/id")
        id2 = self.get_json_path("entry/@1/id")

        self.factory.xfer = DepositDetailSave()
        self.calljson('/diacamma.payoff/depositDetailSave', {'depositslip': 1, 'entry': '%s;%s' % (id1, id2)}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositDetailSave')

        self.factory.xfer = DepositSlipShow()
        self.calljson('/diacamma.payoff/depositSlipShow', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipShow')
        self.assertEqual(len(self.json_actions), 4)
        self.assert_count_equal('depositdetail', 2)
        self.assert_json_equal('LABELFORM', 'total', '125.00€')

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 1)

    def test_deposit_othermode(self):
        self.create_payoff(1, "10.0", "Mr Smith", 0, "ABC123")
        self.create_payoff(2, "8.5", "Mme Smith", 2, "XYZ987")
        self.create_payoff(1, "12.0", "Jean Dupond", 3, "321CBA")
        self.create_payoff(2, "9.75", "Marie Durant", 4, "789ZXY")
        self.create_deposit()

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 0)

    def test_deposit_asset(self):
        self.create_payoff(3, "10.0", "Mr Smith", 1, "ABC123")
        self.create_payoff(3, "8.5", "Mme Smith", 1, "XYZ987")
        self.create_payoff(3, "12.0", "Jean Dupond", 0, "321CBA")
        self.create_payoff(3, "9.75", "Marie Durant", 3, "789ZXY")
        self.create_deposit()

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 0)

    def test_deposit_multipayoff(self):
        self.create_payoff(1, "50.0", "Mr Smith", 1, "ABC123")

        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supportings': '1;2', 'amount': '150.0', 'date': '2015-04-04', 'mode': 1, 'reference': 'IJKL654', 'bank_account': 1, 'payer': "Jean Dupond"}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')
        self.create_deposit()

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 2)
        self.assert_json_equal('', 'entry/@0/bill', 'facture A-1 - 1 avril 2015')
        self.assert_json_equal('', 'entry/@0/payer', 'Mr Smith')
        self.assert_json_equal('', 'entry/@0/amount', '50.00€')
        self.assert_json_equal('', 'entry/@0/reference', 'ABC123')
        self.assert_json_equal('', 'entry/@1/bill', 'facture A-1 - 1 avril 2015{[br/]}facture A-2 - 1 avril 2015')
        self.assert_json_equal('', 'entry/@1/payer', 'Jean Dupond')
        self.assert_json_equal('', 'entry/@1/amount', '150.00€')
        self.assert_json_equal('', 'entry/@1/reference', 'IJKL654')

        id1 = self.get_json_path("entry/@0/id")
        id2 = self.get_json_path("entry/@1/id")

        self.factory.xfer = DepositDetailSave()
        self.calljson('/diacamma.payoff/depositDetailSave', {'depositslip': 1, 'entry': '%s;%s' % (id1, id2)}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositDetailSave')

        self.factory.xfer = DepositSlipShow()
        self.calljson('/diacamma.payoff/depositSlipShow', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipShow')
        self.assert_count_equal('depositdetail', 2)
        self.assert_json_equal('', 'depositdetail/@0/payoff.payer', 'Jean Dupond')
        self.assert_json_equal('', 'depositdetail/@0/payoff.reference', 'IJKL654')
        self.assert_json_equal('', 'depositdetail/@0/amount', '150.00€')
        self.assert_json_equal('', 'depositdetail/@1/payoff.payer', 'Mr Smith')
        self.assert_json_equal('', 'depositdetail/@1/payoff.reference', 'ABC123')
        self.assert_json_equal('', 'depositdetail/@1/amount', '50.00€')
        self.assert_json_equal('LABELFORM', 'total', '200.00€')

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 0)

    def test_deposit_valid(self):
        self.create_payoff(1, "75.0", "Mr Smith", 1, "ABC123")
        self.create_payoff(2, "50.0", "Mme Smith", 1, "XYZ987")
        self.create_deposit()

        self.factory.xfer = DepositDetailAddModify()
        self.calljson('/diacamma.payoff/depositDetailAddModify', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositDetailAddModify')
        self.assert_count_equal('entry', 2)
        id1 = self.get_json_path("entry/@0/id")
        id2 = self.get_json_path("entry/@1/id")
        self.factory.xfer = DepositDetailSave()
        self.calljson('/diacamma.payoff/depositDetailSave', {'depositslip': 1, 'entry': '%s;%s' % (id1, id2)}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositDetailSave')

        self.factory.xfer = DepositSlipTransition()
        self.calljson('/diacamma.payoff/depositSlipTransition', {'depositslip': 1, 'CONFIRME': 'YES', 'TRANSITION': 'close_deposit'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositSlipTransition')

        self.factory.xfer = DepositSlipShow()
        self.calljson('/diacamma.payoff/depositSlipShow', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipShow')
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 12)
        self.assert_json_equal('', 'entryline/@8/entry.num', '---')
        self.assert_json_equal('', 'entryline/@8/entry_account', '[411 Dalton Jack]')
        self.assert_json_equal('', 'entryline/@8/credit', '{[font color="green"]}75.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@9/entry.num', '---')
        self.assert_json_equal('', 'entryline/@9/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@9/debit', '{[font color="blue"]}75.00€{[/font]}')

        self.assert_json_equal('', 'entryline/@10/entry.num', '---')
        self.assert_json_equal('', 'entryline/@10/entry_account', '[411 Minimum]')
        self.assert_json_equal('', 'entryline/@10/credit', '{[font color="green"]}50.00€{[/font]}')
        self.assert_json_equal('', 'entryline/@11/entry.num', '---')
        self.assert_json_equal('', 'entryline/@11/entry_account', '[512] 512')
        self.assert_json_equal('', 'entryline/@11/debit', '{[font color="blue"]}50.00€{[/font]}')

        self.factory.xfer = DepositSlipTransition()
        self.calljson('/diacamma.payoff/depositSlipTransition', {'depositslip': 1, 'CONFIRME': 'YES', 'TRANSITION': 'validate_deposit'}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'depositSlipTransition')

        self.factory.xfer = DepositSlipShow()
        self.calljson('/diacamma.payoff/depositSlipShow', {'depositslip': 1}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'depositSlipShow')
        self.assertEqual(len(self.json_actions), 2)

        self.factory.xfer = EntryAccountList()
        self.calljson('/diacamma.accounting/entryAccountList',
                      {'year': '1', 'journal': '-1', 'filter': '0'}, False)
        self.assert_observer('core.custom', 'diacamma.accounting', 'entryAccountList')
        self.assert_count_equal('entryline', 12)
        self.assert_json_equal('', 'entryline/@8/entry.num', '2')
        self.assert_json_equal('', 'entryline/@10/entry.num', '1')


class MethodTest(InvoiceTest, PaymentTest):

    def setUp(self):
        initial_thirds_fr()
        InvoiceTest.setUp(self)
        default_compta_fr()
        default_articles()
        default_bankaccount_fr()
        default_paymentmethod()
        rmtree(get_user_dir(), True)
        self.add_bills()

    def add_bills(self):
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 0, '2015-04-01', 6, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 1, '2015-04-01', 4, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 2, '2015-04-01', 5, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 3, '2015-04-01', 7, True)
        details = [{'article': 0, 'designation': 'article 0', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 1, '2015-04-01', 6, False)

    def test_payment_asset(self):
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 3}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}avoir{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "100.00€")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 3, 'item_name': 'bill'}, False)
        self.assert_observer('core.exception', 'diacamma.payoff', 'payableShow')

    def test_payment_building(self):
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 5}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "en création")
        self.assertEqual(len(self.json_actions), 3)

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 5, 'item_name': 'bill'}, False)
        self.assert_observer('core.exception', 'diacamma.payoff', 'payableShow')

    def test_payment_cotation(self):
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}devis{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assertEqual(len(self.json_actions), 6)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 1, 'item_name': 'bill'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_count_equal('', 14)
        self.assert_json_equal('LABELFORM', 'num_txt', 'A-1')
        self.check_payment(1, 'devis A-1 - 1 avril 2015')

    def test_payment_bill(self):
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "100.00€")
        self.assertEqual(len(self.json_actions), 5)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 2, 'item_name': 'bill'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_count_equal('', 14)
        self.assert_json_equal('LABELFORM', 'num_txt', 'A-1')
        self.check_payment(2, 'facture A-1 - 1 avril 2015')

    def test_send_bill(self):
        configSMTP('localhost', 2025)
        server = TestReceiver()
        server.start(2025)
        try:
            self.factory.xfer = ResponsabilityModify()
            self.calljson('/lucterios.contacts/responsabilityModify', {'legal_entity': '7', 'individual': '3', "SAVE": "YES"}, False)
            self.assert_observer('core.acknowledge', 'lucterios.contacts', 'responsabilityModify')

            self.assertEqual(0, server.count())
            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail', {'item_name': 'bill', 'bill': 2}, False)
            self.assert_observer('core.custom', 'diacamma.payoff', 'payableEmail')
            self.assert_count_equal('', 4)
            self.assert_json_equal('EDIT', 'subject', 'facture A-1')
            self.assert_json_equal('MEMO', 'message', 'William Dalton (Minimum)', True)

            self.factory.xfer = PayableEmail()
            self.calljson('/diacamma.payoff/payableEmail', {'bill': 2, 'OK': 'YES', 'item_name': 'bill',
                                                            'subject': 'my bill', 'message': 'this is a bill.', 'model': 8}, False)
            self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payableEmail')
            self.assertEqual(1, server.count())
            self.assertEqual('mr-sylvestre@worldcompany.com', server.get(0)[1])
            self.assertEqual(['Minimum@worldcompany.com', 'William.Dalton@worldcompany.com', 'mr-sylvestre@worldcompany.com'], server.get(0)[2])
            msg, msg_txt, msg_file = server.check_first_message('my bill', 3, {'To': 'Minimum@worldcompany.com', 'Cc': 'William.Dalton@worldcompany.com'})
            self.assertEqual('text/plain', msg_txt.get_content_type())
            self.assertEqual('text/html', msg.get_content_type())
            self.assertEqual('base64', msg.get('Content-Transfer-Encoding', ''))
            self.check_email_msg(msg, '2', 'facture A-1 - 1 avril 2015')
            self.assertTrue('facture_A-1_Minimum.pdf' in msg_file.get('Content-Type', ''), msg_file.get('Content-Type', ''))
            self.save_pdf(base64_content=msg_file.get_payload())
        finally:
            server.stop()

    def test_payment_bill_with_tax(self):
        Parameter.change_value('invoice-vat-mode', '2')
        Params.clear()
        details = [{'article': 2, 'designation': 'Article 02', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 1, '2015-04-02', 4, True)
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "100.00€")
        self.assert_json_equal('LABELFORM', 'vta_sum', "4.76€")
        self.assertEqual(len(self.json_actions), 5)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 6, 'item_name': 'bill'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_json_equal('LABELFORM', 'num_txt', 'A-2')
        self.check_payment(6, 'facture A-2 - 2 avril 2015', '95.24', '4.76')

    def test_payment_billpartial_with_tax(self):
        Parameter.change_value('invoice-vat-mode', '2')
        Params.clear()
        details = [{'article': 2, 'designation': 'Article 02', 'price': '100.00', 'quantity': 1}]
        self._create_bill(details, 1, '2015-04-02', 4, True)
        self.factory.xfer = PayoffAddModify()
        self.calljson('/diacamma.payoff/payoffAddModify', {'SAVE': 'YES', 'supporting': 6, 'amount': '60.0',
                                                           'payer': "Ma'a Dalton", 'date': '2015-04-01', 'mode': 0, 'reference': 'abc', 'bank_account': 0}, False)
        self.assert_observer('core.acknowledge', 'diacamma.payoff', 'payoffAddModify')

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "40.00€")
        self.assert_json_equal('LABELFORM', 'vta_sum', "4.76€")
        self.assertEqual(len(self.json_actions), 5)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 6, 'item_name': 'bill'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.assert_json_equal('LABELFORM', 'num_txt', 'A-2')
        self.check_payment(6, 'facture A-2 - 2 avril 2015', '38.1', '1.9')

    def test_payment_recip(self):
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 4}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}reçu{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "100.00€")
        self.assertEqual(len(self.json_actions), 5)
        self.assert_action_equal(self.json_actions[0], (six.text_type('Règlement'), 'diacamma.payoff/images/payments.png', 'diacamma.payoff', 'payableShow', 0, 1, 1))

        self.factory.xfer = PayableShow()
        self.calljson('/diacamma.payoff/payableShow', {'bill': 4, 'item_name': 'bill'}, False)
        self.assert_observer('core.custom', 'diacamma.payoff', 'payableShow')
        self.check_payment(4, 'recu A-1 - 1 avril 2015')

    def test_payment_paypal_bill(self):
        self.check_payment_paypal(2, "facture A-1 - 1 avril 2015")
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 2}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")
        self.assertEqual(len(self.json_actions), 4)

    def test_payment_paypal_cotation(self):
        self.check_payment_paypal(1, "devis A-1 - 1 avril 2015")
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 1}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}devis{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'date', "1 avril 2015")
        self.assert_json_equal('LABELFORM', 'status', "archivé")

        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 6}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}facture{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'date', "3 avril 2015")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")
        self.assertEqual(len(self.json_actions), 4)

    def test_payment_paypal_recip(self):
        self.check_payment_paypal(4, "recu A-1 - 1 avril 2015")
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 4}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}reçu{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "0.00€")
        self.assertEqual(len(self.json_actions), 4)

    def test_payment_paypal_asset(self):
        self.check_payment_paypal(5, "avoir A-1 - 1 avril 2015", False)
        self.factory.xfer = BillShow()
        self.calljson('/diacamma.invoice/billShow', {'bill': 3}, False)
        self.assert_observer('core.custom', 'diacamma.invoice', 'billShow')
        self.assert_json_equal('LABELFORM', 'title', "{[br/]}{[center]}{[u]}{[b]}avoir{[/b]}{[/u]}{[/center]}")
        self.assert_json_equal('LABELFORM', 'status', "validé")
        self.assert_json_equal('LABELFORM', 'total_rest_topay', "100.00€")
        self.assertEqual(len(self.json_actions), 3)

    def test_check_payment_paypal(self):
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 1}, True, 302)
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 2}, True, 302)
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 4}, True, 302)
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 5}, True, 200)
        self.assertTrue(self.response.content.decode().strip().startswith("<!DOCTYPE html>"), self.response.content)
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 100}, True, 200)
        self.assertTrue(self.response.content.decode().strip().startswith("<!DOCTYPE html>"), self.response.content)

        cotation = Bill.objects.get(id=1)
        cotation.status = 3
        cotation.save()
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 1}, True, 200)
        self.assertTrue(self.response.content.decode().strip().startswith("<!DOCTYPE html>"), self.response.content)

        self.check_payment_paypal(4, "recu A-1 - 1 avril 2015")
        self.call_ex('/diacamma.payoff/checkPaymentPaypal', {'payid': 4}, True, 200)
        self.assertTrue(self.response.content.decode().strip().startswith("<!DOCTYPE html>"), self.response.content)
