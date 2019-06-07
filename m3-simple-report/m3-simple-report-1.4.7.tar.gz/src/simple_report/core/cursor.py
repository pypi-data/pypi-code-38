# coding: utf-8
from __future__ import absolute_import

from abc import ABCMeta
from abc import abstractmethod

import six

from simple_report.interface import ISpreadsheetSection
from simple_report.utils import ColumnHelper


class AbstractCursor(six.with_metaclass(ABCMeta, object)):
    """
    Абстрактный курсор для табличных отчетов.
    """

    @abstractmethod
    def __init__(self):
        """
        """

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return "row: %s - col: %s" % (self._row, self._column)

    @property
    def row(self):
        """
         Строка
        :result: номер строки
        """
        return self._row

    @row.setter
    def row(self, value):
        self._test_value(value)
        self._row = value

    @property
    def column(self):
        return self._column

    @column.setter
    def column(self, value):
        self._test_value(value)
        self._column = value

    def _test_value(self, value):
        assert isinstance(value, tuple)
        assert len(value) == 2 # Только два элемента.

        # В потомках будет проверка для координаты столбца.

        assert isinstance(value[1], int) # Проверка координаты строки.

class AbstractCalculateNextCursor(six.with_metaclass(ABCMeta, object)):
    """
    Класс, который занимается работой по вычислению курсоров
    """


    def get_next_cursor(self, cursor, begin, end, oriented, section=None):
        """
        сursor - текущее положение курсора
        begin - начало секции
        end - конец секции
        oriented - ориентация вывода
        """

        assert isinstance(cursor, AbstractCursor)

        begin_column, begin_row = begin
        end_column, end_row = end

        # если это первый вывод
        if cursor.row == cursor.column:
            current_col, current_row = cursor.row
            # вычислим следующую строку
            cursor.row = (self.get_first_column(), current_row + end_row - begin_row + 1)
            cursor.column = (self.get_next_column(current_col, end_column, begin_column),
                             current_row)
        else:
            if oriented == ISpreadsheetSection.LEFT_DOWN:
                current_col, current_row = self.get_first_column(), cursor.row[1]
                # вычислим следующую строку
                cursor.row = (self.get_first_column(),
                              current_row + end_row - begin_row + 1)
                cursor.column = (self.get_next_column(current_col, end_column, begin_column),
                                 current_row)
            elif oriented == ISpreadsheetSection.HORIZONTAL:
                current_col, current_row = cursor.column
                cursor.column = (self.get_next_column(current_col, end_column, begin_column),
                                 current_row)
            elif oriented == ISpreadsheetSection.RIGHT_UP:
                current_col, current_row = cursor.column[0], self.get_first_row()
                cursor.row = (current_col, current_row + end_row - begin_row + 1)
                cursor.column = (self.get_next_column(current_col, end_column, begin_column),
                                 self.get_first_row())
            elif oriented == ISpreadsheetSection.RIGHT:
                current_col, current_row = cursor.column
                cursor.row = (current_col, current_row + end_row - begin_row + 1)
                cursor.column = (self.get_next_column(current_col, end_column, begin_column),
                                 current_row)
            elif oriented == ISpreadsheetSection.HIERARCHICAL:
                w = section.get_indent() - 1
                current_col, current_row = (self.calculate_indent(cursor.row[0], w), cursor.row[1])
                cursor.column = (self.get_next_column(current_col, end_column, begin_column), current_row)
                cursor.row = (current_col, current_row + (end_row - begin_row)+1)
            else:
                current_col, current_row = cursor.row
                cursor.column = (self.get_next_column(current_col, end_column, begin_column),
                                 current_row)
                cursor.row = (current_col, current_row + end_row - begin_row + 1)

        return current_col, current_row

    @abstractmethod
    def get_next_column(self, current_col, end_col, begin_col):
        """
         Вычисление следующей колонки
        :param current_col: текущая колонка
        :param end_col: конечная колонка
        :param begin_col: начальная колонка
        :result: следующая колонка
        """

    @abstractmethod
    def get_first_column(self):
        """
        Вычисление первой колонки
        """

    @abstractmethod
    def get_first_row(self):
        """
        Вычисление первой строки
        """

    @abstractmethod
    def calculate_indent(self, column, w):
        """
         Подсчет сдвига колонки
        :param column: колонка
        :param w: ширина сдвига
        :result: колонка после сдвига
        """
