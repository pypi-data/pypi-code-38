import operator
import numpy as np
from pprint import pformat
from .utils import Dict


class DataFrame:
    """
    Класс датафрейма для хранения и обработки таблиц из xml документов
    """
    op_map = {
        '+': operator.add,
        '-': operator.sub,
        '*': operator.mul,
        '/': operator.truediv,
        '<': operator.lt,
        '<=': operator.le,
        '=': operator.eq,
        '>': operator.gt,
        '>=': operator.ge,
        '!=': operator.ne,
    }

    def __init__(self, *, struct=None, data=None):
        """
        Структура датафрейма:
        {
            '06':   {'201': {'s1': None, 's2': 'X', 's3': None, 1: 10, 2: 20},
                    {'301': {'s1': None, 's2': 'X', 's3': None, 1: 15, 2: 23},
                    ...}
            '07':   {'01':  {'s1': 'Y', 's2': None, 's3': None, 1: 13, 2: 24},
                    ...}
        }
        """
        # Выборочная структура, только данные
        if struct is None:
            struct = Dict()
            struct['rows'] = Dict()
            struct['cols'] = Dict()
            struct['specs'] = list()
            struct['d_rows'] = list()
            struct['d_cols'] = list()
            struct['d_specs'] = list()
            struct['data'] = data

        # Структура для отображения
        self.struct = struct
        # Метаданные
        self.rows = struct['rows']
        self.cols = struct['cols']
        self.d_rows = struct['d_rows']
        self.d_cols = struct['d_cols']
        self.d_specs = struct['d_specs']
        # Табличные данные
        self.specs = struct['specs']
        self.data = np.array(struct['data'], dtype=np.float)

    def __str__(self):
        return pformat(self.struct)

    def __add__(self, other):
        return self._op(other, '+')

    def __sub__(self, other):
        return self._op(other, '-')

    def __mul__(self, other):
        return self._op(other, '*')

    def __truediv__(self, other):
        return self._op(other, '/')

    def __gt__(self, other):
        return self._boolop(other, '>')

    def __ge__(self, other):
        return self._boolop(other, '>=')

    def __lt__(self, other):
        return self._boolop(other, '<')

    def __le__(self, other):
        return self._boolop(other, '<=')

    def __eq__(self, other):
        return self._boolop(other, '=')

    def __ne__(self, other):
        return self._boolop(other, '!=')

    def _op(self, other, op):
        """
        Вспомогательный метод для перегрузки операторов
        """
        if type(other) == DataFrame:
            data = DataFrame.op_map[op](self.data, other.data)
        else:
            data = DataFrame.op_map[op](self.data, other)
        return DataFrame(data=data)

    def _boolop(self, other, op):
        """
        Вспомогательный метод для перегрузки булевых операций
        """
        if type(other) == DataFrame:
            #TODO: fix a strange warning about "invalid value encountered"
            nonan_mask = DataFrame.op_map[op](self.data, other.data)
            nan_mask = np.isnan(self.data) | np.isnan(other.data)
            return (nonan_mask | nan_mask).all()
        else:
            nonan_mask = DataFrame.op_map[op](self.data, other)
            nan_mask = np.isnan(self.data)
            return (nonan_mask | nan_mask).all()

    @staticmethod
    def from_file_content(xml_section, scheme_section):
        """
        Инициализирует базовый датафрейм (из которого будут делаться выборки)
        по содержимому файла xml_section и секции в шаблоне scheme_section
        с описанием формата.
        Все методы применяются к "выборочному" датафрейму, но НЕ к базовому.
        При работе с выборочным датафреймом используются только данные поля "data"
        """
        #TODO: check wtf takes so long to parse
        # Копируем шаблон датафрейма
        df_struct = scheme_section.df_struct.copy()

        # Отображение колонок-специфик на индексы
        spec_map = {'s1': 0, 's2': 1, 's3': 2}

        # Число колонок
        ncols = len(df_struct['cols'])

        # Заполнение массивов 'data' и 'specs'
        rows = xml_section.xpath('.//row')
        for rx, row in enumerate(rows):
            _row = int(row.attrib['code'])
            df_struct['rows'][_row].append(rx)

            # Заполняем специфики, если есть
            df_struct['specs'].append([None for _ in range(3)])
            for attrib, value in row.attrib.items():
                if attrib != 'code':
                    sx = spec_map[attrib]
                    df_struct['specs'][rx][sx] = value.lower()
                    df_struct['d_specs'][sx].add(value.lower())

            df_struct['data'].append([None for _ in range(ncols)])

            cols = row.xpath('.//col')
            for col in cols:
                _col = int(col.attrib['code'])
                cx = df_struct['cols'][_col]
                # Значение не заполнено, используем значение по умолчанию или 0
                if col.text:
                    value = float(col.text)
                else:
                    value = scheme_section['columns'][str(_col)].get('default')
                    value = float(value) if value else 0
                df_struct['data'][rx][cx] = value

        df_struct['d_specs'] = [sorted(list(spec))
                                for spec in df_struct['d_specs']]

        # Создание объекта датафрейма
        return DataFrame(struct=df_struct)

    def dim(self):
        # Определяет размерность датафрейма
        return self.data.shape

    def get(self, rows, cols, *spec):
        #TODO: fillout the docstring
        #TODO: take parsing logic for rows/cols/specs out to compendium?
        """
        Делает выборку из датафрейма по заданным
        спискам строк и граф.
        Возвращает новый объект DataFrame (выборочный датафрейм) или скаляр,
        если рамерность - 1*1
        """
        data = list()

        # Выбираем строки
        _rows = list()
        while rows:
            rel = rows.pop()
            # Все строки
            if rel == '*':
                _rows = [row for row in self.d_rows]
            # Просто номер строки
            elif type(rel) == int:
                _rows.append(rel)
            # Диапазон строк
            elif rel == '-':
                max_r = rows.pop()
                min_r = rows.pop()
                max_r_idx = self.d_rows.index(max_r)
                min_r_idx = self.d_rows.index(min_r)
                _rows.extend(self.d_rows[min_r_idx: max_r_idx])

        # Выбираем графы (колонки)
        _cols = list()
        while cols:
            cel = cols.pop()
            # Все графы
            if cel == '*':
                _cols = [col for col in self.d_cols]
            # Номер графы
            elif type(cel) == int:
                _cols.append(cel)
            # Диапазон граф
            elif cel == '-':
                max_c = cols.pop()
                min_c = cols.pop()
                max_c_idx = self.d_cols.index(max_c)
                min_c_idx = self.d_cols.index(min_c)
                _cols.extend(self.d_cols[min_c_idx: max_c_idx])

        # Индексы строк
        rxs = sorted([idx for row in _rows for idx in self.rows[row]])
        # Индексы колонок
        cxs = sorted([self.cols[col] for col in _cols])

        # Работаем со спецификами
        # Получаем списки специфик по каждой оси
        #TODO: clear up this mess
        spec_list = ['plug', 'plug', 'plug']
        if any(spec):
            for spx, sp in enumerate(spec):
                spec_list[spx] = set()
                while sp:
                    spel = sp.pop()
                    # Выбираем все строки без фильтра
                    if spel == '*':
                        spec_list[spx] = self.d_specs[spx]
                    # Значение специфики
                    elif spel != '-':
                        # Специфика из проверки не найдена, пропускаем
                        if spel not in self.d_specs[spx]:
                            continue
                        spec_list[spx].add(spel)
                    # Диапазон специфик
                    else:
                        max_s = sp.pop()
                        min_s = sp.pop()
                        if (min_s not in self.d_specs[spx]
                                or max_s not in self.d_specs[spx]):
                            continue
                        max_s_idx = self.d_specs[spx].index(max_s)
                        min_s_idx = self.d_specs[spx].index(min_s)
                        spec_list[spx].update(self.d_specs[spx]
                                              [min_s_idx: max_s_idx])

            # Строки содержат специфики
            if all(spec_list):
                # Индексы непустых массивов специфик
                spec_idxs = [idx for idx, spec in enumerate(spec_list) if spec != 'plug']
                for rx in rxs:
                    flag = True
                    for spx in spec_idxs:
                        if self.specs[rx][spx] not in spec_list[spx]:
                            flag = False
                            break
                    # У строки подходящие специфики, добавляем в выборку
                    if flag:
                        data.append([self.data[rx][cx] for cx in cxs])

        # Специфик нет, просто добавляем строки
        else:
            for rx in rxs:
                data.append([self.data[rx][cx] for cx in cxs])

        frame = DataFrame(data=data)
        # if frame.dim() == (1, 1):
        #     return frame.data[0][0]
        # Пустая выборка
        if frame.data.size == 0:
            return DataFrame(data=[[0]])
        return frame

    def fill_none(self, *, filler=0):
        """
        Заменяет все отсутствующие (None) элементы таблицы section
        на filler
        """
        data = np.nan_to_num(self.data)
        return DataFrame(data=data)

    def is_none(self):
        """
        Определяет, содержатся ли незаполненные (None) элементы
        в датафрейме
        """
        return np.isnan(self.data).all()

    def sum(self, *, axis=0):
        """
        Выполняет сложение элементов таблицы section
        вдоль оси axis:
            0 - по столбцам,
            1 - по строкам,
            2 - во всей таблице
        Возвращает объект DataFrame, если сложение производится по строкам/столбцам,
        или скаляр, если сложение производится по всему датафрейму
        """
        if axis == 2:
            return np.nansum(self.data)

        data = np.nansum(self.data, axis=axis, keepdims=True)
        return DataFrame(data=data)

    def abs(self):
        """
        Возвращает новый датафрейм с абсолютными значениями элементов
        """
        data = np.abs(self.data)
        return DataFrame(data=data)

    def round(self, precision, op_type=0):
        """
        Возвращает новый датафрейм со значениями элементов,
        округлённых до указанной длины и точности
        precision - точность округления;
        op_type - тип операции
        """
        #TODO: alter behaviour according to the document
        #TODO: Use map()
        data = self.data.copy()
        dim = self.dim()

        for rx in range(dim[0]):
            for cx in range(dim[1]):
                if self.data[rx][cx]:
                    data[rx][cx] = round(self.data[rx][cx], precision)
        return DataFrame(data=data)

    def floor(self):
        """
        Возвращает наибольшее число, меньшее или равное
        наименьшему элементу в датафрейме
        """
        return np.nanmin(self.data)
