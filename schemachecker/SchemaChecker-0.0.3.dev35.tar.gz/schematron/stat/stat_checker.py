import os
from collections import OrderedDict
from lxml import etree
from .utils import Dict
from .interpreter import Interpreter, PeriodInterpreter
from .tokenizer import Tokenizer
from .dataframe import DataFrame
from .exceptions import *


#TODO: make its own class errors
class StatChecker:
    def __init__(self, *, root):
        self.root = root
        self.parser = etree.XMLParser(encoding='utf-8',
                                      recover=True,
                                      remove_comments=True)
        # Содержимое xml файла
        self.xml_report = Dict()
        self.xml_title = Dict()
        self.xml_sections = Dict()
        self.filename = None
        self.content = None
        self.okud = None

        # Содержимое компендиума проверочных схем
        self.compendium = Dict()

        # Словарь датафреймов, ключи - id секций
        self.frames = Dict()

        # Подготовка лексера и интерпретатора
        self.interpreter = Interpreter()
        self.period_interpreter = PeriodInterpreter()
        self.tokenizer = Tokenizer()
        self.condition, self.log_expr, self.period_cond = self.tokenizer.create_tokenizer()

    def process_input(self, filename, content):
        self.filename = filename
        self.content = content
        # Убираем расширение
        pure_filename = filename.split('.')[0]

        add_info_split = pure_filename.split('__')
        if len(add_info_split) > 1:
            # Дополнительная информация в заголовке файла
            add_info = add_info_split[1]

        # Основная информация в заголовке файла
        file_info = add_info_split[0].split('_')

        try:
            _okud, _idf, _idp, _okpo, _year = file_info[:5]
            _period = file_info[5]
            self.period_interpreter.period = _period
            self.okud = _okud
            if len(file_info) > 6:
                # Дополнительная, необязательная информация
                _extinfo = file_info[6:]
        except IndexError:
            raise InputError(self.filename,
                             'Формат названия файла не распознан')

        # Данные о статистическом отчёте
        self.xml_report = Dict(self.content.items())

        # Данные титульной страницы отчёта
        try:
            title_items = self.content.xpath('/report/title//item')
            for item in title_items:
                self.xml_title[item.attrib['name']] = item.attrib['value']
        except KeyError as ex:
            raise InputError(self.filename,
                             f'Не найден обязательный атрибут в элементе item: {ex}')

        # Данные о разделах
        sections = self.content.xpath('/report/sections//section')
        for section in sections:
            sec_code = section.attrib['code']
            try:
                self.frames[sec_code] = \
                    DataFrame.from_file_content(
                        section, self.compendium[_okud].sections[sec_code]
                    )
            except KeyError as ex:
                raise InputError(self.filename,
                                 f'Не найден обязательный атрибут в разделе sections: {ex}')

    #TODO: clear up the method
    def _parse_elements(self, rule, condition):
        """
        Вспомогательный метод для получения списка секций/строк/колонок/специфик
        для каждого правила и условия в компендиуме
        """
        element_map = Dict()

        # Определение секций для правила/условия
        r_sec, c_sec = None, None
        for element in rule:
            if type(element) == list:
                r_sec = element[0][0]
                break
        # Условие может отсутствовать
        if condition:
            for element in condition:
                if type(element) == list:
                    c_sec = element[0][0]
                    break

        element_map['section'] = r_sec, c_sec
        element_map['rows'] = tuple()
        element_map['cols'] = tuple()
        element_map['specs'] = tuple()

        return element_map

    def _create_df_structure(self, section):
        """
        Метод для инициализации структуры датафрейма в каждой секции
        при построении компендиума
        """
        df_struct = Dict()
        # Формирование структуры датафрейма по xml шаблону
        _section = int(section.code)
        # Словарь строк, ключ - номер строки, значение - массив индексов
        df_struct['rows'] = OrderedDict()
        # Словарь граф, ключ - номер графы, значение - индекс
        df_struct['cols'] = OrderedDict()
        # Двумерный массив специфик
        df_struct['specs'] = list()
        # Двумерный массив данных, построчный
        df_struct['data'] = list()
        # Вспомогательные массивы для быстрого поиска диапазонов
        df_struct['d_specs'] = [set(), set(), set()]

        # Добавление граф (колонок)
        idx = 0
        for col in section.columns.values():
            # Добавляем числовые колонки
            if col.type == 'Z':
                _col = int(col.code)
                df_struct['cols'][_col] = idx
                idx += 1
        df_struct['d_cols'] = list(df_struct['cols'].keys())

        # Добавление строк
        for row in section.rows.values():
            # Пропускаем не предназначенные для ввода строки
            if row.type != 'C':
                _row = int(row.code)
                df_struct['rows'][_row] = list()
        df_struct['d_rows'] = list(df_struct['rows'].keys())

        return df_struct

    def setup_compendium(self):
        self.compendium = Dict()

        comp_root = os.path.join(self.root, 'compendium')
        for root, dirs, files in os.walk(comp_root):
            for file in files:
                with open(os.path.join(root, file), 'r') as handler:
                    try:
                        content = etree.fromstring(handler.read(), parser=self.parser)
                    except etree.XMLSyntaxError as ex:
                        print(f'Ошибка при разборе .xml файла шаблона: {ex}')
                        continue

                scheme = Dict()
                # Данные раздела metaForm
                scheme['metaForm'] = Dict(content.items())

                # Данные раздела title
                title_items = content.xpath('/metaForm/title//item')
                title = Dict()
                try:
                    for item in title_items:
                        item_attribs = (item.attrib['name']) if not item.get('dic')\
                            else (item.attrib['name'], item.attrib['dic'])
                        title[item.attrib['field']] = item_attribs

                    scheme['title'] = title
                except KeyError as ex:
                    print(f'Не найден обязательный атрибут в элементе item: {ex}')

                # Данные раздела sections
                scheme['sections'] = Dict()
                sections = content.xpath('/metaForm/sections//section')
                for section in sections:
                    _section = Dict(section.items())

                    _section['columns'] = Dict()
                    _section['rows'] = Dict()

                    cols = section.xpath('./columns//column')
                    for col in cols:
                        _col = Dict(col.items())
                        default_cell = col.find('./default-cell')
                        if default_cell is not None:
                            _col['default-cell'] = Dict(default_cell.items())

                        _section['columns'][col.attrib['code']] = _col

                    rows = section.xpath('./rows//row')

                    for row in rows:
                        _row = Dict(row.items())

                        cells = row.xpath('./cell')
                        for cell in cells:
                            # Заполнение значения по умолчанию
                            if 'default' in cell.keys():
                                col_code = cell.attrib['column']
                                cell_default = cell.attrib['default']
                                _section['columns'][col_code]['default'] = cell_default

                        if _row.type != 'C':
                            _section['rows'][row.attrib['code']] = _row

                    # Создание структуры для датафрейма
                    _section['df_struct'] = self._create_df_structure(_section)

                    scheme['sections'][section.attrib['code']] = _section

                # Данные раздела controls
                scheme['controls'] = list()
                controls = content.xpath('/metaForm/controls//control')
                for control in controls:
                    _control = Dict(control.items())
                    # Нет информации о предыдущем периоде,
                    # пропускаем такие проверки
                    if '{{' in _control.rule.lower():
                        continue

                    # Парсинг и сохранение выражения
                    ex_rule = _control.rule
                    try:
                        _rule = self.tokenizer.tokenize_expression(
                            _control.rule.lower(), self.log_expr)
                        _control.rule = _rule
                    except Exception:
                        raise TokenizerError(ex_rule)

                    # Парсинг и сохранение условия
                    # Могут попадаться условия, содержащие только пробелы
                    if _control.condition and not _control.condition.isspace():
                        if '{{' in _control.condition.lower():
                            continue
                        ex_condition = _control.condition
                        try:
                            _condition = self.tokenizer.tokenize_expression(
                                _control.condition.lower(), self.condition)
                            _control.condition = _condition
                        except Exception:
                            raise TokenizerError(ex_condition)
                    else:
                        _control.condition = ''

                    # Парсинг и сохранение условия на период
                    if _control.periodClause and not _control.periodClause.isspace():
                        ex_period = _control.periodClause
                        try:
                            _period = self.tokenizer.tokenize_expression(
                                _control.periodClause.lower(), self.period_cond)
                            _control.period = _period
                        except Exception:
                            raise TokenizerError(ex_period)
                    else:
                        _control.period = ''

                    # Парсинг и получение списка строк/колонок/специфик
                    # для правила и условия
                    element_map = self._parse_elements(_control.rule,
                                                       _control.condition)
                    _control['section'] = element_map.section
                    _control['rows'] = element_map.rows
                    _control['cols'] = element_map.cols
                    _control['specs'] = element_map.specs

                    scheme['controls'].append(_control)

                # Данные справочников
                scheme['dics'] = Dict()
                dics = content.xpath('/metaForm/dics//dic')
                for dic in dics:
                    _dic = Dict(dic.items())
                    _dic['terms'] = Dict()
                    terms = dic.xpath('.//term')
                    for term in terms:
                        _dic['terms'][term.attrib['id']] = term.text

                    scheme['dics'][dic.attrib['id']] = _dic

                _okud = content.get('OKUD')
                if _okud:
                    self.compendium[_okud] = scheme
                else:
                    raise OkudError(self.filename)

    def check_file(self, input):
        self.filename = input.filename
        self.content = input.xml_obj

        input.verify_result = dict()

        input.verify_result['result'] = 'passed'
        input.verify_result['asserts'] = []

        try:
            self.process_input(self.filename, self.content)
        except InputError as ex:
            input.verify_result['result'] = 'failed'
            input.verify_result['description'] = ex
            return

        for control in self.compendium[self.okud].controls:
            # Секция, для которой выполняется проверка
            r_sec = str(control.section[0])
            # Секция заполнена
            if self.frames[r_sec].data.size != 0:
                period_cond = True
                condition = True
                try:
                    if control.period:
                        period_cond = self.period_interpreter\
                            .evaluate_expr(control.period)
                    if control.condition:
                        condition = self.interpreter\
                            .evaluate_expr_cond(control.condition, self.frames)
                    if period_cond and condition:
                        ret = self.interpreter\
                            .evaluate_expr(control.rule, self.frames)
                        # Проверка не выполнена, формируем отчёт с ошибкой
                        if not ret:
                            input.verify_result['asserts']\
                                .append((control.id, control.name))
                except InterpreterError as ex:
                    input.verify_result['result'] = 'failed'
                    input.verify_result['description'] = ex
                    return

        if input.verify_result['asserts']:
            input.verify_result['result'] = 'failed'
        return
