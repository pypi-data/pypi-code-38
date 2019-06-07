# coding: utf-8
import os

from simple_report.report import SpreadsheetReport


class TestPKO(object):
    dst_dir = test_files = None

    def test_pko(self):
        pko_file = self.test_files['test-PF_PKO.xlsx']

        pko_res = os.path.join(self.dst_dir, 'res-PF_PKO.xlsx')
        if os.path.exists(pko_res):
            os.remove(pko_res)

        self.assertEqual(os.path.exists(pko_res), False)

        self.create_report(pko_file, pko_res)

        self.assertEqual(os.path.exists(pko_res), True)


    def create_report(self, temp_path, res_path):
        """

        """
        header_params = {}
        #string_params = {}
        bottom_params = {}

        header_params[u'cashier'] = u'Иванов Иван Иваныч'#document.cashier

        #enterprise = Enterprise.objects.filter(id=document.enterprise_id)
        #if enterprise:
        header_params[u'enterprise'] = u'Здесь название организации' #enterprise[0].name
        header_params[u'okpo'] = u'123947843' #enterprise[0].okpo

        #if document.number:
        header_params[u'number'] = '1' #document.number

        date = u'01-01-2001'#document.date_formatting
        base = u'Иванычу на похмел'#document.base
        if date:
            header_params[u'date'] = date
            bottom_params[u'date'] = date
        if base:
            header_params[u'base'] = base
            bottom_params[u'base'] = base

        report = SpreadsheetReport(temp_path)

        header = report.get_section(u'Header')
        header.flush(header_params)

        #Строки, соответствующие операциям
        #operations = AccEntry.objects.filter(document_id = document_id).select_related('debet_kbk',
        #                                                                               'credit_kbk',
        #                                                                               'debit_account',
        #                                                                               'credit_account')
        #total_summa = 1000.21
        #for operation in operations:
        #if document.kvd:
        #    kvd = ' %s ' %document.kvd.code
        #else:
        #    kvd = u' '
        kvd = u'1'

        debit_kbk_part = '123456789012'#operation.debet_kbk if operation.debet_kbk else ''
        debit_account = '20104'#operation.debet_account if operation.debet_account else ''

        credit_kbk_part = '976543223232'#operation.credit_kbk if operation.credit_kbk else ''
        credit_account = '40110'#operation.credit_account if operation.credit_account else ''

        debit_kbk = debit_kbk_part + kvd + debit_account
        credit_kbk = credit_kbk_part + kvd + credit_account

        #total_summa += operation.summa

        string_params = {u'debit_kbk': debit_kbk,
                         u'kredit_kbk': credit_kbk}

        #if credit_account:
        accounting = credit_account #credit_account.code[-2:]
        string_params[u'accounting'] = accounting

        #if operation.summa:
        string_params[u'sum'] = 1000.21 #operation.summa

        string = report.get_section(u'String')
        for i in range(20):
            string.flush(string_params)

        #bottom_params = {u'total_sum': total_summa,
        #                 u'total_kopeks': two_decimal_kopeks(total_summa),
        #                 u'total_sum_in_words': money_in_words(total_summa)
        #                 }
        bottom_params = {u'total_sum': 1000.21, u'total_kopeks': 21, u'total_sum_in_words': u'Одна тысяча рублей',
                         u'annex': 'annex', u'cashier': u'Иванов Иван Иваныч'}

        #if document.annex:
        #if document.cashier:

        bottom = report.get_section(u'Bottom')
        bottom.flush(bottom_params)

        report.build(res_path)
