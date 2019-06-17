from pyparsing import Word, Literal, ZeroOrMore, Forward, Keyword,\
    Combine, Group, Suppress, Optional, oneOf, srange, nums


class Tokenizer:
    def __init__(self):
        # Стек выражения
        self.stack = []
        # Вспомогательные массивы для формирования элементов
        self.axis = []
        self.coords = []
        # Вспомогательный массив для числа аргументов функций
        self.args = 0

    def push(self, toks):
        self.stack.append(toks[0])

    def push_arg(self):
        self.args += 1

    def push_func(self):
        # self.stack.append(self.args+1)
        self.args = 0

    def push_num(self, toks):
        # Проверка, целое или вещественное число
        #TODO: -30 is converted to float -30.0, fix this
        if toks[0].isalnum():
            self.stack.append(int(''.join(toks)))
        else:
            self.stack.append(float(''.join(toks)))

    def push_nat(self, toks):
        self.axis.append(int(toks[0]))

    def push_axis(self, toks):
        self.axis.append(''.join(toks))

    def push_coords(self):
        self.coords.append(self.axis)
        self.axis = []

    def push_element(self):
        self.stack.append(self.coords)
        self.coords = []

    def push_diap(self):
        self.axis.append('-')

    def create_tokenizer(self):
        alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'

        general_comp = oneOf('|<| |>| |=| |<>| |<=| |>=|')
        period_comp = oneOf('< > = <> <= >=')
        add = oneOf('+ -')
        multy = oneOf('* /')
        bool_in = Keyword('in')
        bool_and = Keyword('and')
        bool_or = Keyword('or')
        ter_symbol = Keyword('&np').setParseAction(self.push)
        sum_symbol = Keyword('sum')
        dash = Literal('-')
        comma = Suppress(',')
        lpar, rpar = map(Suppress, '()')
        lsqbr, rsqbr = map(Suppress, '[]')
        lcbr, rcbr = map(Suppress, '{}')
        any = Literal('*').setParseAction(self.push)

        # Логический предикат
        log_pred = bool_and | bool_or

        natural = Word(nums).setParseAction(self.push_nat)
        integer_s = (Optional('-') + Word(nums)).setParseAction(self.push_num)
        float = (Optional('-') + Combine(Word(nums) + '.' + Word(nums)))\
            .setParseAction(self.push_axis)
        float_s = float.copy().setParseAction(self.push_num)
        # Значение
        spec_val = Word(srange('[a-zA-Z]') + alphabet + alphabet.upper() + nums + '.')\
            .setParseAction(self.push_axis)
        # Код периода
        period_code = Word(nums).setParseAction(self.push)

        # Функции
        f_abs = Keyword('abs')
        f_coalesce = Keyword('coalesce')
        f_floor = Keyword('floor')
        f_isnull = Keyword('isnull')
        f_nullif = Keyword('nullif')
        f_round = Keyword('round')

        # Условие на период
        period_list = period_code + ZeroOrMore((comma + period_code))
        expr = ter_symbol + ((period_comp + period_code).setParseAction(self.push) |
                             (bool_in + Group(lpar + period_list + rpar))
                             .setParseAction(self.push))
        comp_expr = expr + ZeroOrMore((log_pred + expr).setParseAction(self.push))
        period_cond = Group(lpar + comp_expr + rpar)

        # Логическое выражение
        log_expr = Forward()

        diap = Group(natural + dash + natural)
        position = (diap.setParseAction(self.push_diap) ^ natural)
        position_list = position + ZeroOrMore(comma + position)
        position_descr = any.setParseAction(self.push_axis) | position_list
        # Графа
        entry = Group(lsqbr + position_descr + rsqbr).setParseAction(self.push_coords)
        # Строка
        row = Group(lsqbr + position_descr + rsqbr).setParseAction(self.push_coords)
        # Раздел
        section = Group(lsqbr + natural + rsqbr).setParseAction(self.push_coords)

        # Описание специфик
        diap_val = Group(spec_val + dash + spec_val)
        value = diap_val.setParseAction(self.push_diap) ^ spec_val
        # Список значений
        value_list = value + ZeroOrMore(comma + value)
        # Описание специфики
        spec_descr = any.setParseAction(self.push_axis) | value_list
        # Специфика
        spec = Group(lsqbr + spec_descr + rsqbr).setParseAction(self.push_coords)
        # Список специфик
        spec_list = spec + Optional(spec + Optional(spec))
        coords = (section + row + entry + Optional(spec_list))\
            .setParseAction(self.push_element)
        # За текущий период
        current_per = Group(lcbr + coords + rcbr)
        # За предыдущий период
        prev_per = Group(lcbr + lcbr + coords + rcbr + rcbr)
        element = (prev_per | current_per)

        arith_expr = Forward()
        # Функция
        func = Forward()

        # Область действия
        valid_area = element | func | Group(lpar + arith_expr + rpar)
        summa = (sum_symbol + valid_area).setParseAction(self.push)
        # Список параметров
        arg_list = arith_expr + ZeroOrMore((comma + arith_expr).setParseAction(self.push_arg))
        func <<= ((f_abs | f_coalesce | f_floor | f_isnull | f_nullif | f_round)
                  + Group(lpar + arg_list + rpar))\
            .setParseAction(self.push)\
            .addParseAction(self.push_func)
        # Множитель
        multiplic = (Group(lpar + arith_expr + rpar) |
                     ((float_s | integer_s) | element | summa | func))
        # Слагаемое
        term = multiplic + ZeroOrMore((multy + multiplic).setParseAction(self.push))
        arith_expr <<= term + ZeroOrMore((add + term).setParseAction(self.push))

        log_expr <<= period_cond | (arith_expr + (general_comp + arith_expr).setParseAction(self.push) +
                                    Optional((general_comp + arith_expr).setParseAction(self.push)))

        # Условие
        condition = log_expr + ZeroOrMore((log_pred + log_expr).setParseAction(self.push))

        return condition, log_expr, period_cond

    def tokenize_expression(self, expr, parser_type):
        self.stack = []
        parser_type.parseString(expr)

        return self.stack
