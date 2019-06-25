# Copyright (c) Microsoft Corporation. All rights reserved.
""" Module containing higher level function expressions.
"""

from .expressions import (Expression, InvokeExpression, IdentifierExpression, ValueExpression, _ensure_expression,
                          _assert_expression, IntExpressionLike, BoolExpressionLike, StrExpressionLike)
from .engineapi.typedefinitions import TrimType, FieldType


def round(value: Expression, decimal_places: IntExpressionLike) -> Expression:
    """
    Creates an expression that will round the result of the expression specified to the desired number of decimal places.

    :param value: An expression that returns the value to round.
    :param decimal_places: The number of desired decimal places. Can be a value or an expression.
    :return: An expression that results in the rounded number.
    """
    _assert_expression(value)
    decimal_places = _ensure_expression(decimal_places)
    Expression._validate_type(value, FieldType.DECIMAL)
    Expression._validate_type(decimal_places, FieldType.INTEGER)
    return InvokeExpression(InvokeExpression(IdentifierExpression('AdjustColumnPrecision'), [decimal_places]), [value])


def trim_string(value: Expression,
                trim_left: BoolExpressionLike=True,
                trim_right: BoolExpressionLike=True) -> Expression:
    """
    Creates an expression that will trim the string resulting from the expression specified.

    :param value: An expression that returns the value to trim.
    :param trim_left: Whether to trim from the beginning. Can be a value or an expression.
    :param trim_right: Whether to trim from the end. Can be a value or an expression.
    :return: An expression that results in a trimmed string.
    """
    _assert_expression(value)
    trim_left = _ensure_expression(trim_left)
    trim_right = _ensure_expression(trim_right)
    Expression._validate_type(value, FieldType.STRING)
    Expression._validate_type(trim_left, FieldType.BOOLEAN)
    Expression._validate_type(trim_right, FieldType.BOOLEAN)
    return InvokeExpression(InvokeExpression(IdentifierExpression('TrimStringTransform'), [
        trim_left,
        trim_right,
        ValueExpression(TrimType.WHITESPACE.value),
        ValueExpression(None)
    ]), [value])


def get_stream_name(value: Expression) -> Expression:
    """
    Creates an expression that returns the name of the file backing the input stream.

    :param value: An expression that returns a stream.
    :return: An expression that results in the name of the stream.
    """
    _assert_expression(value)
    return InvokeExpression(IdentifierExpression('GetResourceName'), [value])


def get_stream_properties(value: Expression) -> Expression:
    """
    Creates an expression that returns a set of properties (such as last modified time) of the stream.
        The properties can vary depending on the type of the stream.

    :param value: An expression that returns a stream.
    :return: A record containing the stream's properties.
    """
    _assert_expression(value)
    return InvokeExpression(IdentifierExpression('GetStreamProperties'), [value])


def create_datetime(*values: Expression) -> Expression:
    """
    Creates an expression that returns a datetime from the given list of date parts.
        The input values should be in this order: year, month, day, hour, minute, second.
        The values can be of string or numeric type.
        e.g., create_datetime(2019), create_datetime(2019, 2)

    :param values: Date parts.
    :return: Created datetime.
    """
    return InvokeExpression(IdentifierExpression('CreateDateTime'), [_ensure_expression(value) for value in values])


class RegEx:
    """
    The RegEx class makes it possible to create expressions that leverage regular expressions.

    .. remarks::

        The way in which the pattern specified is parsed and executed will depend on the execution mode.
        When executing in local or scale-up mode (such as when calling to_pandas_dataframe), the CLR engine will be used;
        when executing in Spark, the JVM engine will be used.

        There is no time limit enforced on regular expression execution. This means that, depending on your input
        and pattern, it could take a long time to evaluate it.
    """
    def __init__(self,
                 pattern: StrExpressionLike,
                 single_line: bool = False,
                 multiline: bool = False,
                 ignore_case: bool = False):
        pattern = _ensure_expression(pattern)
        Expression._validate_type(pattern, FieldType.STRING)

        if not isinstance(single_line, bool):
            raise ValueError('single_line must be bool')
        if not isinstance(multiline, bool):
            raise ValueError('multiline must be bool')
        if not isinstance(ignore_case, bool):
            raise ValueError('ignore_case must be bool')

        self._pattern = pattern
        self._single_line = single_line
        self._multiline = multiline
        self._ignore_case = ignore_case

    def is_match(self, value: StrExpressionLike):
        """
        Creates an expression that will return whether the specified value can be matched by this regular expression.

        :param value: The value to match against.
        :return: An expression that returns whether the value can be matched.
        """
        regex_fn_expression = InvokeExpression(IdentifierExpression('RegexIsMatch'), [
            self._pattern,
            ValueExpression(self._single_line),
            ValueExpression(self._multiline),
            ValueExpression(self._ignore_case)
        ])

        return InvokeExpression(regex_fn_expression, [value])
    
    def extract_record(self, value: Expression):
        """
        Creates an expression that will return a record with group names in the regex
            as keys and matching strings as values.

        :param value: The value to match against.
        :return: An expression that returns a record with group names in the regex
            as keys and matching strings as values.
        """

        value = _ensure_expression(value)
        regex_fn_expression = InvokeExpression(IdentifierExpression('RegexRecordExtractor'), [self._pattern])

        return InvokeExpression(regex_fn_expression, [value])