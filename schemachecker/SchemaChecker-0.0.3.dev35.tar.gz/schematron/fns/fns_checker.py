import operator
import os
from threading import local
from functools import wraps
from lxml import etree
from pyparsing import Literal, Suppress, Forward, Word, \
    Group, ZeroOrMore, Optional, oneOf, nums, srange, Combine
from .exceptions import *

_root = os.path.dirname(os.path.abspath(__file__))


class SchemaChecker(local):
    def __init__(self, *, xsd_root=_root, xml_root=_root, verbose=False):
        # Символы, которые могут содержаться в элементе узла
        self._alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        self._nums = '1234567890'
        self._special_symbols = '@/:._-'
        self._element = set(self._alphabet + self._alphabet.upper() +
                            self._nums + self._special_symbols)

        self._nullary_map = {
            'usch:getFileName': self._usch_file_name
        }

        self._unary_map = {
            'not':      operator.not_,
            'count':    self._count_func,
            'round':    self._round_func,
            'sum':      self._sum_func,
            'number':   self._number_func
        }

        self._binary_map = {
            '<':                self._op_lt,
            '<=':               operator.le,
            '=':                operator.eq,
            '>':                operator.gt,
            '>=':               operator.ge,
            '!=':               operator.ne,
            '*':                self._op_mul,
            '-':                self._op_sub,
            '+':                self._op_add,
            'mod':              self._op_mod,
            'and':              operator.and_,
            'or':               operator.or_,
            'usch:compareDate': self._usch_compare_date
        }

        self._ternary_map = {
            'substring':    self._substring_func,
            'usch:iif':     self._usch_iif
        }

        self._varargs_map = {
            'concat':       self._concat_func
        }

        self._verbose = verbose

        self._local_data = local()

        self._local_data.stack = []
        self._local_data.expr = self._create_tokenizer()
        self._local_data.xsd_root = xsd_root
        self._local_data.xml_root = xml_root
        self._local_data.parser = etree \
            .XMLParser(encoding='cp1251', remove_comments=True)

        self._local_data.xml_file = None
        self._local_data.xml_content = None
        self._local_data.xsd_content = None
        self._local_data.xsd_schema = None
        self._local_data.context = None
        self._local_data.cache = dict()

        # Контейнер для хранения результатов обработки
        self._local_data.output = None

    def _cached_node(func):
        # Кэшируется только один элемент - узел
        @wraps(func)
        def _inner(*args, **kwargs):
            self = args[0]
            element = f'//{self._local_data.context}/{args[1]}'
            if element not in self._local_data.cache:
                self._local_data.cache[element] = func(*args, **kwargs)
            return self._local_data.cache[element]
        return _inner

    def _cached_func(func):
        @wraps(func)
        def _inner(*args, **kwargs):
            self = args[0]
            # Нужен контекст, могут быть идентичные сигнатуры
            # в разных контекстах
            element = f'{func.__name__}/{self._local_data.context}/{args[1:]}'
            if element not in self._local_data.cache:
                self._local_data.cache[element] = func(*args, **kwargs)
            return self._local_data.cache[element]
        return _inner

    def _return_error(self, text):
        return f'\u001b[31mError. {text}.\u001b[0m'

    def _get_error(self, node):
        error = {}
        replacing = []
        error['code'] = node.get('code')

        text = ''
        if node.text:
            text = node.text

        for child in node:
            select = child.get('select', None)
            replacing.append(select)
            text += select

            if child.tail is not None:
                # Конец текста ошибки перед закрывающим тегом
                text += child.tail

        # Убираем спецсимволы
        text = ' '.join((text.replace('\n', '').replace('\t', '')).split())
        error['text'] = text
        error['replacing'] = replacing

        return error

    def _get_error_text(self, assertion):
        error = assertion['error']
        error_text = error['text']
        for replacement in error['replacing']:
            error_text = error_text.replace(
                replacement, str(self._parse(replacement, assertion['context'])))
        return error_text

    def _get_asserts(self, content):
        assertions = content.findall('.//xs:appinfo', namespaces=content.nsmap)
        assert_list = []

        for assertion in assertions:
            for pattern in assertion:
                name = pattern.attrib.get('name', None)
                if not name:
                    continue

                for rule in pattern:
                    context = rule.attrib['context']

                    # Пропуск проверок, родительский элемент
                    # которых может не встречаться, minOccurs=0
                    occurs_elements = assertion.xpath(
                        f'ancestor::*[@minOccurs=0]')
                    if len(occurs_elements):
                        continue

                    # Проверка, присутствует ли контекст в xml файле
                    if len(self._local_data.xml_content.xpath(f'//{context}')) == 0:
                        # Не найден контекст в xml файле

                        # Пропуск опциональных проверок, choice
                        choice_elements = assertion.xpath(f'ancestor::xs:choice',
                                                          namespaces=content.nsmap)
                        if len(choice_elements):
                            # Опциональная проверка, пропускаем
                            continue
                        # Ошибка, проверка обязательна, контекст не найден
                        raise ContextError(context, self._local_data.xml_file)

                    for sch_assert in rule:
                        for error_node in sch_assert:
                            error = self._get_error(error_node)

                            assert_list.append({
                                'name':     name,
                                'assert':   sch_assert.attrib['test'],
                                'context':  context,
                                'error': error
                            })

        return assert_list

    def _push(self, toks):
        self._local_data.stack.append(toks[0])
        # print('=>', self._stack)

    def _push_not(self, toks):
        for tok in toks:
            if tok == 'not':
                self._local_data.stack.append(tok)
        # print('=>', self._stack)

    def _create_tokenizer(self):
        general_comp = oneOf('< > = != <= >=')
        bool_and = Literal('and')
        bool_or = Literal('or')
        bool_not = Literal('not')
        lpar, rpar = map(Suppress, '()')
        tick = Literal("'")
        minus = Literal('-')
        plus = Literal('+')
        mul = Literal('*')
        mod = Literal('mod')
        comma = Suppress(',')

        alphabet = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
        element = (Word(alphabet + alphabet.upper() + nums + '@/:._- ')
                   .setParseAction(self._push))
        integer = Word(nums).setParseAction(self._push)
        floats = (Combine(Word(nums) + '.' + Optional(Word(nums)))
                  .setParseAction(self._push))
        string = Word(alphabet + alphabet.upper() +
                      nums + srange('[a-zA-Z]' + '.'))
        quoted_string = Combine(tick + string + tick).setParseAction(self._push)
        date = Combine(tick + Word(nums, exact=2) + '.' +
                       Word(nums, exact=2) + '.' + Word(nums, exact=4) +
                       tick).setParseAction(self._push)

        expr = Forward()
        node = element + ZeroOrMore(((mul | minus) + element)
                                    .setParseAction(self._push))
        parenthesized_node = Group(lpar + node + rpar)
        node_or_parnode = node | parenthesized_node
        # Переменное (не менее двух) количество узлов, разделённых запятыми
        variadic_node = Group(node_or_parnode + comma + node_or_parnode +
                              ZeroOrMore(comma + node_or_parnode))
        parenthesized_expr = Group(lpar + expr + rpar)

        count_func = Literal('count') + parenthesized_node
        round_func = Literal('round') + parenthesized_node
        sum_func = Literal('sum') + parenthesized_node
        number_func = Literal('number') + parenthesized_expr
        substring_func = (Literal('substring') +
                          Group(lpar + node + comma + integer +
                                Optional(comma + integer) + rpar))
        concat_func = (Literal('concat') + Group(lpar + variadic_node + rpar))
        usch_filename = Literal('usch:getFileName') + Group(lpar + rpar)
        usch_iif = (Literal('usch:iif') +
                   Group(lpar + expr + comma + expr + comma + expr + rpar))
        usch_compare_date = (Literal('usch:compareDate') +
                             Group(lpar + node + comma + node + rpar))
        funcs = (count_func | round_func | sum_func | number_func |
                 substring_func | concat_func | usch_filename |
                 usch_iif | usch_compare_date).setParseAction(self._push)

        atom = (funcs | node | (Optional(bool_not) + parenthesized_expr)
                .setParseAction(self._push_not))
        left_expr = atom + ZeroOrMore(((mul | minus | plus | mod) + atom)
                                      .setParseAction(self._push))

        factor = (left_expr +
                  ZeroOrMore((general_comp +
                              (floats | integer | atom | quoted_string | date))
                             .setParseAction(self._push)))
        term = factor + ZeroOrMore((bool_and + factor)
                                   .setParseAction(self._push))
        expr <<= term + ZeroOrMore((bool_or + term).setParseAction(self._push))
        return expr

    @_cached_node
    def _evaluate_node(self, node):
        element = f'//{self._local_data.context}/{node}'
        value = self._local_data.xml_content.xpath(element)
        if '@' in node:
            # Работаем с атрибутом, возвращаем значение
            if not value:
                # Элемент/атрибут не найден
                raise NodeAttributeError(self._local_data.context,
                                         node, self._local_data.xml_file)
            value = value[0]
            return value
        else:
            # Работаем с элементом, возвращаем наличие
            return True if value else False

    def _evaluate_stack(self):
        op = self._local_data.stack.pop()

        if op in self._nullary_map:
            return self._nullary_map[op]()
        elif op in self._unary_map:
            if op == 'count':
                arg = self._local_data.stack.pop()
            else:
                arg = self._evaluate_stack()
            return self._unary_map[op](arg)
        elif op in self._binary_map:
            arg2 = self._evaluate_stack()
            arg1 = self._evaluate_stack()
            return self._binary_map[op](arg1, arg2)
        elif op in self._ternary_map:
            arg3 = self._evaluate_stack()
            arg2 = self._evaluate_stack()
            if op == 'substring' and not arg2.isdigit():
                # Получили substring без опционального третьего аргумента
                return self._ternary_map[op](arg2, arg3)
            arg1 = self._evaluate_stack()
            return self._ternary_map[op](arg1, arg2, arg3)
        elif op in self._varargs_map:
            args = []
            # Смотрим на вершину стека, если он не пуст
            if len(self._local_data.stack):
                arg = self._local_data.stack[-1]
                while set(arg) <= self._element:
                    # Если элемент узла - можно вычислять значение
                    arg = self._evaluate_stack()
                    args.append(arg)
                    arg = self._local_data.stack[-1]
            # Разворачиваем аргументы, приходят из стека в обратном порядке
            return self._varargs_map[op](*args[::-1])
        elif op.isdigit():
            # Возвращаем найденное число
            return op
        elif op.startswith('\''):
            # Возвращаем строку без кавычек
            return op[1:-1]
        else:
            node = self._evaluate_node(op)
            return node

    def _parse(self, expression, context):
        # print(expression)
        self._local_data.context = context
        try:
            self.tokenize(expression)
        except Exception as ex:
            raise TokenizerError(expression, self._local_data.xml_file, ex)
        try:
            parsing_result = self._evaluate_stack()
            return parsing_result
        except Exception as ex:
            raise ParserError(expression, self._local_data.xml_file, ex)

    # Функции

    # Обёртки для некоторых арифметических операций
    def _float_converter(func):
        @wraps(func)
        def _inner(*args, **kwargs):
            inner_args = [*args]
            try:
                inner_args[1:] = map(float, args[1:])
            except ValueError as ex:
                raise TypeConvError(inner_args[1:], ex)
            return func(*inner_args, **kwargs)
        return _inner

    def _op_lt(self, a, b):
        return str(a) < str(b)

    @_float_converter
    def _op_mul(self, a, b):
        val = a * b
        return val

    @_float_converter
    def _op_sub(self, a, b):
        val = a - b
        return val

    @_float_converter
    def _op_add(self, a, b):
        val = a + b
        return val

    @_float_converter
    def _op_mod(self, a, b):
        val = a % b
        return val

    @_cached_func
    def _count_func(self, node):
        return str(len(self._local_data.xml_content
                       .xpath(f'//{self._local_data.context}/{node}')))

    @_cached_func
    def _round_func(self, node):
        return round(node)

    @_cached_func
    def _sum_func(self, node):
        return node

    @_cached_func
    def _number_func(self, node):
        return node

    @_cached_func
    def _substring_func(self, node, start, length='0'):
        start, length = int(start) - 1, int(length)
        return node[start:start + int(length)] if length else node[start:]

    def _concat_func(self, *args):
        return ''.join(args)

    def _usch_file_name(self):
        return '.'.join(self._local_data.xml_file.split('.')[:-1])

    def _usch_iif(self, cond, true, false):
        return true if cond else false

    def _usch_compare_date(self, first_node, second_node):
        return (first_node == second_node)

    # Публичное API

    def tokenize(self, text):
        self._local_data.stack = []
        return self._local_data.expr.parseString(text).asList()

    def check_file(self, input):
        # Очищаем кэш
        self._local_data.cache = dict()

        self._local_data.xml_file = input.filename
        self._local_data.xml_content = input.xml_obj
        self._local_data.xsd_content = input.xsd_schema
        self._local_data.xsd_scheme = etree.XMLSchema(self._local_data.xsd_content)

        input.verify_result = dict()

        input.verify_result['result'] = 'passed'
        input.verify_result['xsd_asserts'] = []
        input.verify_result['sch_asserts'] = []

        # if not self._local_data.result.get('xsd_scheme'):
        #     return self._local_data.result
        #
        # with open(self._local_data.result['file'], 'rb') as xml_file_handler:
        #     self._local_data.xml_content = etree.fromstring(xml_file_handler.read())
        #
        # self._local_data.result['file'] = os.path.basename(self._local_data.result['file'])
        #
        # with open(os.path.join(self._local_data.xsd_root, self._local_data.result['xsd_scheme']),
        #           'r', encoding='cp1251') as xsd_file_handler:
        #     xsd_content = etree.parse(xsd_file_handler, self._local_data.parser).getroot()
        #     xsd_schema = etree.XMLSchema(xsd_content)
        #
        # self._local_data.xsd_content = xsd_content
        # self._local_data.xsd_schema = xsd_schema
        # self._local_data.xml_file = self._local_data.result['file']

        # Проверка по xsd
        try:
            self._local_data.xsd_scheme.assertValid(self._local_data.xml_content)
        except etree.DocumentInvalid as ex:
            if self._verbose:
                print('_' * 80)
                print('FILE:', self._local_data.xml_file)
                print(self._return_error(f'Ошибка при валидации по xsd схеме '
                                         f'файла {self._local_data.xml_file}.'))

            for error in self._local_data.xsd_scheme.error_log:
                input.verify_result['xsd_asserts']\
                    .append(f'{error.message} (строка {error.line})')

            input.verify_result['result'] = 'failed_xsd'
            input.verify_result['description'] = (
                f'Ошибка при валидации по xsd схеме файла '
                f'{self._local_data.xml_file}: {ex}.')
            return

        # Проверка выражений fns
        try:
            asserts = self._get_asserts(self._local_data.xsd_content)
        except Exception as ex:
            if self._verbose:
                self._return_error(ex)
            input.verify_result['result'] = 'failed_sch'
            input.verify_result['description'] = self._return_error(ex)
            return

        # Нет выражений для проверки
        if not asserts:
            return

        for assertion in asserts:
            try:
                assertion_result = self._parse(assertion['assert'],
                                               assertion['context'])
                if not assertion_result:
                    input.verify_result['sch_asserts'] \
                        .append((assertion['name'],
                                 assertion['error']['code'],
                                 self._get_error_text(assertion)))
            except ParserError:
                pass
            except Exception as ex:
                if self._verbose:
                    print('_' * 80)
                    print('FILE:', self._local_data.xml_file)
                    self._return_error(ex)
                input.verify_result['result'] = 'failed_sch'
                input.verify_result['description'] = ex
                return

        if input.verify_result['sch_asserts']:
            if self._verbose:
                print('_' * 80)
                print('FILE:', self._local_data.xml_file)
                for name, errcode, errtext in input.verify_result['sch_asserts']:
                    print(f'{name}: \u001b[31m{errtext} ({errcode})\u001b[0m')
                print('\u001b[31mTest failed\u001b[0m')
            input.verify_result['result'] = 'failed_sch'
            input.verify_result['description'] = 'Ошибки при проверке fns'

        return
