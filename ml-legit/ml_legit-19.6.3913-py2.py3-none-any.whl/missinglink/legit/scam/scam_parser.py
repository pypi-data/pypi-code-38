# -*- coding: utf-8 -*-
import re
import json
import six
from .luqum.tree import OrOperation, Word, Item, Phrase, SearchField, UnknownOperation
from .luqum.utils import LuceneTreeVisitorV2, UnknownOperationResolver, LuceneTreeTransformer
from .luqum.parser import parser, lexer, ParseError
import pyparsing as pp


class ParseApplicationException(ParseError):
    pass


def process_vals(t, l):
    res = []
    for val in t:
        res.append(l(val))

    return res


def convert_boolean(t):
    def bools(val):
        if val.lower() in ['true', 'yes']:
            return True

        return False

    return process_vals(t, bools)


def parse_expr(expr_text):
    operator = pp.Regex(">=|<=|!=|>|<|=")('operator')

    TRUE = pp.Keyword('True', caseless=True) | pp.Keyword('Yes', caseless=True)
    FALSE = pp.Keyword('False', caseless=True) | pp.Keyword('No', caseless=True)

    boolean = (TRUE | FALSE)('boolean')
    boolean.setParseAction(convert_boolean)
    float_number = (pp.pyparsing_common.sci_real | pp.pyparsing_common.real)
    int_number = (pp.pyparsing_common.integer | pp.pyparsing_common.signed_integer)
    identifier = ~float_number + pp.Word(pp.alphanums + "_" + "." + "-" + "*" + '?' + '/' + '\\')

    quoted_string = pp.QuotedString('"', endQuoteChar='"', unquoteResults=False)
    text_identifier = (quoted_string | identifier)
    comparison_term = boolean ^ float_number ^ int_number ^ text_identifier
    values = pp.OneOrMore(comparison_term)('values')
    range_op = pp.Suppress(pp.CaselessLiteral('TO'))
    range_operator = (pp.Suppress('[') + comparison_term + range_op + comparison_term + pp.Suppress(']'))('range')
    range_inclusive = (pp.Suppress('{') + comparison_term + range_op + comparison_term + pp.Suppress('}'))('range_inclusive')

    condition_group = (range_inclusive | range_operator | values | (operator + values))('condition_group')
    conditions = pp.Group(condition_group)('conditions')

    expr = pp.infixNotation(conditions, [
        ("AND", 2, pp.opAssoc.LEFT, ),
        ("OR", 2, pp.opAssoc.LEFT, ),
    ])

    return expr.parseString(expr_text, parseAll=True)


def _wrap_in_parentheses(text):
    return '(%s)' % text


def quotes_if_needed(val):
    return '"%s"' % val if isinstance(val, six.string_types) and not val.startswith('"') else val


def unquotes_if_needed(val):
    if val.startswith('"'):
        val = val[1:]

    if val.endswith('"'):
        val = val[:-1]

    return val


class QueryFunction(Item):
    def __init__(self, name, node):
        self.name = name
        self.node = node

    def __str__(self):
        return str(self.node)

    @classmethod
    def create_with_args(cls, vals):
        name = cls.__name__.replace('Function', '').lower()
        node = SearchField('@' + name, vals)
        return cls(name, node)


class FunctionVersion(QueryFunction):

    _equality_attrs = ['version']

    def __init__(self, name, node):
        super(FunctionVersion, self).__init__(name, node)
        self.version = str(node.expr)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.version)


class FunctionPhase(QueryFunction):

    _equality_attrs = ['phase']

    def __init__(self, name, node):
        super(FunctionPhase, self).__init__(name, node)
        self.phase = str(node.expr)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.phase)


class FunctionSplit(QueryFunction):

    _equality_attrs = ['split', 'split_field']

    def __init__(self, name, node):
        super(FunctionSplit, self).__init__(name, node)

        self.split_field = None
        self.split = {}

        split_vars = self.__validate_split_params(node)

        try:
            split_vars = list(map(float, split_vars))
            split_vars += [None] * (3 - len(split_vars))

            self.split = dict(zip(('train', 'test', 'validation'), split_vars))
        except ValueError:
            if len(split_vars) == 1:
                self.split_field = split_vars[0]
            else:
                raise ParseApplicationException('invalid values in @split')

    @classmethod
    def __validate_split_params(cls, node):
        split_vars = str(node)
        split_vars = split_vars.split(':')

        if len(split_vars) > 4:
            raise ParseApplicationException('too many values in @split')

        if len(split_vars) == 1:
            raise ParseApplicationException('@split needs at least one value')

        return split_vars[1:]


class FunctionSample(QueryFunction):

    _equality_attrs = ['sample']

    def __init__(self, name, node):
        super(FunctionSample, self).__init__(name, node)
        self.sample = float(node.expr.value)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.sample)


class FunctionSeed(QueryFunction):

    _equality_attrs = ['seed']

    def __init__(self, name, node):
        super(FunctionSeed, self).__init__(name, node)
        self.seed = int(str(node.expr))

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.seed)


class FunctionGroupBy(QueryFunction):

    _equality_attrs = ['group']

    def __init__(self, name, node):
        super(FunctionGroupBy, self).__init__(name, node)
        self.group = str(node.expr)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.group)


class FunctionDatapointBy(QueryFunction):

    _equality_attrs = ['datapoint']

    def __init__(self, name, node):
        super(FunctionDatapointBy, self).__init__(name, node)
        self.datapoint = str(node.expr)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.datapoint)


FunctionGroup = FunctionGroupBy


class FunctionLimit(QueryFunction):

    _equality_attrs = ['limit']

    def __init__(self, name, node):
        super(FunctionLimit, self).__init__(name, node)
        self.limit = int(str(node.expr))

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.limit)


class FunctionOffset(QueryFunction):

    _equality_attrs = ['offset']

    def __init__(self, name, node):
        super(FunctionOffset, self).__init__(name, node)
        self.offset = int(str(node.expr))

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.offset)


class FunctionPath(QueryFunction):

    _equality_attrs = ['expr']

    def __init__(self, name, node):
        super(FunctionPath, self).__init__(name, node)
        self.expr = str(node.expr)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.expr.__repr__())


class FunctionSize(QueryFunction):

    _equality_attrs = ['expr']

    def __init__(self, name, node):
        super(FunctionSize, self).__init__(name, node)
        self.expr = str(node.expr)

    def __repr__(self):
        return "%s(%r, %s)" % (self.__class__.__name__, self.name, self.expr.__repr__())


class MLQueryMixin(object):
    @classmethod
    def _handle_internal_function(cls, node):
        if node.name.startswith('@'):
            func_name = node.name[1:]
            func_class_name = 'Function%s' % func_name.title()
            func_class_name = func_class_name.replace('_', '')
            function_class = globals().get(func_class_name)

            if function_class is None:
                raise ParseApplicationException('invalid function %s' % func_name)

            return function_class(func_name, node)

        return None


# noinspection PyClassicStyleClass
class MLQueryTransformer(LuceneTreeTransformer, MLQueryMixin):
    # noinspection PyUnusedLocal
    def visit_search_field(self, node, parents):
        return self._handle_internal_function(node) or node

    def __call__(self, tree):
        return self.visit(tree)


class MLQueryVisitor(LuceneTreeVisitorV2):
    def __visit_binary_operation(self, node, parents, context, op):
        new_context = {}
        if context is not None:
            new_context.update(context)

        new_context['op'] = op

        self.generic_visit(node, parents, new_context)

    def generic_visit(self, node, parents=None, context=None):
        for child in node.children:
            self.visit(child, parents, context=context)

    def visit_and_operation(self, node, parents=None, context=None):
        self.__visit_binary_operation(node, parents, context, 'AND')

    def visit_or_operation(self, node, parents=None, context=None):
        self.__visit_binary_operation(node, parents, context, 'OR')


# noinspection PyClassicStyleClass
class VersionVisitor(MLQueryVisitor):
    def __init__(self):
        self.version = None

    # noinspection PyUnusedLocal
    def visit_function_version(self, node, parents=None, context=None):
        self.version = node.version


# noinspection PyClassicStyleClass
class SplitVisitor(MLQueryVisitor):
    def __init__(self):
        self.__split = {'train': 1.0}
        self.__split_field = None
        self.__has_split = False

    def has_phase(self, phase):
        return self.__split.get(phase) is not None

    # noinspection PyUnusedLocal
    def visit_function_split(self, node, parents, context):
        self.__split = node.split
        self.__split_field = node.split_field
        self.__has_split = True

    def get(self, phase):
        return self.__split.get(phase)

    @property
    def has_split(self):
        return self.__has_split


# noinspection PyClassicStyleClass
class LimitVisitor(MLQueryVisitor):
    def __init__(self):
        self.limit = None

    # noinspection PyUnusedLocal
    def visit_function_limit(self, node, parents=None, context=None):
        self.limit = node.limit


# noinspection PyClassicStyleClass
class SeedVisitor(MLQueryVisitor):
    def __init__(self):
        self.__seed = 1337

    @property
    def seed(self):
        return self.__seed

    # noinspection PyUnusedLocal
    def visit_function_seed(self, node, parents, context):
        self.__seed = node.seed


# noinspection PyClassicStyleClass
class DatapointVisitor(MLQueryVisitor):
    def __init__(self):
        self.datapoint = None

    # noinspection PyUnusedLocal
    def visit_function_datapoint_by(self, node, parents, context):
        self.datapoint = node.datapoint


# noinspection PyClassicStyleClass
class SQLQueryBuilder(MLQueryVisitor, MLQueryMixin):
    phase_where_level = -1
    random_function_level = -1

    def __init__(self, sql_helper):
        self.__where = {}
        self.__vars = {}
        self.__sql_helper = sql_helper
        self.__visit_state = dict(
            has_complex_data=False,
            has_group_by=False,
            has_sample=False
        )

    internal_function_names = ['sample', 'seed', 'group', 'group_by', 'datapoint_by', 'offset', 'version', 'limit', 'path', 'size']

    @property
    def has_complex_data(self):
        return self.__visit_state.get('has_complex_data', False)

    @has_complex_data.setter
    def has_complex_data(self, _has_complex_data):
        self.__visit_state['has_complex_data'] = _has_complex_data

    @property
    def has_group_by(self):
        return self.__visit_state.get('has_group_by', False)

    @has_group_by.setter
    def has_group_by(self, _has_group_by):
        self.__visit_state['has_group_by'] = _has_group_by

    @property
    def has_sample(self):
        return self.__visit_state.get('has_sample', False)

    @has_sample.setter
    def has_sample(self, _has_sample):
        self.__visit_state['has_sample'] = _has_sample

    # noinspection PyUnusedLocal
    def visit_function_sample(self, node, parents=None, context=None):
        sample_percentile = 1.0 - node.sample

        self.__where.setdefault(self.random_function_level, []).append(
            ('AND', '($random_function>{sample_percentile:.4g})'.format(sample_percentile=sample_percentile)))

        self.__vars['sample_percentile'] = sample_percentile
        self.__vars['sample'] = node.sample
        self.has_sample = True

    # noinspection PyUnusedLocal
    def visit_function_path(self, node, parents=None, context=None):
        context = context or {}
        self.__add_where('_sha', node.expr, context.get('op'))

    # noinspection PyUnusedLocal
    def visit_function_size(self, node, parents=None, context=None):
        context = context or {}
        self.__add_where('_size', node.expr, context.get('op'))

    # noinspection PyUnusedLocal
    def visit_function_seed(self, node, parents=None, context=None):
        self.__vars['seed'] = node.seed

    # noinspection PyUnusedLocal
    def visit_function_limit(self, node, parents=None, context=None):
        self.__vars['limit'] = node.limit

    # noinspection PyUnusedLocal
    def visit_function_offset(self, node, parents=None, context=None):
        self.__vars['offset'] = node.offset

    def visit_function_group(self, node, parents=None, context=None):
        self.visit_function_group_by(node, parents, context)

    # noinspection PyUnusedLocal
    def visit_function_group_by(self, node, parents=None, context=None):
        self.__vars['group'] = node.group
        self.has_group_by = True

    # noinspection PyUnusedLocal
    def visit_function_datapoint_by(self, node, parents=None, context=None):
        self.__vars['datapoint'] = node.datapoint

    # noinspection PyUnusedLocal
    def visit_function_split(self, node, parents=None, context=None):
        if node.split_field is not None:
            self.__vars['split_field'] = node.split_field
        else:
            self.__vars.update(get_split_vars(node.split))

    # noinspection PyUnusedLocal
    def visit_function_phase(self, node, parents=None, context=None):
        self.__add_where('_phase', node.phase, 'AND', level=self.phase_where_level)

    # noinspection PyUnusedLocal
    def visit_function_version(self, node, parents=None, context=None):
        self.__vars['version'] = node.version

    # noinspection PyUnusedLocal
    def visit_func_limit(self, node, parents=None, context=None):
        self.__vars['limit'] = node.limit

    # noinspection PyUnusedLocal
    def visit_group(self, node, parents=None, context=None):
        self._sub_visit(node.expr, context=context, on_sql=_wrap_in_parentheses)

    # noinspection PyUnusedLocal
    def visit_not(self, node, parents=None, context=None):
        def wrap_in_not(sql):
            return '(NOT ' + _wrap_in_parentheses(sql) + ')'

        self._sub_visit(node.a, context=context, on_sql=wrap_in_not)

    # noinspection PyUnusedLocal
    def visit_prohibit(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    # noinspection PyUnusedLocal
    def visit_phrase(self, node, parents=None, context=None):
        phrase = str(node)

        phrase = phrase.strip()

        self.__add_where(context.get('field_name'), phrase, context.get('op'))

    # noinspection PyUnusedLocal
    def visit_range(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    # noinspection PyUnusedLocal
    def visit_plus(self, node, parents=None, context=None):
        self.__add_where(context.get('field_name'), str(node)[1:], context.get('op'))

    def visit_field_group(self, node, parents=None, context=None):
        self.visit(node.expr, parents + [node], context)

    def __add_standalone_where(self, where, op, level=0):
        self.__where.setdefault(level, []).append((op, where))

    def __add_where(self, field_name, expr, op, level=0):
        if expr is None:
            self.__where.setdefault(level, []).append((None, '%s is NULL' % field_name))
            return

        expr_parsed = parse_expr(expr) if expr is not None else None
        where = self.__expr_to_sql_where(field_name, expr_parsed)
        self.__add_standalone_where(where, op, level)

    # noinspection PyUnusedLocal
    def visit_word(self, node, parents=None, context=None):
        if context is None:
            raise ParseApplicationException('invalid field %s' % node)

        self.__add_where(context.get('field_name'), str(node), context.get('op'))

    @classmethod
    def __conditions_expr_to_sql_where(cls, field_name, item):
        sql = cls.__expr_to_sql_where(field_name, item)
        return _wrap_in_parentheses(sql)

    @classmethod
    def __is_expr_wildcards(cls, operator, val):
        return operator == '=' and isinstance(val, six.string_types) and ('?' in val or '*' in val)

    @classmethod
    def __convert_wildcards_to_regex(cls, val):
        val = unquotes_if_needed(val)

        val = re.escape(val)

        val = '^' + val.replace('\\*', '.*').replace('\\?', '.') + '$'

        val = quotes_if_needed(val)

        return val

    @classmethod
    def __condition_group_expr_to_sql_where_handle_values(cls, field_name, item):
        values = item.get('values') or []
        operator = item.get('operator', '=')
        vals = []
        for val in values:
            if cls.__is_expr_wildcards(operator, val):
                sql_where = 'REGEXP_CONTAINS(`{field_name}`, r{val_as_regex})'.format(
                    val_as_regex=cls.__convert_wildcards_to_regex(val), field_name=field_name)
            else:
                sql_where = '`{field_name}`{operator}{value}'.format(
                    field_name=field_name, operator=operator, value=quotes_if_needed(val))

            vals.append(sql_where)

        return 'OR'.join(vals)

    @classmethod
    def __condition_group_expr_to_sql_where_handle_range(cls, field_name, item):
        sql_format = None
        if 'range' in item:
            sql_format = '(`{field_name}`>={value1})AND(`{field_name}`<={value2})'
        elif 'range_inclusive' in item:
            sql_format = '(`{field_name}`>{value1})AND(`{field_name}`<{value2})'

        if sql_format is not None:
            return sql_format.format(field_name=field_name, value1=quotes_if_needed(item[0]),
                                     value2=quotes_if_needed(item[1]))

    @classmethod
    def __condition_group_expr_to_sql_where(cls, field_name, item):
        for handlers in (
                cls.__condition_group_expr_to_sql_where_handle_values,
                cls.__condition_group_expr_to_sql_where_handle_range):
            result = handlers(field_name, item)

            if result:
                return result

    @classmethod
    def __expr_to_sql_where(cls, field_name, expr):
        if 'conditions' in expr:
            sql = ''
            for item in expr:
                sql += cls.__conditions_expr_to_sql_where(field_name, item)

            return sql
        elif 'condition_group' in expr:
            return cls.__condition_group_expr_to_sql_where(field_name, expr)

        return ''

    def _handle_complex_field(self, name, value, op):
        parts = name.split('.')

        fields = '.'.join(parts[1:])
        first_part = parts[0]

        def validate_value():
            if value.isdigit():
                return int(value)

            if value.startswith('"') and value.endswith('"'):
                return value[1:-1]

            if value.endswith("'"):
                return value[:-1]

            return value

        value = json.dumps(validate_value()) if value is not None else None

        if not first_part.endswith('_json'):
            first_part = first_part + '_json'

        casted_value = 'CAST({value} AS STRING)'.format(value=value) if value is not None else None

        sql = '(matchJson(`{first_part}`, "{fields}", {casted_value}))'.format(
            first_part=first_part,
            fields=fields,
            casted_value=casted_value)

        self.has_complex_data = True
        self.__add_standalone_where(sql, op)

    @classmethod
    def _is_complex_field(cls, name):
        return '.' in name

    # noinspection PyUnusedLocal
    def visit_search_field(self, node, parents=None, context=None):
        function_node = self._handle_internal_function(node)
        if function_node is not None:
            return function_node

        context = context or {}

        for child in node.children:
            if isinstance(child, (Word, Phrase)):
                value = str(node.expr)
                if value.lower() in ['null', 'none']:
                    value = None

                if self._is_complex_field(node.name):
                    self._handle_complex_field(node.name, value, context.get('op'))
                elif value is None:
                    self.__add_where(node.name, None, 'is')
                else:
                    self.__add_where(node.name, value, context.get('op'))
            else:
                sub_context = {}
                sub_context.update(context)
                sub_context['field_name'] = node.name
                self._sub_visit(node.expr, context=sub_context)

    @classmethod
    def __combine_where(cls, sql_builder):
        combine_where = {}
        for bucket, wheres in sorted(sql_builder.where.items()):
            for where in wheres:
                operator, expr = where

                combine_where.setdefault(bucket, []).append((operator, expr))

        return combine_where

    def __combine_visit_state(self, sql_builder):
        merged_visit_state = {key: value or self.__visit_state.get(key) for key, value in sql_builder.__visit_state.items()}
        self.__visit_state = merged_visit_state

    def _sub_visit(self, child, context=None, on_sql=None):
        sql_builder = SQLQueryBuilder(self.__sql_helper)
        sql_builder.visit(child, context=context)

        self.__combine_visit_state(sql_builder)

        self.__vars.update(sql_builder.vars)

        combine_where = self.__combine_where(sql_builder)

        for bucket, wheres in combine_where.items():
            op = None
            sql = ''
            for where in wheres:
                operator, expr = where
                if op is not None:
                    sql += op

                sql += expr
                op = operator

            if on_sql:
                sql = on_sql(sql)
            elif len(wheres) > 1:
                sql = _wrap_in_parentheses(sql)

            op = (context or {}).get('op')
            self.__where.setdefault(bucket, []).append((op, sql))

    def build_vars(self):
        if not self.__vars:
            return None

        return self.__vars

    def __check_operator_dependencies(self):
        # ignore sampling on the phase split stage (using _phr) - it's already done in the grouping stage
        if self.has_sample and self.has_group_by:
            try:
                del self.__where[self.random_function_level]
            except KeyError:
                pass

    def __build_where(self):
        self.__check_operator_dependencies()
        sql = ''
        last_operator = None
        combine_operator = ''
        for bucket, wheres in sorted(self.__where.items()):
            group_where = ''
            for where in wheres:
                operator, expr = where

                if group_where:
                    group_where += last_operator if operator is None else operator

                group_where += expr

                last_operator = operator

            if len(wheres) > 1:
                group_where = _wrap_in_parentheses(group_where)

            sql = sql + combine_operator + group_where
            combine_operator = last_operator

        return sql

    def build_where(self):
        return self.__build_where() or None  # Make sure to return None and not empty string

    @property
    def where(self):
        return self.__where

    @property
    def vars(self):
        return self.__vars


# noinspection PyClassicStyleClass
class AddLimitOffsetFunctionTransformer(LuceneTreeTransformer):
    def __init__(self, limit, offset):
        self.__offset_function = FunctionOffset.create_with_args(offset) if offset is not None else None
        self.__limit_function = FunctionLimit.create_with_args(limit) if limit is not None else None
        self.__has_offset = False
        self.__has_limit = False

    # noinspection PyUnusedLocal
    def visit_function_offset(self, node, parents=None, context=None):
        self.__has_offset = True
        return self.__offset_function or node

    # noinspection PyUnusedLocal
    def visit_function_limit(self, node, parents=None, context=None):
        self.__has_limit = True
        return self.__limit_function or node

    def __call__(self, tree):
        result = self.visit(tree)
        if not self.__has_offset and self.__offset_function is not None:
            result = UnknownOperation(self.__offset_function, result)

        if not self.__has_limit and self.__limit_function is not None:
            result = UnknownOperation(self.__limit_function, result)

        return result


def get_split_vars(split):
    sql_vars = {}

    start = 0.
    for phase in ['train', 'test', 'validation']:
        percentage = split.get(phase)
        if phase is None:
            continue

        if percentage is None:
            sql_vars['phase_%s_start' % phase] = -1
            sql_vars['phase_%s_end' % phase] = -1
            continue

        sql_vars['phase_%s_start' % phase] = start
        sql_vars['phase_%s_end' % phase] = start + percentage

        start += percentage

    return sql_vars


# noinspection PyClassicStyleClass
class AddPhaseFunction(LuceneTreeTransformer):
    def __init__(self, phase):
        self.__phase_function = FunctionPhase.create_with_args(phase)
        self.__has_phase = False

    # noinspection PyUnusedLocal
    def visit_function_phase(self, node, parents=None, context=None):
        self.__has_phase = True
        return self.__phase_function

    def __call__(self, tree):
        result = self.visit(tree)
        if not self.__has_phase:
            result = UnknownOperation(self.__phase_function, result)

        return result


def _unquote_string(s):
    s = s.strip()
    if s.startswith('"') or s.startswith("'"):
        ch = s[0]
        s = s[1:]

        if s.endswith(ch):
            s = s[:-1]
    return s


class QueryParser(object):
    def __init__(self):
        self.__parser = parser()

    def parse_query(self, query):
        query = _unquote_string(query)
        return self.__parser.parse(query, lexer=lexer())


class QueryUtils(object):
    @classmethod
    def run_visitor_on_query_text(cls, query_text, visitor, parser_=None):
        parser_ = parser_ or QueryParser()
        tree = parser_.parse_query(query_text)
        visit_query(visitor, tree)
        return tree, visitor

    @classmethod
    def get_version(cls, query_text, parser_=None):
        _, visitor = cls.run_visitor_on_query_text(query_text, VersionVisitor(), parser_=parser_)
        return visitor.version or 'head'


def resolve_tree(tree, *transformers):
    transformers2 = [UnknownOperationResolver(OrOperation), MLQueryTransformer()]

    transformers2.extend(transformers)

    resolved_tree = None
    for transformer in transformers2:
        if resolved_tree is None:
            resolved_tree = transformer(tree)
            continue

        resolved_tree = transformer(resolved_tree)

    return resolved_tree


def visit_query(visitor, tree):
    resolver = resolve_tree(tree)

    if isinstance(visitor, six.class_types):
        visitor = visitor()

    visitor.visit(resolver)

    return visitor


def tree_to_sql_builder(tree, sql_helper):
    sql_builder = SQLQueryBuilder(sql_helper)
    visit_query(sql_builder, tree)

    return sql_builder


def tree_to_sql_parts(tree, sql_helper):
    sql_builder = tree_to_sql_builder(tree, sql_helper)

    return sql_builder.build_vars(), sql_builder.build_where()
