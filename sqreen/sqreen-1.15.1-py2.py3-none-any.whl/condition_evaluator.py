# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Condition evaluator."""

import operator
from collections import deque
from functools import wraps
from logging import getLogger

from .binding_accessor import BindingAccessor
from .exceptions import SqreenException
from .utils import is_string, is_unicode

LOGGER = getLogger(__name__)


class ConditionError(SqreenException):
    """Base class for condition errors."""


class ConditionValueError(ConditionError):
    """Exception raised when the condition is invalid."""


class ConditionRecursionError(ConditionError):
    """Exception raised when the condition is too deeply nested."""


def hash_value_includes(value, iterable, min_value_size, max_iterations=1000):
    """Check whether a nested iterable value is included into a string.

    The iterable can be a combination of dicts and lists. The argument
    min_value_size  is used to avoid comparison on small strings: For example,
    there is no possible SQL injection below 8 characters.
    """
    iteration = 0

    # Early stop.
    if iterable is None:
        return False

    if value is None:
        return False

    elif not is_string(value):
        if isinstance(value, bytes):
            value = str(value)
        # FIXME: We had customer with List instead of string. This will prevent any exception
        else:
            return False

    if isinstance(iterable, dict):
        remaining_iterables = deque(iterable.values())
    else:
        remaining_iterables = deque(iterable)

    while remaining_iterables:

        iteration += 1
        # If we have a very big or nested iterable, return True to execute the
        # rule.
        if iteration >= max_iterations:
            return True

        iterable = remaining_iterables.popleft()

        # If we get an iterable, add it to the list of remaining iterables.
        if isinstance(iterable, dict):
            remaining_iterables.extend(iterable.values())
        elif isinstance(iterable, list):
            remaining_iterables.extend(iterable)
        else:
            # Convert and check the value.
            if not is_string(iterable):
                iterable = str(iterable)
            if not is_unicode(iterable) and is_unicode(value):
                iterable = iterable.decode(errors='replace')
            elif not is_unicode(value) and is_unicode(iterable):
                value = value.decode(errors='replace')

            if len(iterable) >= min_value_size and iterable in value:
                return True

    return False


def hash_key_includes(patterns, iterable, min_value_size, max_iterations=1000):
    """Check whether a nested iterable key matches a pattern.

    The iterable can be a combination of dicts and lists. The argument
    min_value_size is used to avoid comparison on small strings: for example,
    there is no possible MongoDB injection below 1 characters.
    """
    iteration = 0

    # Early stop.
    if not isinstance(iterable, dict):
        return False

    remaining_iterables = deque([iterable])

    while remaining_iterables:

        iteration += 1
        # If we have a very big or nested iterable, return True to execute the
        # rule.
        if iteration >= max_iterations:
            return True

        iterable_value = remaining_iterables.popleft()

        if not iterable_value:
            continue

        if isinstance(iterable_value, list):
            remaining_iterables.extend(iterable_value)
        elif isinstance(iterable_value, dict):
            # Process the keys.
            for key, value in iterable_value.items():

                if isinstance(value, dict):
                    remaining_iterables.extend(iterable_value.values())
                elif isinstance(value, list):
                    remaining_iterables.extend(value)
                elif len(key) >= min_value_size and key in patterns:
                    return True

    return False


def unpack_parameters(f):
    """Unpack first argument into multiple arguments."""
    @wraps(f)
    def wrapper(values, **kwargs):
        return f(*values, **kwargs)
    return wrapper


OPERATORS = {
    "%and": all,
    "%or": any,
    "%equals": unpack_parameters(operator.eq),
    "%not_equals": unpack_parameters(operator.ne),
    "%gt": unpack_parameters(operator.gt),
    "%gte": unpack_parameters(operator.ge),
    "%lt": unpack_parameters(operator.lt),
    "%lte": unpack_parameters(operator.le),
    "%include": unpack_parameters(operator.contains),
    "%hash_val_include": unpack_parameters(hash_value_includes),
    "%hash_key_include": unpack_parameters(hash_key_includes),
}

OPERATORS_ARITY = {
    "%equals": 2,
    "%not_equals": 2,
    "%gt": 2,
    "%gte": 2,
    "%lt": 2,
    "%lte": 2,
    "%include": 2,
    "%hash_val_include": 3,
    "%hash_key_include": 3,
}


def is_condition_empty(condition):
    """Return True if the condition is no-op, False otherwise."""
    if condition is None:
        return True
    elif isinstance(condition, bool):
        return False
    elif isinstance(condition, dict):
        return len(condition) == 0
    else:
        LOGGER.warning("Invalid precondition type: %r", condition)
        return True


def compile_condition(condition, level):
    """Compile a raw condition and validate it.

    Values are replaced by BindingAccessor instances and operator validity and
    arity are checked.
    """
    if level <= 0:
        raise ConditionRecursionError("compile recursion depth exceeded")

    if isinstance(condition, bool):
        return condition

    if not isinstance(condition, dict):
        raise ConditionValueError(
            "condition should be a dict, got {}".format(type(condition))
        )

    compiled = {}

    for _operator, values in condition.items():

        # Check operator validity.
        if _operator not in OPERATORS:
            raise ConditionValueError("unkown operator {!r}".format(_operator))

        # Check operator arity.
        arity = OPERATORS_ARITY.get(_operator, len(values))
        if len(values) != arity:
            raise ConditionValueError(
                "bad arity for operator {!r}: expected {}, got {}".format(
                    _operator, arity, len(values)
                )
            )

        # Check types.
        if not isinstance(values, list):
            raise ConditionValueError(
                "values should be an array, got {}".format(type(values))
            )

        compiled_values = []
        for value in values:
            if isinstance(value, bool):
                compiled_values.append(value)
            elif isinstance(value, dict):
                compiled_values.append(compile_condition(value, level - 1))
            elif isinstance(value, bytes):
                compiled_values.append(BindingAccessor(value.decode(errors='replace')))
            elif is_string(value):
                compiled_values.append(BindingAccessor(value))
            else:
                # XXX we should warn on this because not all types will nicely convert to string
                # and most of the time it will repr() the value.
                compiled_values.append(BindingAccessor(str(value)))

        compiled[_operator] = compiled_values

    return compiled


def evaluate(value, level=1, **kwargs):
    """Evaluate a value."""

    if isinstance(value, BindingAccessor):
        return value.resolve(**kwargs)

    elif isinstance(value, dict):

        if level <= 0:
            raise ConditionRecursionError("resolve recursion depth exceeded")

        for operator_name, values in value.items():
            operator_func = OPERATORS.get(operator_name)
            if operator_func is None:
                raise ConditionValueError("unkown operator {!r}".format(operator_name))

            # Create a lazily evaluated value generator
            values = (evaluate(v, level - 1, **kwargs) for v in values)
            result = operator_func(values)
            if result is False:
                return False

        return True

    return value


class ConditionEvaluator(object):
    """Evaluate a condition, resolving literals using BindingAccessor.

    {"%and": ["true", "true"]} -> true
    {"%or": ["true", "false"]} -> true
    {"%and": ["false", "true"]} -> false
    {"%equal": ["coucou", "#.args[0]"]} -> "coucou" == args[0]
    {"%hash_val_include": ["toto is a small guy", "#.request_params", 0]} ->
        true if one value of request params in included
        in the sentence 'toto is a small guy'.

    Combined expressions:
    { "%or":
        [
            {"%hash_val_include": ["AAA", "#.request_params", 0]},
            {"%hash_val_include": ["BBB", "#.request_params", 0]},
        ]
    }
    will return true if one of the request_params includes either AAA or BBB.
    """

    def __init__(self, condition):
        self.raw_condition = condition
        self.compiled = compile_condition(condition, 10)

    def evaluate(self, **kwargs):
        """Evaluate the compiled condition and return the result."""
        return evaluate(self.compiled, 10, **kwargs)

    def __repr__(self):
        return "{}({})".format(self.__class__.__name__, self.raw_condition)
