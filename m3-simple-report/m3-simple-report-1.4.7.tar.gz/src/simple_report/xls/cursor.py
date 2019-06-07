# coding: utf-8
from __future__ import absolute_import

from simple_report.core.cursor import AbstractCalculateNextCursor
from simple_report.core.cursor import AbstractCursor


class CursorXLS(AbstractCursor):
    """
    Специализированный курсор для XLS таблиц
    """

    def __init__(self, column=None, row=None):
        super(CursorXLS, self).__init__()

        self.column = column or (0, 0)
        self.row = row or (0, 0)

    def _test_value(self, value):
        super(CursorXLS, self)._test_value(value)

        # Координаты в XLS таблицах имеют вид
        # (3, 0). 3 - Номер столбца. Нумерация с нуля
        #         0 - Номер строки. Нумерация с нуля.
        assert isinstance(value[0], int)

class CalculateNextCursorXLS(AbstractCalculateNextCursor):
    """
    Получение следующего курсора
    """

    def get_next_column(self, current_column, end_col, begin_col):
        """
         Получение следующей колонки
        :param current_column: текущая колонка
        :param end_col: конечная колонка
        :param begin_col: начальная колонка
        :result: следующая колонка
        """

        return current_column + end_col - begin_col + 1

    def get_first_column(self):
        """
         Получение первой колонки
        :result: номер первой колонки
        """
        # Колонки нумеруются и номер первой нуль.
        return 0

    def get_first_row(self):
        """
         Получение первой строки
        :result: номер первой строки
        """
        return 0

    def calculate_indent(self, column, w):
        """
         Вычисление сдвига
        :param column: колонка
        :param w: ширина сдвига
        :result: разница между номером колонки и шириной сдвига
        """

        return column - w
