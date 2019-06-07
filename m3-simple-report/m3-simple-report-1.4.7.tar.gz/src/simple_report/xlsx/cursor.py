# coding: utf-8
from __future__ import absolute_import

import six

from simple_report.core.cursor import AbstractCalculateNextCursor
from simple_report.core.cursor import AbstractCursor
from simple_report.utils import ColumnHelper


class Cursor(AbstractCursor):
    """
    Специализированный курсор для XLSX таблиц.
    """

    def __init__(self, column=None, row=None,):
        """

        :param column: колонка
        :type column: 2-tuple
        :param row: строка
        :type row: 2-tuple
        """
        super(Cursor, self).__init__()
        self._column = column or ('A', 1)
        self._row = row or ('A', 1)

    def _test_value(self, value):
        """
        Проверка значения курсора

        :param value: значение курсора
        :type value: 2-tuple
        """

        super(Cursor, self)._test_value(value)

        # Координаты в XLSX таблицах имеют вид
        # (F, 3). F - имя стобла
        #         3 - номер строки. Нумерация строк с 1
        assert isinstance(value[0], six.string_types)


class CalculateNextCursorXLSX(AbstractCalculateNextCursor):
    u"""
    Вычисление следующего курсора
    """

    def get_next_column(self, current_col, end_col, begin_col):
        """
        Получение следующей колонки

        :param current_col: текущая колонка
        :type current_col: str
        :param end_col: конечная колонка
        :type end_col: str
        :param begin_col: начальная колонка
        :type begin_col: str
        """

        return ColumnHelper.add(current_col, ColumnHelper.difference(end_col, begin_col) + 1)

    def get_first_column(self):
        u"""
        Получение первой колонки
        """
        # Колонки имеют строкое представление
        return 'A'

    def get_first_row(self):
        u"""
        Получение первой строки
        """
        # Строки имеют числовое представление и нумер. с единицы.
        return 1

    def calculate_indent(self, column, w):
        """
        Получение колонки на `w` раньше чем `column`

        :param column: строковое представление колонки
        :type column: str
        :param w: смещение
        :type w: int
        """
        return ColumnHelper.number_to_column(
            ColumnHelper.column_to_number(column) - w)
