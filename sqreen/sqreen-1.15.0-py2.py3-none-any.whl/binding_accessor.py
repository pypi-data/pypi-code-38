# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
"""Binding accessor class."""

import re
import types
from os import getcwd


def flat_keys(iterable, max_iterations=1000):
    """Return the list of keys in iterable and nested iterables."""
    iteration = 0

    keys = []
    remaining_iterables = [iterable]

    seen_iterables = set()

    while len(remaining_iterables) != 0:

        iteration += 1
        # If we have a very big or nested iterable, return False.
        if iteration >= max_iterations:
            break

        iterable = remaining_iterables.pop(0)

        # Protection against recursive objects.
        if id(iterable) in seen_iterables:
            continue

        seen_iterables.add(id(iterable))

        # If we get an iterable, add it to the list of remaining iterables.
        if isinstance(iterable, dict):

            dict_values = iterable.values()
            if len(dict_values) > 0:
                remaining_iterables.extend(list(dict_values))

            dict_keys = iterable.keys()
            if len(dict_keys) > 0:
                keys.extend(dict_keys)

        elif isinstance(iterable, list) and len(iterable) > 0:
            remaining_iterables.extend(iterable)

    return keys


def flat_values(iterable, max_iterations=1000):
    """Return the list of values of iterable and nested iterables."""
    iteration = 0

    values = []
    remaining_iterables = [iterable]

    seen_iterables = set()

    while len(remaining_iterables) != 0:

        iteration += 1
        # If we have a very big or nested iterable, returns False.
        if iteration >= max_iterations:
            break

        iterable = remaining_iterables.pop(0)

        # Protection against recursive objects
        if id(iterable) in seen_iterables:
            continue

        seen_iterables.add(id(iterable))

        # If we get an iterable, add it to the list of remaining iterables.
        if isinstance(iterable, dict):

            dict_values = iterable.values()
            if len(dict_values) > 0:
                remaining_iterables.extend(list(dict_values))

        elif isinstance(iterable, list):
            if len(iterable) > 0:
                remaining_iterables.extend(iterable)

        else:
            values.append(iterable)

    return values


class StringScanner(object):
    """Lexical scanning operations on a string.

    This is a poor man equivalent of Ruby's StringScanner class.
    """

    __slots__ = ("string", "_size", "_pos", "match")

    def __init__(self, string):
        self.string = string
        self._size = len(string)
        self._pos = 0
        self.match = None

    def tell(self):
        """Return the current position in the string."""
        return self._pos

    def scan_string(self, sub):
        """Find the given substring from the current position.

        If the substring is present, the cursor position is updated and the
        substring is returned. Otherwise, this method returns None.

        This is semantically equivalent to calling scan_regex with an exact
        regexp, but faster.
        """
        size = len(sub)
        if self.string[self._pos : self._pos + size] == sub:
            self._pos += size
            return sub

    def scan_regex(self, regex):
        """Match the regex from the current position.

        If there is a match, the cursor position is updated and the match
        object is returned. Otherwise, this method returns None.
        """
        self.match = regex.match(self.string, self._pos)
        if self.match is not None:
            self._pos += len(self.match.group(0))
            return self.match

    def finished(self):
        """True if the cursor is at the end of the string, False otherwise."""
        return self._pos == self._size


class BindingAccessor(object):
    """Binding accessors.

    The class constructor is given a binding accessor expression
    (e.g. "#.args[0]") and _parses it.
    """

    __slots__ = (
        "path",
        "expression",
        "transformation",
        "_transformation_func",
        "_scanner",
    )

    def __init__(self, expression):
        self.path = []
        self.expression = expression
        self.transformation = None
        self._transformation_func = None
        self._scanner = None
        self._parse(expression)

    def _parse(self, expression):
        """Parse a binding accessor expression.

        It is internally converted to a series of componentss that are later
        resolved.
        """
        # If there is a transformation, set it and remove it
        # (e.g. "expression | transformation").
        expression = self._parse_transformation(expression)

        self._scanner = StringScanner(expression)
        while not self._scanner.finished():
            start_pos = self._scanner.tell()

            # Check for scalar values first.
            scalar = self._scan_scalar()
            if scalar:
                self.path.append(scalar)
                return

            # If we are at the beginning of an expression, a variable is
            # allowed.
            if start_pos == 0:
                self._scan_push_variable()
            else:
                self._scan_push_attribute()
            self._scan_push_indexes()

            # Remove potential dot.
            self._scanner.scan_string(".")

            if start_pos == self._scanner.tell():
                raise ValueError("parsing error, _parser is stuck")

        # Delete the scanner instance.
        self._scanner = None

    _TRANSFORMATION_REGEX = re.compile(r"\|[ \w]*$")
    _TRANSFORMATION_FUNCS = {
        "len": len,
        "flat_keys": flat_keys,
        "flat_values": flat_values,
    }

    def _parse_transformation(self, expression):
        """Try to parse a transformation out of an expression."""
        match = self._TRANSFORMATION_REGEX.search(expression)
        if match is None:
            return expression
        len_suffix = len(match.group(0))
        self.transformation = expression[-len_suffix + 1 :].strip()

        # Check that the transformation name is defined.
        if self.transformation not in self._TRANSFORMATION_FUNCS:
            raise ValueError(
                "unknown transformation {!r} for expression {!r}".format(
                    self.transformation, expression
                )
            )

        self._transformation_func = self._TRANSFORMATION_FUNCS[
            self.transformation
        ]
        return expression[:-len_suffix].rstrip()

    _SQREEN_VARIABLE_REGEX = re.compile(r"#\.(\w+)")
    _PYTHON_IDENTIFIER_REGEX = re.compile(r"[a-zA-Z_](?:\w)*")

    def _scan_push_variable(self):
        """Try to parse a variable and push it to the components list.

        Do nothing if the scanner cannot parse a variable or a Python
        identifier.
        """
        if self._scanner.scan_regex(self._SQREEN_VARIABLE_REGEX):
            self.path.append(
                {
                    "name": self._scanner.match.group(1),
                    "kind": "sqreen-variable",
                }
            )
        elif self._scanner.scan_regex(self._PYTHON_IDENTIFIER_REGEX):
            self.path.append(
                {"name": self._scanner.match.group(), "kind": "variable"}
            )

    def _scan_push_attribute(self):
        """Try to parse an attribute and push it to the components list.

        Do nothing of the scanner cannot parse a Python identifier.
        """
        if self._scanner.scan_regex(self._PYTHON_IDENTIFIER_REGEX):
            self.path.append(
                {"name": self._scanner.match.group(), "kind": "attribute"}
            )

    _INTEGER_REGEX = re.compile(r"\d+")
    _STRING_REGEX = re.compile(r"'((?:\\.|[^\\'])*)'")

    def _scan_scalar(self):
        """Scan a scalar value and return the corresponding components.

        Return None if the scanner cannot parse an integer or a string.
        """
        if self._scanner.scan_regex(self._INTEGER_REGEX):
            return {
                "value": int(self._scanner.match.group()),
                "kind": "integer",
            }
        elif self._scanner.scan_regex(self._STRING_REGEX):
            return {"value": self._scanner.match.group(1), "kind": "string"}

    def _scan_push_indexes(self):
        """Scan a sequence of indexes and push them to the components list."""
        while self._scanner.scan_string("[") is not None:
            scalar = self._scan_scalar()
            if scalar is None:
                raise ValueError("invalid index")
            if self._scanner.scan_string("]") is None:
                raise ValueError("unfinished index")
            self.path.append({"index": scalar["value"], "kind": "index"})

    def resolve(
        self,
        binding=None,
        global_binding=None,
        framework=None,
        instance=None,
        arguments=None,
        kwarguments=None,
        cbdata=None,
        return_value=None,
    ):
        """Given a context, resolve the expression and return the value."""
        if binding is None:
            binding = {}
        if global_binding is None:
            global_binding = {}

        env = [
            framework,
            instance,
            arguments,
            kwarguments,
            cbdata,
            return_value,
        ]
        value = None
        for component in self.path:
            value = self._resolve_component(
                value, component, binding, global_binding, env
            )
        self._validate_value(value)

        if self.transformation is not None:
            value = self._transformation_func(value)

        return value

    def _resolve_component(
        self, value, component, binding, global_binding, env
    ):
        """Resolve a component.

        Simple expressions (static strings, integers, indexes and
        attributes) are directly resolved. Others are dispatched to specialized
        methods.
        """
        component_kind = component["kind"]
        if component_kind == "string" or component_kind == "integer":
            return component["value"]
        elif component_kind == "variable":
            return self._resolve_variable(
                component["name"], binding, global_binding
            )
        elif component_kind == "index":
            return value[component["index"]]
        elif component_kind == "attribute":
            return getattr(value, component["name"])
        elif component_kind == "sqreen-variable":
            return self._resolve_sqreen_variable(component["name"], *env)
        else:
            raise ValueError(
                "invalid component kind {!r}".format(component_kind)
            )

    def _resolve_sqreen_variable(
        self,
        what,
        framework,
        instance,
        arguments,
        kwarguments,
        cbdata,
        return_value,
    ):
        """Resolve sqreen-variables (the ones starting with #.).

        Fall back on the framework object if the value is not a special
        sqreen-variable. Return None if the framework is None.
        """
        if what == "data":
            return cbdata
        elif what == "rv":
            return return_value
        elif what == "args" or what == "cargs":
            return arguments
        elif what == "kwargs":
            return kwarguments
        elif what == "inst":
            return instance
        elif what == "cwd":
            return getcwd()
        elif framework is not None:
            if what == "client_ip":
                return str(framework.client_ip)
            else:
                return getattr(framework, what)

    def _resolve_variable(self, variable_name, binding, global_binding):
        """Resolve a general variable name.

        Search in local context first, then in general context.
        """
        if variable_name in binding:
            return binding[variable_name]
        elif variable_name in global_binding:
            return global_binding[variable_name]
        else:
            raise NameError(
                "name {!r} was not found in bindings".format(variable_name)
            )

    def _validate_value(self, value):
        """Raise ValueError if the value is a method or a function."""
        if isinstance(value, (types.FunctionType, types.MethodType)):
            raise ValueError("invalid return value {!r}".format(value))

    def __repr__(self):
        return "{}({!r})".format(self.__class__.__name__, self.expression)
