# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Base class for JS Callbacks
"""
import hashlib
import logging

from py_mini_racer.py_mini_racer import JSEvalException, JSTimeoutException

from ..binding_accessor import BindingAccessor
from ..exceptions import SqreenException
from ..frameworks.blank import BlankRequest
from ..rules import RuleCallback
from ..utils import ALL_STRING_CLASS, CustomJSONEncoder, is_string
from .mini_racer_pool import JSContextPool

LOGGER = logging.getLogger(__name__)


class JSException(SqreenException):
    """ Base exception raised in JSCB
    """

    def __init__(self, message, callback, arguments):
        super(JSException, self).__init__(message)
        self.callback = callback
        self.arguments = arguments

    def exception_infos(self):
        return {"cb": self.callback, "args": self.arguments}


class JSCB(RuleCallback):
    """ A callback that run a JS function as pre / post / failing through
    py_mini_racer context.
    """

    SUPPORTS_BUDGET = True

    def __init__(self, *args, **kwargs):
        super(JSCB, self).__init__(*args, **kwargs)

        self._loaded = False
        self.arguments = {}
        self.source = ''
        self.code_id = None

    def load(self):
        """ Create the binding accessors and save the js definitions
        """

        self.source = ''
        if self.callbacks:
            for callback_name, callback_args in self.callbacks.items():

                if not isinstance(callback_args, list):
                    self.source += "{} = {}\n".format(callback_name, callback_args)
                    self.arguments[callback_name] = []
                else:
                    self.source += "{} = {}\n".format(callback_name, callback_args[-1])
                    arguments = callback_args[:-1]
                    self.arguments[callback_name] = [
                        BindingAccessor(arg) for arg in arguments
                    ]

        self.code_id = hashlib.md5(self.source.encode('utf-8')).hexdigest()
        self._loaded = True

    def __getattribute__(self, name):
        """ Lie about pre / post / failing existence if no callbacks is defined
        for them
        """
        if name in ("pre", "post", "failing"):
            if name not in self.callbacks:
                err_msg = "'{}' object has no attribute '{}'"
                raise AttributeError(
                    err_msg.format(self.__class__.__name__, name)
                )

        return RuleCallback.__getattribute__(self, name)

    def pre(self, original, *args, **kwargs):
        """ Call the pre JS function with its arguments
        """
        return self.execute(
            "pre", self.get_budget(kwargs), original, None, args, kwargs
        )

    def post(self, original, return_value, *args, **kwargs):
        """ Call the post JS function with its arguments
        """
        return self.execute(
            "post",
            self.get_budget(kwargs),
            original,
            return_value,
            args,
            kwargs,
        )

    def failing(self, original, exception, *args, **kwargs):
        """ Call the failing JS function with its arguments
        """
        return self.execute(
            "failing",
            self.get_budget(kwargs),
            original,
            exception,
            args,
            kwargs,
        )

    def execute(self, name, budget_in_ms, *args, **kwargs):
        """ Fetches a context before executing _execute
        """
        if self._loaded is False:
            self.load()

        pool = JSContextPool.fetch_for_runner(self.runner)
        return pool.with_context(
            lambda ctx: self._execute(
                ctx, name, budget_in_ms, self.arguments[name], *args, **kwargs))

    def _execute(self, js_ctx, name, budget_in_ms, arguments, original, return_value, args, kwargs):
        """ Execute a JS callback passed in definition.
        Handle recording attack, observations and chaining.
        Protected against infinite recursion with a max number of JS calls
        set to 100.
        """

        if self.code_id in js_ctx.failed_code_ids:
            LOGGER.debug("Skipping execution of callback %s (code md5 %s)"
                         " due to previous failure of definition eval",
                         name, self.code_id)
            return

        if self.code_id not in js_ctx.code_ids:
            js_ctx.add_code(self.code_id, self.source)

        request = self.storage.get_current_request()

        # Fallback on a blank request for binding accessor
        if request is None:
            request = BlankRequest()

        # Safeguard against infinite recursion

        for _ in range(100):
            binding_eval_args = {
                "binding": locals(),
                "global_binding": globals(),
                "framework": request,
                "instance": original,
                "arguments": self.storage.get_current_args(args),
                "kwarguments": kwargs,
                "cbdata": self.data,
                "return_value": return_value,
            }

            resolved_args = [
                arg.resolve(**binding_eval_args) for arg in arguments
            ]
            if name in self.conditions:
                resolved_args = self._restrict(name, resolved_args)

            LOGGER.debug("Resolved args %s for %s", resolved_args, arguments)
            if not budget_in_ms:
                budget_in_ms = 0

            try:
                callee = "sqreen_data['{}']['{}']".format(self.code_id, name)
                result = js_ctx.call(
                    callee, *resolved_args,
                    encoder=CustomJSONEncoder, timeout=budget_in_ms
                )
            except JSTimeoutException as err:
                LOGGER.debug("Budget exhausted while running JS callback: %s", err)
                return None
            except JSEvalException as err:
                raise JSException(err.args[0], name, resolved_args)

            LOGGER.debug("JS Result %r for %s", result, self.rule_name)

            if result is None:
                return result

            # Process the return value
            self._record_attack(result)
            self._record_observations(result)

            # Check for chaining
            if result.get("call") is None:
                return result

            # Prepare next call
            name = result["call"]

            if name not in self.callbacks:
                raise JSException(
                    "Invalid callback '{}'".format(name), name, None
                )

            return_value = result.get("data")

            if result.get("args"):
                arguments = [BindingAccessor(arg) for arg in result["args"]]
            else:
                arguments = self.arguments[name]

    def _record_attack(self, return_value):
        """ Record an attack if the JS callback returned a record info
        """
        if return_value.get("record"):
            self.record_attack(return_value["record"])

    def _record_observations(self, return_value):
        """ Record observations if the JS callback returned a observations list
        """
        if return_value.get("observations"):
            for observation in return_value["observations"]:
                self.record_observation(*observation)

    def _restrict(self, name, arguments):
        """ Filter out useless values from iterables present in *arguments*.
        """
        if name not in self.conditions or name not in self.arguments:
            return arguments
        condition = self.conditions[name]
        expressions = [
            accessor.expression for accessor in self.arguments[name]
        ]
        for value, iterable, min_length in self.iter_hash_val_include_values(
            condition
        ):
            try:
                value_idx = expressions.index(value)
                iterable_idx = expressions.index(iterable)
            except ValueError:
                continue
            arguments[iterable_idx] = self.hash_value_included(
                arguments[value_idx], arguments[iterable_idx], int(min_length)
            )
        return arguments

    @classmethod
    def iter_hash_val_include_values(cls, condition, depth=10):
        """ Recursively yield arguments of operator %hash_val_includes in
        *condition*.
        """
        if depth <= 0:
            return
        for key, values in condition.items():
            if key == "%hash_val_include":
                yield values
            else:
                for value in values:
                    if not isinstance(value, dict):
                        continue
                    for v in cls.iter_hash_val_include_values(
                        value, depth - 1
                    ):
                        yield v

    @classmethod
    def hash_value_included(cls, needed, iterable, min_length=8, max_depth=20):
        """ Return a filtered, deep copy of dict *iterable*, where only
        (sub)values included in *needed* are present.
        """
        needed = needed if is_string(needed) else str(needed)
        result = {}
        insert = []
        todos = [(result, key, value, 0) for key, value in iterable.items()]
        while todos:
            where, key, value, depth = todos.pop()
            if not isinstance(key, (int, ALL_STRING_CLASS)):
                key = str(key)
            if depth >= max_depth:
                insert.append((where, key, value))
            elif isinstance(value, dict):
                val = {}
                insert.append((where, key, val))
                todos.extend((val, k, v, depth + 1) for k, v in value.items())
            elif isinstance(value, list):
                val = []
                insert.append((where, key, val))
                todos.extend(
                    (val, k, v, depth + 1) for k, v in enumerate(value)
                )
            else:
                v = value if is_string(value) else str(value)
                if len(v) < min_length or v not in needed:
                    pass
                elif isinstance(where, list):
                    where.append(value)
                else:
                    where[key] = value
        for where, key, value in reversed(insert):
            if not value:
                pass
            elif isinstance(where, list):
                where.append(value)
            else:
                where[key] = value
        return result
