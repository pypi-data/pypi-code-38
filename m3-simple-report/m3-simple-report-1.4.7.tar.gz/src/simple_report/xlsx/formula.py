# coding: utf-8
from __future__ import absolute_import

import re

from simple_report.utils import ColumnHelper


# TODO: кажется, нигде не используется

class Formula(object):
    u"""
    Изменение формулы для последующего вывода
    """

    # Регулярка для поиска индекса колонки (набор латинских букв в верхнем регистре длины >= 1).
    col_ind = '[A-Z]+'
    # Регулярка для поиска индекса строки (набор цифр длины >= 1. Первая цифра не нуль).
    row_ind = '[1-9][0-9]*'
    # Регулярка для поиска адреса ячейки.
    cell_coord = '[$]?'.join(['', col_ind, row_ind])

    col_re = re.compile(col_ind)
    row_re = re.compile(row_ind)
    # Так выглядит адрес ячейки в электронной таблице
    cell_coordinates_re = re.compile(cell_coord)

    # Кэш формул.
    _cache = {}

    @classmethod
    def get_instance(cls, formula):
        """
        Получение формулы
        :param formula:
        :type formula:
        """
        return Formula._cache.get(formula) or Formula(formula)

    def __init__(self, formula):
        self.formula = formula
        # Флаг того, что формула вычисляется впервые. В этом случае изменять её,
        # нет необходимости
        self.first = True

        self._last_row = 0
        self._last_column = 'A'

        if formula not in Formula._cache:
            Formula._cache[formula] = self

    def _get_cell_coord(self):
        """
        Возвращает индексы начала и конца подстроки с адресом ячейки
        """

        iterator = self.cell_coordinates_re.finditer(self.formula)

        for i in iterator:
            yield i.start(), i.end()

    def _change_analyze(self, cell_coord):
        """
        Смотрит на адрес ячейки и в зависимости от наличия (отсутствия)
        символа $ сообщает, что колонку можно менять (или нет)
        Например: $A11 -> (false, true), A$12 -> (true, false)
        """

        column = re.compile('[$]?[A-Z]+')
        row = re.compile('[$]?[1-9][0-9]*')

        change_column = change_row = True

        # Проверяем, первый символ это $? Если да, то менять ничего нельзя.
        if column.search(cell_coord).group()[0] == '$':
            change_column = False
        if row.search(cell_coord).group()[0] == '$':
            change_row = False

        return change_column, change_row

    def _get_next_index(self, cell_coord, may_change, diff, is_column):
        """
        Изменяем индекс у столбца(строки) ячейки(в зависимости от флага is_column)
        may_change - можно ли индекс изменять
        diff - на сколько нужно изменить индекс
        """

        reg_exp = self.col_re if is_column else self.row_re

        index = reg_exp.search(cell_coord).group()

        if may_change:
            if is_column:
                index = ColumnHelper.add(index, diff)
            else:
                index = str(int(index) + diff)
        else:
            index = ''.join(['$', index])

        return index

    def get_next_formula(self, row, column):
        """
        Изменяем формулу и отдаём
        """

        diff_row = row - self._last_row
        self._last_row = row

        diff_column = ColumnHelper.difference(column, self._last_column)
        self._last_column = column

        if not self.first:

            formula = self.formula

            for start, end in self._get_cell_coord():
                # Подстрока с адресом ячейки
                cell_coord = self.formula[start:end]

                change_column, change_row = self._change_analyze(cell_coord)

                column_index = self._get_next_index(cell_coord, change_column, diff_column,
                                                    is_column=True)
                row_index = self._get_next_index(cell_coord, change_row, diff_row,
                                                 is_column=False)
                # Сцепляем индекс колонки и индекс ячейки
                new_cell_coord = ''.join([column_index, row_index])

                # Заменяем подстроку в формуле
                formula = formula.replace(cell_coord, new_cell_coord)

            self.formula = formula
        else:
            self.first = False

        return self.formula
