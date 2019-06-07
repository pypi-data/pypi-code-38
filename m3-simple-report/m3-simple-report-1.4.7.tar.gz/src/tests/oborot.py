# coding: utf-8
from collections import defaultdict

from simple_report.report import SpreadsheetReport


__author__ = 'prefer'

class OperationsJournalReportFactory(object):
    """
    Генерирует отчеты журнала операций в формате Excel
    """

    def __init__(self, template_name):
        self.template_name = template_name

    def _create_header(self, ppp_code):
        """
        Формирует заголовок отчета
        """
        #        period = u'%s %s года' % (MonthsEnum.values.get(self.date_start.month).lower(), self.date_start.year)
        #        ent = get_current_user_enterprise()
        #        ent_name = ent.name if ent else u'Облако'

        header = self._report.get_section('header')
        header.flush({
            'number': 1,
            'name': 2,
            'period': 3,
            'ent_name': 4,
            'last_day': 5,
            'ppp_code': 6
        })

    def _fetch_main_rows(self):
    #        qf = OperationsJournalQueryFactory()
    #
    #        if self.config_object.is_reverse_mode():
    #            query = qf.create_reverse_query(self.date_start, self.date_end, self.config_object)
    #        else:
    #            query = qf.create_query(self.date_start, self.date_end, self.config_object)
    #
    #        #noinspection PyUnresolvedReferences
    #        query = query.order_by('operation_date', 'document_date', 'document_number', 'document_type__name').\
    #        select_related('debet_kbk', 'credit_kbk', 'operation', 'document_type', 'debet_account',
    #            'credit_account', 'kvd', 'debet_kosgu', 'credit_kosgu')

    #        # Сворачивание по операциям
    #        if self.group_operations:
    #            fields4group = ['debet_account', 'credit_account', 'operation_date', 'document_date',
    #                            'document_number', 'document_type', 'operation', 'kvd', 'debet_kosgu', 'credit_kosgu',
    #                            'debet_kbk', 'credit_kbk', 'document_type', 'document_id']
    #            for i in range(1, ANALYTIC_COUNT + 1):
    #                fields4group.append('credit_analytic' + str(i) + '_id')
    #                fields4group.append('debet_analytic' + str(i) + '_id')
    #
    #            query = query.values(*fields4group).annotate(summa=Sum('summa'))
    #
    #        data = []
    #        if self.group_operations:
    #            for i, d in enumerate(query):
    #                data.append(BitchyRow(d))
    #        else:
    #            data = list(query)
    #
    #        dict_code = self.config_object.get_dict_code()
    #        debet_accounts, credit_accounts = qf.get_accounts_by_analytic_code(self.config_object, dict_code)

    #        result = []
    #        random_ppp = ''
    #        for d in data:
    #
    #            # Извлекаем наименование аналитики, сначала по дебету, затем по кредиту
    #            value = None
    #            if d.debet_account in debet_accounts:
    #                value = get_analytic_value_by_code(d, dict_code, False)
    #            elif d.credit_account in credit_accounts:
    #                value = get_analytic_value_by_code(d, dict_code, True)
    #            analytic_name = value.name if value else ''
    #
    #            result.append({
    #                'doc_date': d.document_date.strftime("%d.%m.%Y"), # Потому что у генератора летит дата
    #                'doc_num': d.document_number,
    #                'doc_name': d.document_type.name,
    #                'analytic_name': analytic_name,
    #                'description': d.operation.name,
    #                'debet_account': get_account_presentation_for_report(d.debet_account, d.kvd, d.debet_kosgu, d.debet_kbk),
    #                'credit_account': get_account_presentation_for_report(d.credit_account, d.kvd, d.credit_kosgu, d.credit_kbk),
    #                'summa': d.summa,
    #                # Надо для определения журнала
    #                'debet_account_id': d.debet_account.id if d.debet_account else -1,
    #                'credit_account_id': d.credit_account.id if d.credit_account else -1,
    #                })
    #
    #            # Ну надо так, что ;)
    #            if d.debet_kbk and not random_ppp:
    #                random_ppp = d.debet_kbk.code[:3]
    #
    #        return result, random_ppp
        return True

    def _create_main(self, main_rows):
        """
        Главная часть отчета, в которой достаются исходные данные для
        """
        line = self._report.get_section('main_line')
        for row in main_rows:
            line.flush({})

    def _fill_data_with_journal_numbers(self):
        """
        Проставляет в строки номер журнала, к которому принадлежит сумма.
        Выбор журнала происходит исходя из его приоритера.
        """
        pass

    def _create_middle(self, main_rows):
        """
        Таблица с суммой по счетам, сформированная из операций в главной таблице
        """
        middle = self._report.get_section('middle')
        middle.flush({})

        #        # Вычисляем сумму исходных данных по паре: счет дебета и счет кредита
        #        aggr = defaultdict(lambda: 0)
        #        for row in main_rows:
        #            key = (row['debet_account'], row['credit_account'], row['debet_account_id'], row['credit_account_id'])
        #            aggr[key] += row['summa']
        #
        #        # Проставляет в строки номер журнала, к которому принадлежит сумма.
        #        # Выбор журнала происходит исходя из его приоритера.
        #        priority_journal_configs = []
        #        for config in OperJournalConfig.objects.order_by('priority', 'number'):
        #            temp_config_object = ConfigObject(config)
        #            priority_journal_configs.append({
        #                'number': config.number,
        #                'debet_account_ids': temp_config_object.get_debet_accounts(),
        #                'credit_account_ids': temp_config_object.get_credit_accounts(),
        #                })
        #
        #        middle = self._report.get_section('middle_line')
        total = 0
        aggr = {'a': 1, }
        for key, value in aggr.iteritems():
        #            debet_account, credit_account, debet_account_id, credit_account_id = key
        #
        #            # Определяем к какому журналу принадлежит строка
        #            number = ''
        #            for config in priority_journal_configs:
        #                if debet_account_id in config['debet_account_ids'] or credit_account_id in config['credit_account_ids']:
        #                    number = config['number']
        #                    break

            middle.flush({
                'debet_account': key,
                'credit_account': value,
                'summa': 1,
                'number': 2
            })
            total += value

        middle_total = self._report.get_section('middle_total')
        middle_total.flush({
            'total': total
        })

    # Эта часть отчета отключена
    def _create_first_oborot(self):
        """
        Первая оборотка отображает обороты по всем счетам за период журнала, с детализацией по КОСГУ.
        Причем первой строкой для кждого счета выводится общая сумма без КОСГУ.
        """
        account_ids = set()
        account_ids.update(self.config_object.get_credit_accounts())
        account_ids.update(self.config_object.get_debet_accounts())

        oborotka = OborotkaSQLGenerator()
        data = oborotka.get_data(
            ent_id=self.ent_id,
            account_ids={'*': account_ids},
            date_start=self.date_start,
            date_end=self.date_end,
            details=[DictEnumerate.ACCCHART, DictEnumerate.KBK, DictEnumerate.KVD, DictEnumerate.KOSGU]
        )

        # Подготовим счета в виде КБК.КВД+Счет плана счетов (+КОСГУ в строках развертки)
        kosgu_totals = defaultdict(lambda: {
            'summa_begin_credit': 0,
            'summa_begin_debet': 0,
            'summa_end_credit': 0,
            'summa_end_debet': 0,
            'summa_turn_credit': 0,
            'summa_turn_debet': 0
        })
        for row in data:
            account_key = row['kbk_name'] + '.' + row['kvd_name'] + row['account_name']
            full_account_name = account_key + row['kosgu_name']
            row['full_account_name'] = full_account_name
            row['account_key'] = account_key
            t = kosgu_totals[account_key]
            t['summa_begin_credit'] += row['summa_begin_credit']
            t['summa_begin_debet'] += row['summa_begin_debet']
            t['summa_end_credit'] += row['summa_end_credit']
            t['summa_end_debet'] += row['summa_end_debet']
            t['summa_turn_credit'] += row['summa_turn_credit']
            t['summa_turn_debet'] += row['summa_turn_debet']

        data = sorted(data, key=lambda x: x['full_account_name'])

        # Сначала выводятся итоговые строки по счету, без КОСГУ, затем детальные с КОСГУ
        fo_line_bold = self._report.get_section('first_oborot_line_bold')
        fo_line = self._report.get_section('first_oborot_line')
        last_key_account = ''
        total_begin_debet = total_begin_credit = total_turn_debet = total_turn_credit = 0
        total_end_debet = total_end_credit = 0
        for row in data:
            account_key = row['account_key']
            if last_key_account != account_key:
                t = kosgu_totals[account_key]
                t['full_account_name'] = row['full_account_name'][:-3] + '000' # Как бы нет КОСГУ
                fo_line_bold.flush(t)
                last_key_account = account_key

            fo_line.flush(row)

            # Считаем итоги
            total_begin_debet += row['summa_begin_debet']
            total_begin_credit += row['summa_begin_credit']
            total_turn_debet += row['summa_turn_debet']
            total_turn_credit += row['summa_turn_credit']
            total_end_debet += row['summa_end_debet']
            total_end_credit += row['summa_end_credit']

        # Итоговая строка
        fo_total = self._report.get_section('first_oborot_total')
        fo_total.flush({
            'total_begin_debet': total_begin_debet,
            'total_begin_credit': total_begin_credit,
            'total_turn_debet': total_turn_debet,
            'total_turn_credit': total_turn_credit,
            'total_end_debet': total_end_debet,
            'total_end_credit': total_end_credit
        })

    # Эта часть отчета отключена
    def _create_second_oborot(self):
        dict_code = self.config_object.get_dict_code()
        if not dict_code:
            return

        # Шапка второй оборотки
        analytic_name = DictEnumerate.get_label_by_code(dict_code)
        fo_total = self._report.get_section('first_oborot_total')
        fo_total.flush({
            'analytic_name': analytic_name,
            })

    def _create_footer(self):
        """
        Формирует подвал отчета
        """
        #        mol = get_enterprise_official(self.ent_id, EnterpriseOfficialType.CHIEF_ACCOUNTANT)
        #        glavbuh = mol.person.get_short_fio() if mol else ''
        #
        #        profile = get_current_user_profile()
        #        username = profile.get_short_fio()

        footer = self._report.get_section('footer')
        footer.flush({
            'glavbuh': 123123,
            'username': 123123123123
        })

    def generate(self):
        """
        Генерирует отчет и возвращает url для скачивания
        """
        self._report = SpreadsheetReport(self.template_name)

        #main_rows, ppp_code = self._fetch_main_rows()

        self._create_header({})
        self._create_main({})
        self._create_middle({})
        # Оборотки отключены и не дописаны, т.к. никто из аналитиков не может понять как их правильно собирать. facepalm!
        #self._create_first_oborot()
        #self._create_second_oborot()
        self._create_footer()

        return self._report
