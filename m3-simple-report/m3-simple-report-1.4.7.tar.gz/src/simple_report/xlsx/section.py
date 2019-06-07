# coding: utf-8
from __future__ import absolute_import

from datetime import datetime
import copy
import numbers
import re

from lxml.etree import QName
from lxml.etree import SubElement
from six.moves import range
import six

from simple_report.core.exception import SheetDataException
from simple_report.core.shared_table import SharedStringsTable
from simple_report.core.spreadsheet_section import AbstractMerge
from simple_report.core.spreadsheet_section import SpreadsheetSection
from simple_report.core.tags import TemplateTags
from simple_report.interface import ISpreadsheetSection
from simple_report.utils import ColumnHelper
from simple_report.utils import FormulaWriteExcel
from simple_report.utils import FormulaWriteExcelFromStr
from simple_report.utils import date_to_float
from simple_report.utils import get_addr_cell
from simple_report.utils import split_string
from simple_report.xlsx.cursor import CalculateNextCursorXLSX
from simple_report.xlsx.cursor import Cursor
from simple_report.xlsx.formula import Formula


XLSX_GROUPING_COUNT = 30
ORIENTATION_LANDSCAPE = 'landscape'
ORIENTATION_PORTRAIT = 'portrait'
MAX_COLUMN_NAME_LEN = 3  # Максимальная колонка - XFD (2^14)


class SheetData(object):
    u"""
    self.read_data:
        <sheetData>
            <row collapsed="false" customFormat="false" customHeight="false" hidden="false" ht="12.8" outlineLevel="0" r="5">
                <c r="C5" s="1" t="s">
                    <v>0</v>
                </c>
                <c r="D5" s="1"/>
                <c r="E5" s="1"/>
            </row>
            <row collapsed="false" customFormat="false" customHeight="false" hidden="false" ht="12.8" outlineLevel="0" r="6">
                <c r="C6" s="0" t="s">
                    <v>1</v>
                </c>
            </row>
        </sheetData>

    self.read_dimension:
        <dimension ref="B5:I10"/>

    self.read_merge_cell:
        <mergeCells count="1">
            <mergeCell ref="C5:E5"/>
        </mergeCells>

    Данные для подобных write атрибутов должны быть такой же структуры
    """

    XPATH_TEMPLATE_ROW = '*[@r="%d"]'
    XPATH_TEMPLATE_CELL = '*[@r="%s"]'

    PREFIX_TAG = '%'

    FIND_PARAMS = re.compile(u'#[A-zА-яёЁ_0-9]+#')
    FIND_TEMPLATE_TAGS = re.compile(u'#{0}[A-zА-яёЁ_0-9]+{0}#'.format(PREFIX_TAG))

    COLUMN_INDEX = re.compile('[A-Z]+')
    ROW_INDEX = re.compile('[1-9][0-9]*')

    def __init__(self, sheet_xml, tags, cursor, ns, shared_table):
        # namespace
        self.ns = ns
        self.formula_id_dict = {}
        # Шаблонные теги
        assert isinstance(tags, TemplateTags)
        self.tags = tags

        assert isinstance(cursor, Cursor)
        self._cursor = cursor

        self._last_section = Cursor()

        assert isinstance(shared_table, SharedStringsTable)
        self.shared_table = shared_table

        self._read_xml = sheet_xml

        self.read_data = sheet_xml.find(QName(self.ns, 'sheetData'))
        if self.read_data is None:
            self.read_data = []

        self.read_dimension = sheet_xml.find(QName(self.ns, 'dimension'))
        if self.read_dimension is None:
            self.read_dimension = []

        self.read_merge_cell = sheet_xml.find(QName(self.ns, 'mergeCells'))
        if self.read_merge_cell is None:
            self.read_merge_cell = []

        # Строчные разделители страниц
        self.read_rowbreaks = self._read_xml.find(QName(self.ns, 'rowBreaks'))

        # Колоночные разделители страниц
        self.read_colbreaks = self._read_xml.find(QName(self.ns, 'colBreaks'))

        self._write_xml = copy.deepcopy(sheet_xml)

        # Ссылка на тег данных строк и столбцов листа с очищенными значениями
        self.write_data = self._write_xml.find(QName(self.ns, 'sheetData'))
        self._page_setup = self._write_xml.find(QName(self.ns, 'pageSetup'))

        self.write_data_dict = {}
        if not self.write_data is None:
            self.write_data.clear()

        # Ссылка на размеры листа
        self.write_dimension = self._write_xml.find(QName(self.ns, 'dimension'))

        # Ссылка на объединенные ячейки листа с очищенными значениями
        self.write_merge_cell = self._write_xml.find(QName(self.ns, 'mergeCells'))
        if self.write_merge_cell is not None:
            self.write_merge_cell.clear()

        # Ссылка на ширины столбцов
        self.write_cols = self._write_xml.find(QName(self.ns, 'cols'))
#        if self.write_cols is None:
#            self.write_cols = SubElement(self._write_xml, 'cols', attrib={})

        # Строчные разделители страниц
        self.write_rowbreaks = self._write_xml.find(QName(self.ns, 'rowBreaks'))
        # очистим, т.к. будем заполнять при копировании
        if self.write_rowbreaks is None:
            self.write_rowbreaks = SubElement(self._write_xml, 'rowBreaks', attrib={"count":"0", "manualBreakCount":"0"})
        else:
            self.write_rowbreaks.clear()
            self.write_rowbreaks.set("count", "0")
            self.write_rowbreaks.set("manualBreakCount", "0")

        # Колоночные разделители страниц
        self.write_colbreaks = self._write_xml.find(QName(self.ns, 'colBreaks'))
        # очистим, т.к. будем заполнять при копировании
        if self.write_colbreaks is None:
            self.write_colbreaks = SubElement(self._write_xml, 'colBreaks', attrib={"count":"0", "manualBreakCount":"0"})
        else:
            self.write_colbreaks.clear()
            self.write_colbreaks.set("count", "0")
            self.write_colbreaks.set("manualBreakCount", "0")

    @property
    def cursor(self):
        u"""
        Курсор
        """
        return self._cursor

    @cursor.setter
    def cursor(self, value):
        u"""
        Установка курсора
        :param value: новый курсор
        :type value: Cursor
        """
        assert isinstance(value, Cursor)
        self._cursor = value

    @property
    def last_section(self):
        u"""
        Последняя секция
        """
        return self._last_section

    @last_section.setter
    def last_section(self, value):
        """
        Установка последней секции
        :param value: курсор
        :type value: Cursor
        """
        assert isinstance(value, Cursor)
        self._last_section = value

    @property
    def default_row_height(self):
        u"""
        Высота строки по умолчанию
        """
        sheet_format = self._read_xml.find(QName(self.ns, 'sheetFormatPr'))
        if sheet_format is not None:
            return float(sheet_format.attrib.get('defaultRowHeight', 0))

    def flush(self, begin, end, start_cell, params, used_formulas=None):
        """
        Вывод секции
        :param begin: Начало секции, пример ('A', 1)
        :param end: Конец секции, пример ('E', 6)
        :param start_cell: ячейка с которой надо выводить
        :param params: данные для вывода
        """

        self.set_section(begin, end, start_cell, params, used_formulas)
        self.set_merge_cells(begin, end, start_cell)

        self.last_section.row = (
            self.cursor.row[0],
            max((self.cursor.row[1], self.last_section.row[1]))
        )

        self.last_section.column = (
            max((self.cursor.column[0], self.last_section.column[0])),
            self.cursor.column[1]
        )

        self.set_dimension()

        if self.write_cols is not None:
            self.set_columns_width(begin, end, start_cell)

        self.set_pagebreaks(begin, end, start_cell)

    def set_dimension(self):
        u"""
        Установка диапазона
        """
        _, row_index = self.last_section.row
        col_index, _ = self.last_section.column

        dimension = 'A1:%s' % \
                    (ColumnHelper.add(col_index, -1) + str(row_index - 1))

        self.write_dimension.set('ref', dimension)

    def _get_merge_cells(self):
        for cell in self.read_merge_cell:
            yield cell.attrib['ref'].split(':')

    def set_merge_cells(self, section_begin, section_end, start_cell):
        """
        Объединение ячеек
        
        :param section_begin: начало секции
        :type section_begin: 2-tuple
        :param section_end: конец секции
        :type section_end: 2-tuple
        :param start_cell: стартовая ячейка
        :type start_cell: 2-tuple
        """

        def cell_dimensions(section, merge_cell, start_cell):
            """
            Получение координаты ячейки после смещения из-за
            объединения ячеек
            
            :param section: начало секции
            :type section: 2-tuple
            :param merge_cell: начало объединенной ячейки
            :type merge_cell: 2-tuple
            :param start_cell: стартовая ячейка
            :type start_cell: 2-tuple
            """

            section_begin_col, section_begin_row = section

            start_col, start_row = start_cell

            begin_col, begin_row = merge_cell

            new_begin_row = start_row + begin_row - section_begin_row
            new_begin_col = ColumnHelper.add(start_col, ColumnHelper.difference(begin_col, section_begin_col))

            return new_begin_col + str(new_begin_row)

        range_rows, range_cols = self._range(section_begin, section_end)

        for begin, end in self._get_merge_cells():
            begin_col, begin_row = get_addr_cell(begin)
            end_col, end_row = get_addr_cell(end)

            # Если объединяемый диапазон лежит внутри секции
            if (begin_col in range_cols and end_col in range_cols and
                begin_row in range_rows and end_row in range_rows):
                begin_merge = cell_dimensions(section_begin, (begin_col, begin_row), start_cell)
                end_merge = cell_dimensions(section_begin, (end_col, end_row), start_cell)

                attrib = {'ref': ':'.join((begin_merge, end_merge))}
                SubElement(self.write_merge_cell, 'mergeCell', attrib)

        if self.write_merge_cell is not None:
            count_merge_cells = len(self.write_merge_cell)
            self.write_merge_cell.set('count', str(count_merge_cells))

    def _find_rows(self, range_rows):
        """
        Итератор по строкам
        
        :param range_rows: номера строк
        :type range_rows: iterable
        """
        for i, num_row in enumerate(range_rows):
            row = self.read_data.find(self.XPATH_TEMPLATE_ROW % num_row)
            if not row is None:
                yield i, num_row, row

    def _find_cells(self, range_cols, num_row, row):
        """
        Итератор по ячейкам
        
        :param range_cols: диапазон колонок
        :type range_cols: iterable
        :param num_row: номер строки
        :type num_row: int
        :param row: объект строки
        :type row: lxml.etree.Element
        """
        for j, col in enumerate(range_cols):
            cell = row.find(self.XPATH_TEMPLATE_CELL % (col + str(num_row)))
            if not cell is None:
                yield j, col, cell


    def _get_tag_value(self, cell):
        """
        Получение значения ячейки
        
        :param cell: ячейка
        :type cell: lxml.etree.Element
        """
        return cell.find(QName(self.ns, 'v'))

    def _get_params(self, cell):
        """
        Получение параметров ячейки 
        :param cell: ячейка
        :type cell: lxml.etree.Element
        """
        value = self._get_tag_value(cell)

        if not value is None and cell.get('t') == 's':  # 't' = 's' - значит есть значения shared strings
            index_value = int(value.text)
            value_string = self.shared_table.get_value(index_value)

            return self._get_values_by_re(value_string, self.FIND_PARAMS)
        else:
            return []

    def _get_values_by_re(self, value_string, what_found=None):
        """
        Получение значений по регулярному выражению
         
        :param value_string: строка, в которой ищем
        :type value_string: basestring
        :param what_found: регулярное выражение
        :type what_found: regexp
        """
        """
        """
        if what_found is None:
            # Если значение поиска неопределено выводим поиск для всех параметров
            return self._get_values_by_re(value_string, self.FIND_PARAMS) + \
                   self._get_values_by_re(value_string, self.FIND_TEMPLATE_TAGS)

        who_found_params = what_found.findall(value_string)
        if who_found_params is not None:
            return [found_param for found_param in who_found_params]
        else:
            return []

    def find_all_parameters(self, begin, end):
        """
        Получение всех параметров
        
        :param begin: начальная ячейка
        :type begin: 2-tuple
        :param end: конечная ячейка
        :type end: 2-tuple
        """
        range_rows, range_cols = self._range(begin, end)
        for i, num_row, row in self._find_rows(range_rows):
            for j, col, cell in self._find_cells(range_cols, num_row, row):
                for param in self._get_params(cell):
                    yield param

    def _get_tag_formula(self, cell):
        u"""
        Получение тега с формулой
        
        :param cell: ячейка
        :type cell: lxml.etree.Element
        """
        return cell.find(QName(self.ns, 'f'))

    def _create_or_get_output_row(self, row_index, attrib_row):
        u"""
        Получение выходной строки
        
        :param row_index: индекс строки
        :type row_index: int
        :param attrib_row: атрибуты строки
        :type attrib_row: dict
        """
        # найдем существующую строку в результирующих данных
        key = self.XPATH_TEMPLATE_ROW % row_index
        row_el = self.write_data_dict.get(key)

        if row_el is None:
            # если не нашли - создадим
            row_el = SubElement(self.write_data, 'row', attrib=attrib_row)
            self.write_data_dict[key] = row_el
        return row_el


    def _create_or_get_output_row_old(self, row_index, attrib_row):
        """
        Deprecated/unused
        
        :param row_index:
        :type row_index:
        :param attrib_row:
        :type attrib_row:
        """
        # найдем существующую строку в результирующих данных
        row_el = self.write_data.find(self.XPATH_TEMPLATE_ROW % row_index)

        if row_el is None:
            # если не нашли - создадим
            row_el = SubElement(self.write_data, 'row', attrib=attrib_row)
        return row_el

    def _create_or_get_output_cell(self, row_el, cell_index, attrib_cell):
        """
        Получение выходной ячейки
        
        :param row_el: элемент строки
        :type row_el: lxml.etree.Element
        :param cell_index: индекс ячейки
        :type cell_index: int
        :param attrib_cell: атрибуты ячейки
        :type attrib_cell: dict
        """
        # найдем существующую ячейку в строке
        cell_el = row_el.find(self.XPATH_TEMPLATE_CELL % cell_index)
        if cell_el is None:
            # если не нашли - создадим
            cell_el = SubElement(row_el, 'c', attrib=attrib_cell)
        return cell_el

    def set_section(self, begin, end, start_cell, params, used_formulas=None):
        u"""
        Вывод секции

        :param begin: начальная ячейка секции
        :type begin: 2-tuple
        :param end: конечная ячейка секции
        :type end: 2-tuple
        :param start_cell: стартовая ячейка (с которой начинается запись)
        :type start_cell: 2-tuple
        :param params: параметры отчета
        :type params: dict
        :param used_formulas: используемые формулы
        :type used_formulas: dict
        """
        # TODO: разбить на методы
        range_rows, range_cols = self._range(begin, end)
        start_column, start_row = start_cell
        if used_formulas is None:
            used_formulas = {}

        for i, num_row, row in self._find_rows(range_rows):
            attrib_row = dict(list(row.items()))

            row_index = start_row + i
            attrib_row['r'] = str(row_index)
            # следующая строка создает линейное время для флаша от числа флашей
            row_el = self._create_or_get_output_row(row_index, attrib_row)

            for j, col, cell in self._find_cells(range_cols, num_row, row):
                attrib_cell = dict(list(cell.items()))

                col_index = ColumnHelper.add(start_column, j)

                attrib_cell['r'] = col_index + str(row_index)

                cell_el = self._create_or_get_output_cell(row_el, col_index + str(row_index), attrib_cell)

                # Перенос формул
                formula = self._get_tag_formula(cell)
                if formula is not None:
                    formula_el = SubElement(cell_el, 'f')

                    row_cursor_column, row_cursor_row = self.cursor.row
                    column_cursor_column, column_cursor_row = self.cursor.column
                    formula_el.text = Formula.get_instance(formula.text).get_next_formula(row_cursor_row,
                                                                                          column_cursor_column)
                    # Если есть формула, то значение является вычисляемым параметром и не сильно интересует
                    continue

                value = self._get_tag_value(cell)
                if not value is None:
                    value_el = SubElement(cell_el, 'v')

                    if attrib_cell.get('t') in ('n', None):  # number

                        value_el.text = value.text

                    elif attrib_cell.get('t') == 's':  # 't' = 's' - значит есть значения shared strings

                        index_value = int(value.text)
                        value_string = self.shared_table.get_value(index_value)

                        who_found_params = self._get_values_by_re(value_string)
                        is_int = False
                        if who_found_params:
                            for found_param in who_found_params:
                                param_name = found_param[1:-1]

                                param_value = params.get(param_name)
                                if used_formulas:
                                    formula_id_list = used_formulas.get(param_name)
                                    assert (
                                        formula_id_list is None or
                                        isinstance(
                                            formula_id_list,
                                            (list, tuple))
                                    ), ("used_formulas values must be "
                                        "lists or tuples")
                                    if formula_id_list is not None:
                                        for formula_id in formula_id_list:
                                            cell_string = ''.join([col_index,
                                                                str(row_index)])
                                            self.formula_id_dict.setdefault(
                                                formula_id, []).append(cell_string)
                                # Находим теги шаблонов, если есть таковые
                                if param_name[0] == self.PREFIX_TAG and param_name[-1] == self.PREFIX_TAG:
                                    param_value = self.tags.get(param_name[1:-1])

                                if isinstance(param_value, datetime) and found_param == value_string:
                                    # В OpenXML хранится дата относительно 1900 года
                                    days = date_to_float(param_value)
                                    if days > 0:
                                        # Дата конвертируется в int, начиная с 31.12.1899
                                        is_int = True
                                        cell_el.attrib['t'] = 'n'  # type - number
                                        value_el.text = six.text_type(days)
                                    else:
                                        date_less_1900 = '%s.%s.%s' % (
                                            param_value.date().day,
                                            param_value.date().month,
                                            param_value.date().year
                                        )
                                        # strftime(param_value, locale.nl_langinfo(locale.D_FMT)) - неработает для 1900 и ниже
                                        value_string = value_string.replace(found_param, six.text_type(date_less_1900))

                                elif (isinstance(param_value, numbers.Number) and
                                      found_param == value_string):
                                    # В первую очередь добавляем числовые значения
                                    is_int = True

                                    cell_el.attrib['t'] = 'n'  # type - number
                                    value_el.text = six.text_type(param_value)

                                elif isinstance(param_value, six.string_types):
                                    # Строковые параметры

                                    value_string = value_string.replace(found_param, six.text_type(param_value))

                                elif isinstance(param_value, FormulaWriteExcel):
                                    # Записываем формулу, которой не было в
                                    # шаблоне
                                    func_ = param_value.excel_function
                                    f_id = param_value.formula_id
                                    if f_id and func_:
                                        attrib_cell['t'] = 'e'
                                        # тип вычислимого по формуле поля
                                        cell_el.remove(value_el)
                                        # значения в ячейке с формулой нет
                                        formula_el = SubElement(cell_el, 'f')
                                        row_cursor_column, row_cursor_row = self.cursor.row
                                        column_cursor_column, column_cursor_row = self.cursor.column
                                        f_cells = self.formula_id_dict.get(
                                            f_id, [])
                                        if param_value.ranged and f_cells:
                                            formula_el.text = '%s(%s)' % (
                                                func_, ':'.join([f_cells[0],
                                                                f_cells[-1]])
                                                )
                                        elif f_cells:
                                            # Группируем по 30 элементов
                                            cells_number = int(
                                                len(f_cells) // XLSX_GROUPING_COUNT
                                            ) + 1
                                            val_list = []
                                            for x in range(cells_number):
                                                sub_args = (
                                                    ','.join(
                                                        f_cells[x * XLSX_GROUPING_COUNT:(x + 1) * XLSX_GROUPING_COUNT]
                                                    )
                                                )
                                                if sub_args:
                                                    sub_val = '(%s)' % (
                                                        sub_args
                                                    )
                                                    val_list.append(sub_val)

                                            formula_el.text = '%s(%s)' % (
                                                func_,
                                                ','.join(val_list)
                                            )

                                        self.formula_id_dict[f_id] = []
                                    else:
                                        continue

                                elif isinstance(
                                        param_value, FormulaWriteExcelFromStr):
                                    # Записываем кастомную формулу из строки
                                    attrib_cell['t'] = 'e'
                                    # тип вычислимого по формуле поля
                                    cell_el.remove(value_el)
                                    # значения в ячейке с формулой
                                    formula_el = SubElement(cell_el, 'f')
                                    formula_el.text = param_value.text

                                elif param_value:
                                    # любой объект, например список или
                                    # словарь. Вынесено для производительности

                                    value_string = value_string.replace(found_param, six.text_type(param_value))

                                else:
                                    # Не передано значение параметра
                                    value_string = value_string.replace(found_param, '')
                            value_string = adjust_row_height_and_split_string(
                                row_el, value_string, Section.MIN_ROW_HEIGHT
                            )
                            if not is_int:
                                # Добавим данные в shared strings

                                new_index = self.shared_table.get_new_index(value_string)
                                value_el.text = new_index

                        else:
                            # Параметры в поле не найдены

                            index = self.shared_table.get_new_index(value_string)
                            value_el.text = index

                    elif attrib_cell.get('t'):
                        raise SheetDataException("Unknown value '%s' for tag t" % attrib_cell.get('t'))

    def _range(self, begin, end):
        u"""
        Диапазон строк, колонок
        
        :param begin: начальная ячейка 
        :type begin: 2-tuple
        :param end: конечная ячейка
        :type end: 2-tuple
        """

        # Если есть объединенная ячейка, и она попадает на конец секции, то адресс конца секции записывается как конец
        # объединенной ячейки
        end = self.get_cell_end(end)

        rows = begin[1], end[1] + 1
        cols = begin[0], end[0]

        range_rows = range(*rows)
        range_cols = list(ColumnHelper.get_range(*cols))

        return range_rows, range_cols

    def _addr_in_range(self, addr, begin, end):
        u"""
        Проверяет, попадает ли адрес в диапазон
        
        :param addr: адрес ячейки
        :type addr: 2-tuple
        :param begin: начальная ячейка диапазона
        :type begin: 2-tuple
        :param end: конечная ячейка диапазона
        :type end: 2-tuple
        """
        col, row = addr
        rows = range(begin[1], end[1] + 1)
        cols = list(ColumnHelper.get_range(begin[0], end[0]))
        return all([col in cols, row in rows])

    def get_cell_end(self, cell_addr):
        """
        Получение (правого нижнего) конца ячейки
        
        :param cell_addr: адрес ячейки
        :type cell_addr: 2-tuple
        """
        cell_end = cell_addr
        # Если указанный адрес пападает в объединенную ячейку, то адресс конца ячейки указывается как конец
        # объединенной ячейки
        for begin_merge, end_merge in self._get_merge_cells():
            begin_addr = get_addr_cell(begin_merge)
            end_addr = get_addr_cell(end_merge)
            if self._addr_in_range(cell_addr, begin_addr, end_addr):
                cell_end = end_addr
                break
        return cell_end

    def new_sheet(self):
        """
        """

        if self.write_merge_cell is not None:
            childs = self.write_merge_cell.getchildren()
            if not childs:
                self._write_xml.remove(self.write_merge_cell)

        if self.write_cols is not None and not self.write_cols.getchildren():
            self._write_xml.remove(self.write_cols)

        # если небыло разделителей страниц, то удалим раздел
        if not self.write_colbreaks.getchildren():
            self._write_xml.remove(self.write_colbreaks)
        if not self.write_rowbreaks.getchildren():
            self._write_xml.remove(self.write_rowbreaks)

        return self._write_xml

    def _create_or_get_output_col(self, col_index, attrib_col=None):
        """
        Найдем существующую колонку в результирующих данных
        Если не передали начальные данные, то колонка не создается,
        если не найдена,
        
        :param col_index: индекс колонки
        :type col_index: int
        :param attrib_col: атрибуты элемента колонки
        :type attrib_col: dict
        """
        # найдем интервал, в который попадаем искомый индекс
        col_index = ColumnHelper.column_to_number(col_index) + 1
        col_el = None
        for col in self.write_cols.getchildren():
            begin_col = int(col.attrib['min'])
            end_col = int(col.attrib['max'])
            if begin_col <= col_index <= end_col:
                col_el = col
                break

        if col_el is None:
            # если не нашли - создадим
            if attrib_col is None:
                return None
            attrib_col["min"] = str(col_index)
            attrib_col["max"] = str(col_index)
            col_el = SubElement(self.write_cols, 'col', attrib=attrib_col)
        return col_el

    def _set_new_column_width(self, col_index, src_col, dst_col):
        """
        Установка новой ширины колонки
        Особенность в том, что нужно разбивать интервалы, если потребуется
        
        :param col_index: индекс колонки
        :type col_index: int
        :param src_col: элемент исходной колонки
        :type src_col: lxml.etree.Element
        :param dst_col: элемент выходной колонки
        :type dst_col: lxml.etree.Element
        """
        col_index = ColumnHelper.column_to_number(col_index) + 1
        # если ширина колонок отличается и колонка-приемник является интервалом,
        # то нужно разбить интервал на части с разной шириной колонок
        if dst_col.attrib["width"] != src_col.attrib["width"]:
            begin_col = int(dst_col.attrib['min'])
            end_col = int(dst_col.attrib['max'])
            # если задано интервалом, то будем разбивать
            if end_col - begin_col > 0:
                if col_index > begin_col:
                    # предыдущий интервал: max = col-1
                    prev_attrib_col = dict(list(dst_col.items()))
                    prev_attrib_col['max'] = str(col_index - 1)
                    prev_col_el = SubElement(self.write_cols, 'col', attrib=prev_attrib_col)

                if col_index < end_col:
                    # следующий интервал: min = col+1
                    next_attrib_col = dict(list(dst_col.items()))
                    next_attrib_col["min"] = str(col_index + 1)
                    next_col_el = SubElement(self.write_cols, 'col', attrib=next_attrib_col)

                # интервал для текущей колонки: min = max = col
                dst_col.attrib["min"] = str(col_index)
                dst_col.attrib["max"] = str(col_index)

            dst_col.attrib["width"] = src_col.attrib["width"]

    def set_columns_width(self, begin, end, start_cell):
        """
        Копирование ширины колонок
        :param begin: начало секции, пример ('A', 1)
        :type begin: 2-tuple
        :param end: конец секции, пример ('E', 6)
        :type end: 2-tuple
        :param start_cell: ячейка с которой выводилась секция
        :type start_cell: 2-tuple
        """
        # определим интервал столбцов из которых надо взять ширину
        end = self.get_cell_end(end)
        cols = list(ColumnHelper.get_range(begin[0], end[0]))

        # определим интервал столбцов, начинаемый со столбца начальной ячейки, куда надо прописать ширину
        end_col = ColumnHelper.add(start_cell[0], ColumnHelper.difference(end[0], begin[0]))
        new_cols = list(ColumnHelper.get_range(start_cell[0], end_col))

        # запишем ширину столбцов в интервал
        for index, src_col in enumerate(cols):
            dst_col = new_cols[index]
            src_col_el = self._create_or_get_output_col(src_col)
            # если нет исходной колонки, то не надо копировать
            if not src_col_el is None:
                # копируем данные
                attrib_col = dict(list(src_col_el.items()))
                dst_col_el = self._create_or_get_output_col(dst_col, attrib_col)
                # записываем в новую колонку
                self._set_new_column_width(dst_col, src_col_el, dst_col_el)

    def get_rowbreaks(self):
        u"""
        Получение разрывов строк
        """
        breaks = [elem.attrib['id'] for elem in self.write_rowbreaks.getchildren()]
        return tuple(breaks)

    def get_colbreaks(self):
        u"""
        Получение разрывов колонок
        """
        breaks = [elem.attrib['id'] for elem in self.write_colbreaks.getchildren()]
        return tuple(breaks)


    def _set_colpagebreaks(self, colbreaks_list):
        """
        Добавление разделителей страниц по колонкам
        
        :param colbreaks_list:
        :type colbreaks_list:
        """
        # добавим разделители
        for new_col_index in colbreaks_list:
            # проверим что такого разделителя еще нет
            found = False
            for elem in self.write_colbreaks.getchildren():
                index = int(elem.attrib['id'])
                if index == new_col_index:
                    found = True
                    break
            # добавим
            if not found:
                col_break_attr = {'id': str(new_col_index), 'max': '1048575', 'man':'1'}
                elem = SubElement(self.write_colbreaks, 'brk', attrib=col_break_attr)
                count = int(self.write_colbreaks.get('count', 0))
                man_count = int(self.write_colbreaks.get('manualBreakCount', 0))
                self.write_colbreaks.attrib['count'] = str(count + 1)
                self.write_colbreaks.attrib['manualBreakCount'] = str(man_count + 1)

    def _set_rowpagebreaks(self, rowbreaks_list):
        """
        Добавление разделителей страниц по строкам
        
        :param rowbreaks_list:
        :type rowbreaks_list:
        """
        # добавим разделители
        for new_row_index in rowbreaks_list:
            # проверим что такого разделителя еще нет
            found = False
            for elem in self.write_rowbreaks.getchildren():
                index = int(elem.attrib['id'])
                if index == new_row_index:
                    found = True
                    break
                    # добавим
            if not found:
                row_break_attr = {'id': str(new_row_index), 'max': '16383', 'man':'1'}
                elem = SubElement(self.write_rowbreaks, 'brk', attrib=row_break_attr)
                count = int(self.write_rowbreaks.get('count', 0))
                man_count = int(self.write_rowbreaks.get('manualBreakCount', 0))
                self.write_rowbreaks.attrib['count'] = str(count + 1)
                self.write_rowbreaks.attrib['manualBreakCount'] = str(man_count + 1)

    def set_pagebreaks(self, begin, end, start_cell):
        """
        Копирование разделителей страниц
        :param begin: начало секции, пример ('A', 1)
        :type begin: 2-tuple
        :param end: конец секции, пример ('E', 6)
        :type end: 2-tuple
        :param start_cell: ячейка с которой выводилась секция
        :type start_cell: 2-tuple
        """
        # определим интервал столбцов и колонок из которых надо взять разделители
        end = self.get_cell_end(end)
        begin_col = ColumnHelper.column_to_number(begin[0])
        end_col = ColumnHelper.column_to_number(end[0])
        begin_row = int(begin[1])
        end_row = int(end[1])
        # определим интервал столбцов и колонок, начинаемый с начальной ячейки, куда надо добавить разделители
        new_begin_col = ColumnHelper.column_to_number(start_cell[0])
        new_begin_row = int(start_cell[1])
        # вытащим смещение индексов столбцов у которых есть разделители и которые попали в этот интервал
        colbreaks = []
        if self.read_colbreaks is not None:
            for elem in self.read_colbreaks.getchildren():
                col_index = int(elem.attrib['id'])
                if begin_col <= col_index - 1 <= end_col:
                    colbreaks.append(col_index - begin_col + new_begin_col)

        self._set_colpagebreaks(colbreaks)

        # вытащим смещение индексов строк у которых есть разделители и которые попали в этот интервал
        rowbreaks = []
        if self.read_rowbreaks is not None:
            for elem in self.read_rowbreaks.getchildren():
                row_index = int(elem.attrib['id'])
                if begin_row <= row_index <= end_row:
                    rowbreaks.append(row_index - begin_row + new_begin_row)

        self._set_rowpagebreaks(rowbreaks)

    def prepare_merge(self, begin_new_merge, end_new_merge):
        """
        Если в документе имеются объединенные ячейки и мы добавляем свою
        область перес. данную, то необходимо прежде всего удалить,
        то что уже имеется.
        
        :param begin_new_merge: начало диапазона
        :type begin_new_merge: 2-tuple
        :param end_new_merge: конец диапазона
        :type end_new_merge: 2-tuple
        """
        def align_chars(col):
            """Выравнивает имя колонки для выполнения сравнений"""
            return col.zfill(MAX_COLUMN_NAME_LEN)

        begin_new_col, begin_new_row = get_addr_cell(begin_new_merge)
        end_new_col, end_new_row = get_addr_cell(end_new_merge)

        # Все смерженные ячейки на листе
        merge_cells = self._write_xml.xpath('.//mergeCell')
        for merge_cell in merge_cells:

            ref_attr = merge_cell.attrib.get('ref')  # D1:D3 Например
            begin_old_merge, end_old_merge = ref_attr.split(':')  # D1, D3

            begin_old_col, begin_old_row = get_addr_cell(begin_old_merge)
            end_old_col, end_old_row = get_addr_cell(end_old_merge)

            if not (
                    align_chars(begin_new_col) > align_chars(end_old_col) or
                    align_chars(end_new_col) < align_chars(begin_old_col) or
                    begin_new_row > end_old_row or
                    end_new_row < begin_old_row):

                self.write_merge_cell.remove(merge_cell)

    def set_orientation(self, orientation):
        """
        Задать ориентацию страницы для данного листа
        :param orientation: 'portrait' или 'landscape'
        """
        if self._page_setup is not None:
            assert orientation in (
                ORIENTATION_LANDSCAPE,
                ORIENTATION_PORTRAIT
            )
            self._page_setup.attrib['orientation'] = orientation

class Section(SpreadsheetSection, ISpreadsheetSection):
    u"""
    Секция отчета
    """

    MIN_ROW_HEIGHT = 6.
    DEFAULT_ROW_HEIGHT = 15.

    def __init__(self, sheet_data, name, begin=None, end=None):
        """
        :param sheet_data: Данные листа
        :param name: Название секции
        :param begin: Начало секции, пример ('A', 1)
        :param end: Конец секции, пример ('E', 6)
        """
        super(Section, self).__init__(sheet_data, name, begin, end)

        # Ссылка на курсор листа. Метод flush вставляет данные относительно курсора
        # и меняет его местоположение
        assert isinstance(sheet_data, SheetData)
        self.sheet_data = sheet_data

    def __str__(self):
        return 'Section "{0} - ({1},{2}) \n\t sheet_data - {3}" '.format(
            self.name, self.begin, self.end, self.sheet_data)

    def __repr__(self):
        return self.__str__()

    def get_copy(self):
        u"""
        Получение копии секции, в которой можно манипулировать
        входными данными без побочных эффектов на другие секции
        :param self:
        :return:
        """
        section_copy = copy.copy(self)
        section_copy.sheet_data = copy.copy(self.sheet_data)
        section_copy.sheet_data.read_data = copy.copy(self.sheet_data.read_data)
        return section_copy

    def flush(
        self, params, oriented=ISpreadsheetSection.LEFT_DOWN,
        used_formulas=None
    ):
        """
        Вывод. Имеется два механизма вывода.
        Для использования старого не передавать direction

        :param params: параметры замены
        :type params: dict
        :param oriented: направление ориентации
        :type oriented: ISpreadsheetSection
        :param used_formulas: использованные формулы
        :type used_formulas: dict
        """
        assert isinstance(params, dict)
        assert oriented in (Section.VERTICAL,
                            Section.HORIZONTAL,
                            Section.LEFT_DOWN,
                            Section.RIGHT_UP,
                            Section.RIGHT,
                            Section.HIERARCHICAL)

        if oriented == Section.HIERARCHICAL:
            # Тут смещение курсора, копирование данных из листа и общих строк
            # Генерация новых данных и новых общих строк

            cursor = self.sheet_data.cursor

            begin_col, begin_row = self.begin
            end_col, end_row = self.sheet_data.get_cell_end(self.end)

            current_col, current_row = CalculateNextCursorXLSX().get_next_cursor(
                cursor, (begin_col, begin_row),
                (end_col, end_row), oriented, self
            )
        else:
            current_col, current_row = (
                CalculateNextCursorXLSX().get_next_cursor(
                    self.sheet_data.cursor,
                    self.begin,
                    self.sheet_data.get_cell_end(self.end),
                    oriented, None
                )
            )

        self.sheet_data.flush(
            self.begin, self.end,
            (current_col, current_row),
            params,
            used_formulas
        )

    def get_all_parameters(self):
        u"""
        Возвращает все параметры секции
        """
        return self.sheet_data.find_all_parameters(self.begin, self.end)

    def get_width(self):
        u"""
        Получение ширины секции
        """

        begin_col, begin_row = self.begin
        end_col, end_row = self.sheet_data.get_cell_end(self.end)

        return ColumnHelper.difference(end_col, begin_col) + 1

    def get_total_height(self):
        u"""
        Возвращает полную высоту секции. Если нужна высота секции с учётом текста,
        то её следует перед вызовом этого метода заполнить при помощи метода fill
        :return: Высота секции в точках Excel
        :rtype: int
        """
        sheet_data = self.sheet_data
        rows_range, col_range = sheet_data._range(
            self.begin, self.end
        )
        default_row_height = (
            sheet_data.default_row_height or
            self.DEFAULT_ROW_HEIGHT
        )
        total_height = 0.
        for _, _, row in sheet_data._find_rows(rows_range):
            row_height = row.attrib.get('ht')
            total_height += (
                float(row_height) if row_height else default_row_height
            )
        return total_height

    def _substitute_param(self, found_param, params, value_string):
        u"""
        Подстановка параметров в строку
        :param found_param: найденный в строке параметр
        :param params: Словарь параметров
        :param value_string: Исходная строка
        :return: Строка с подставленными параметрами
        :rtype: six.text_type
        """
        param_name = found_param[1:-1]
        param_value = params.get(param_name)
        sheet_data = self.sheet_data

        value_type = 's'

        if (param_name[0] == sheet_data.PREFIX_TAG and
                param_name[-1] == sheet_data.PREFIX_TAG):
            param_value = sheet_data.tags.get(param_name[1:-1])

        if (isinstance(param_value, datetime) and
                found_param == value_string):
            # В OpenXML хранится дата относительно 1900 года
            days = date_to_float(param_value)
            if days > 0:
                # Дата конвертируется в int, начиная с
                # 31.12.1899
                value_type = 'n'
                value_string = six.text_type(days)
            else:
                date_less_1900 = '%s.%s.%s' % (
                    param_value.date().day,
                    param_value.date().month,
                    param_value.date().year
                )
                value_string = value_string.replace(
                    found_param, six.text_type(date_less_1900))

        elif (isinstance(param_value, numbers.Number) and
                found_param == value_string):
            value_string = six.text_type(param_value)
            value_type = 'n'
            # В первую очередь добавляем числовые значения

        elif isinstance(param_value, six.string_types):
            # Строковые параметры

            value_string = value_string.replace(
                found_param, six.text_type(param_value))

        elif param_value:
            # любой объект, например список или
            # словарь. Вынесено для производительности

            value_string = value_string.replace(
                found_param, six.text_type(param_value))

        else:
            # Не передано значение параметра
            value_string = value_string.replace(
                found_param, '')

        return value_string, value_type

    def _write_to_cell(self, cell, value_string, value_type):
        u"""
        Запись значения в ячейку
        :param cell: XML объект ячейки
        :param value_string: Содержимое ячейки в виде строки
        :param value_type: тип содержимого ячейки:
                           's' (строка) или 'n' (число)
        :return: None
        """
        sheet_data = self.sheet_data
        is_int = (value_type == 'n')
        if is_int:
            cell.attrib['t'] = value_type

            value_element = cell.find(
                'v',
                namespaces={None: self.sheet_data.ns}
            )
            if value_element is not None:
                value_element.text = value_string
            else:
                cell.text = six.text_type(value_string)

        else:
            # Добавим данные в shared strings
            sheet_data.shared_table.elements.append(value_string)
            new_index = len(sheet_data.shared_table.elements) - 1
            sheet_data._get_tag_value(cell).text = six.text_type(new_index)

    def fill(self, params):
        u"""
        Подстановка параметров in-place.
        Пример использования: перед выводом секции нужно проверить, что
        она помещается на страницу

        section_copy = section.get_copy()
        section_copy.fill(params)
        section_height = section_copy.get_total_height()
        if( ... ):
            section_copy.flush({})  # все данные уже зашиты в section_copy
        """
        sheet_data = self.sheet_data
        range_rows, range_cols = sheet_data._range(self.begin, self.end)

        for i, num_row, row in sheet_data._find_rows(range_rows):
            for j, col, cell in sheet_data._find_cells(range_cols, num_row, row):
                attrib_cell = dict(cell.items())

                col_index = col

                attrib_cell['r'] = col_index + str(num_row)

                value = sheet_data._get_tag_value(cell)
                if value is None:
                    continue

                if attrib_cell.get('t') in ('n', None):  # number
                    pass

                elif attrib_cell.get('t') == 's':
                    # 't' = 's' - значит есть значения shared strings
                    index_value = int(value.text)
                    value_string = sheet_data.shared_table.get_value(index_value)

                    who_found_params = sheet_data._get_values_by_re(value_string) or []

                    for found_param in who_found_params:

                        value_string, value_type = self._substitute_param(
                            found_param,
                            params,
                            value_string
                        )

                        value_string = adjust_row_height_and_split_string(
                            row, value_string, self.MIN_ROW_HEIGHT
                        )

                        self._write_to_cell(cell, value_string, value_type)

                elif attrib_cell.get('t'):
                    raise SheetDataException(
                        "Unknown value '%s' for tag t" % attrib_cell.get('t'))


def adjust_row_height_and_split_string(row_el, value_string, min_row_height):
    u"""
    Реализация возможности подбора высоты строки.

    В строке должен находится маркер вида:

      @@max_length:line_height[,offset][:force_split[:sep]]@@

    max_length - Максимальное количество символов
      в ячейке, после которого нужен перенос.

    line_height - Высота ряда, может быть не целым числом
       (разделитель - точка)

    offset - фиксированный отступ по вертикали, т.е.
      полная высота ячейки
        number_of_lines * line_height + offset
      по умолчанию offset = 0

    force_split - Флаг (1 или 0). Следует ли разбить
      строку принудительно.

    sep - Опционально: символ-разделитель.
      По умолчанию - пробел.

    Пример маркера: @@65:15,3.5:0:.@@

    :param row_el: XML элемент строки
    :param value_string: Текст в строке
    :param min_row_height: Минимальная высота строки в точках Excel
    :return: текст, разбитый на строки
    :rtype: basestring
    """

    RE_AUTOHEIGHT_MARKER = re.compile(
        '@@(?P<max_length>[^:]+)'
        ':('
        '(?P<line_height>[^:,]+)'
        '(,(?P<offset>[^:]+))?)'
        '(:(?P<force_split>[^:@]+)'
        '(:(?P<sep>[^@]+))?'
        ')?@@'
    )

    split_settings = RE_AUTOHEIGHT_MARKER.search(
        value_string)

    if split_settings:
        line_max_len = int(
            split_settings.group('max_length').strip(u'@'))
        line_height = float(split_settings.group('line_height'))

        offset = float(split_settings.group('offset') or 0)

        force_split = int(split_settings.group('force_split') or 0)

        len_sep = split_settings.group('sep')

        value_string = value_string.replace(
            split_settings.group(0), '')

        string_split = split_string(value_string, line_max_len)
        lines_count = len(string_split)

        if force_split:
            # Принудительно разбиваем строку на несколько.
            value_string = '\n'.join(string_split)

        current_height = float(
            row_el.attrib.get('ht', min_row_height))

        height = lines_count * line_height + offset

        row_el.attrib['ht'] = str(max(height, current_height))
        row_el.attrib['customHeight'] = '1'

    return value_string


class MergeXLSX(AbstractMerge):
    u"""
    Менеджер контекста для объединения ячеек
    """

    def _merge(self):

        begin_merge = ''.join([self._begin_merge_col, str(self.begin_row_merge)])
        end_merge = ''.join([self._end_merge_col, str(self.end_row_merge)])

        attrib = {'ref': ':'.join([begin_merge, end_merge])}

        if self.section.sheet_data.write_merge_cell is None:
            self.section.sheet_data.write_merge_cell = SubElement(self.section.sheet_data._write_xml, 'mergeCells')

        self.sheet_data.prepare_merge(begin_merge, end_merge)

        SubElement(self.section.sheet_data.write_merge_cell, 'mergeCell', attrib)

    def _calculate_merge_column(self, column):

        column_number = ColumnHelper.column_to_number(column)

        first_section_column = ColumnHelper.number_to_column(column_number - self.section.get_width())
        last_section_column = ColumnHelper.number_to_column(column_number - 1)

        return first_section_column, last_section_column
