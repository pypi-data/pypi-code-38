# coding: utf-8
from __future__ import absolute_import

import abc

import six

from simple_report.interface import ISpreadsheetSection
from simple_report.utils import ColumnHelper


class SpreadsheetSection(six.with_metaclass(abc.ABCMeta, object)):

    def __init__(self, sheet, name, begin=None, end=None):
        """
        Абстракная секция для таблиц
        """

        assert begin or end

        self.name = name
        self.begin = begin
        self.end = end

    @abc.abstractmethod
    def get_width(self):
        """
        @summary получение ширины секции
        :result: ширина секции
        """

    def get_indent(self):
        """
         получение полного сдвига
        :result: сдвиг с учетом дочерних секций
        """

        indent = self.get_width()
        if hasattr(self, 'child'):
            indent += self.child.get_indent()

        return indent


class AbstractMerge(six.with_metaclass(abc.ABCMeta, object)):
    """
    Конструкция Merge
    """

    def __init__(self, parent_section, child_section, params, oriented=ISpreadsheetSection.LEFT_DOWN):

        self.section = parent_section
        self.params = params
        self.oriented = oriented

        self.section.child = child_section
        self.sheet_data = self.section.sheet_data

    def __enter__(self):

        # Строка с которой начинаем обьединять ячейки
        self.begin_row_merge = self._get_border_row()

        self.section.flush(self.params, self.oriented)

        # Индекс колонки, которую мержим
        column, _ = self.section.sheet_data.cursor.column
        self._begin_merge_col, self._end_merge_col = self._calculate_merge_column(column)

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        """

        self.end_row_merge = self._get_border_row(top_border=False)
        self._merge()

    @abc.abstractmethod
    def _calculate_merge_column(self, column):
        """
         Вычисление столбца, строки которого будем мержить.
        По сути вернуть предыдущий столбец
        :param column: предыдущая колонка
        :result: новая колонка
        """

    @abc.abstractmethod
    def _merge(self):
        """
        Слияние
        """

    def _get_border_row(self, top_border=True):
        """
        Вычисление номера строки с которой необходимо
        начать и закончить мержить
        :param top_border: Верхняя граница
        :type top_border: bool
        """
        # Результат работы зависит от курсора.
        # Параметр begin указывает на то, какая граница вычисляется.
        # top_border = True - Верхняя граница

        # Колонка и строка курсора row
        _, r_row = self.section.sheet_data.cursor.row
        _, c_row = self.section.sheet_data.cursor.column

        if top_border:
            if self.oriented == ISpreadsheetSection.HIERARCHICAL:
                border_row = r_row
            else:
                border_row = c_row
        else:
            border_row = r_row-1

        return border_row
