# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Callbacks rules classes and helpers
"""
import logging
from datetime import datetime
from functools import wraps

from .condition_evaluator import ConditionEvaluator, is_condition_empty
from .constants import LIFECYCLE_METHODS
from .payload_creator import PayloadCreator
from .remote_exception import raw_traceback_formatter, traceback_formatter
from .runtime_storage import runtime

LOGGER = logging.getLogger(__name__)


class BaseCallback(object):
    """ Base class for callbacks.

    The hook_name is the path to the hook, it could be either a module, like
    "package.module", or a specific class "package.module::Class".
    The hook_name is the name of the function to hook_on, it's relative to
    the hook_module, for example with a hook_module equal to
    "package.module::Class" and a hook_path equal to "method", we will
    hook on the method named "method" of a class named "Class" in the module
    named "package.module"
    """

    SUPPORTS_BUDGET = False  # override constant in subclasses supporting it

    def __init__(self, hook_module, hook_name, strategy=None):
        self.hook_module = hook_module
        self.hook_name = hook_name
        self.strategy = strategy

    @property
    def supports_budget(self):
        return self.SUPPORTS_BUDGET


def check_condition_wrapper(rule_data, function, condition, lifecycle, storage=runtime):
    """ Wrapper that will check lifecycle method pre-condition before
    calling it.
    If pre-conditions are true, call the lifecycle method, otherwise
    return None.
    """

    @wraps(function)
    def wrapped(*args, **kwargs):
        """ Wrapper around lifecycle method
        """

        # Copy args to work on them
        binding_args = list(args)

        # Compute return value depending on the lifecycle method we wrap
        return_value = False
        if lifecycle in ("post", "failing"):
            # Args[1/2] is either the return value of the hooked point
            # or the exception
            return_value = binding_args.pop(1)

        original = binding_args.pop(0)

        binding_eval_args = {
            "binding": locals(),
            "global_binding": globals(),
            "framework": storage.get_current_request(),
            "instance": original,
            "arguments": storage.get_current_args(binding_args),
            "cbdata": rule_data,
            "return_value": return_value,
        }

        # Check the pre condition
        condition_result = condition.evaluate(**binding_eval_args)

        LOGGER.debug(
            "ConditionWrapper (%s) result for %s: %s",
            condition,
            function,
            condition_result,
        )

        if condition_result in (False, None):
            return None

        # Execute the hook otherwise with the original args
        return function(*args, **kwargs)

    wrapped.__wrapped__ = function

    return wrapped


def call_count_wrapper(
    function, lifecycle, call_count_interval, observation_key, callback
):
    """ Wrapper around lifecycle methods that record number of calls
    """

    @wraps(function)
    def wrapped(*args, **kwargs):
        """ Record the number of calls for this callback lifecycle method.
        Buffer the number in the callback itself (self.call_counts) and record
        an observation every X times, X being the field call_count_interval of
        the rule.
        """
        current_count = callback.call_counts[lifecycle]

        if current_count + 1 == call_count_interval:
            callback.record_observation(
                "sqreen_call_counts", observation_key, call_count_interval
            )
            callback.call_counts[lifecycle] = 0
        else:
            callback.call_counts[lifecycle] += 1

        return function(*args, **kwargs)

    wrapped.__wrapped__ = function

    return wrapped


class RuleCallback(BaseCallback):
    def __init__(
        self,
        hook_module,
        hook_name,
        rule_name,
        rulespack_id,
        block,
        test,
        runner,
        strategy_cls=None,
        data=None,
        conditions=None,
        callbacks=None,
        call_count_interval=0,
        metrics=None,
        payload_sections=None,
        storage=runtime,
        attack_render_info=None
    ):
        super(RuleCallback, self).__init__(
            hook_module, hook_name, strategy_cls
        )
        self.rule_name = rule_name
        self.rulespack_id = rulespack_id

        if data is None:
            data = {}
        self.data = data
        self.block = block
        self.test = test
        self.runner = runner
        self.metrics = metrics
        self.storage = storage

        if conditions is None:
            conditions = {}
        self.conditions = conditions

        self.callbacks = callbacks
        self.attack_render_info = attack_render_info

        # Callbacks
        self.call_count_interval = call_count_interval
        self.call_counts = {"pre": 0, "post": 0, "failing": 0}

        self._apply_conditions()
        self._apply_call_count()

        # Payload sections.
        if payload_sections is None:
            payload_sections = PayloadCreator.SECTIONS
        self.payload_sections = payload_sections

    @classmethod
    def from_rule_dict(cls, rule_dict, runner, storage=runtime):
        """ Return a RuleCallback based on a rule dict
        """
        return cls(
            hook_module=rule_dict["hookpoint"]["klass"],
            hook_name=rule_dict["hookpoint"]["method"],
            rule_name=rule_dict["name"],
            rulespack_id=rule_dict["rulespack_id"],
            strategy_cls=rule_dict["hookpoint"].get("strategy", "import_hook"),
            attack_render_info=rule_dict["hookpoint"].get("attack_render_info", {}),
            block=rule_dict["block"],
            test=rule_dict["test"],
            data=rule_dict.get("data"),
            conditions=rule_dict.get("conditions"),
            callbacks=rule_dict.get("callbacks"),
            call_count_interval=rule_dict.get("call_count_interval", 0),
            runner=runner,
            metrics=rule_dict.get("metrics", []),
            payload_sections=rule_dict.get("payload"),
            storage=storage,
        )

    @classmethod
    def get_budget(cls, kwargs):
        if isinstance(kwargs, dict):
            return kwargs.pop("__sqreen_budget", None)
        return None

    def _apply_conditions(self):
        """ Wrap each lifecycle methods if the Rule define them and if we have
        conditions for them.
        """
        for lifecycle in LIFECYCLE_METHODS.values():
            conditions = self.conditions.get(lifecycle)

            if not is_condition_empty(conditions) and hasattr(self, lifecycle):
                conditions = ConditionEvaluator(conditions)

                # Wrap the lifecycle method
                lifecycle_method = getattr(self, lifecycle)
                wrapped = check_condition_wrapper(
                    self.data, lifecycle_method, conditions, lifecycle,
                    storage=self.storage
                )
                setattr(self, lifecycle, wrapped)

    def _apply_call_count(self):
        # Only count calls if call_count_interval is > 0
        if self.call_count_interval == 0:
            return

        for lifecycle in LIFECYCLE_METHODS.values():
            if hasattr(self, lifecycle):
                lifecycle_method = getattr(self, lifecycle)

                observation_key = "%s/%s/%s" % (
                    self.rulespack_id,
                    self.rule_name,
                    lifecycle,
                )

                wrapped = call_count_wrapper(
                    lifecycle_method,
                    lifecycle,
                    self.call_count_interval,
                    observation_key,
                    self,
                )
                setattr(self, lifecycle, wrapped)

    def exception_infos(self, infos={}):
        """ Returns additional infos in case of exception
        """
        return {"rule_name": self.rule_name, "rulespack_id": self.rulespack_id}

    def record_attack(self, infos=None, at=None):
        """Record an attack."""
        if at is None:
            at = datetime.utcnow()
        payload = {
            "infos": infos,
            "rulespack_id": self.rulespack_id,
            "rule_name": self.rule_name,
            "test": self.test,
            "time": at,
        }
        if "context" in self.payload_sections:
            current_request = self.storage.get_current_request()
            if current_request:
                payload["backtrace"] = list(current_request.raw_caller)
        LOGGER.debug("Observed attack %r", payload)
        self.storage.observe("attacks", payload, self.payload_sections)

    def record_observation(self, metric_name, key, value, at=None):
        """Record a metric observation."""

        self.global_record_observation(metric_name, key, value, at, storage=self.storage)

    @classmethod
    def global_record_observation(cls, metric_name, key, value, at=None, storage=runtime):
        """Record a metric observation"""

        if at is None:
            at = datetime.utcnow()
        payload = (metric_name, at, key, value)
        LOGGER.debug("Observed metric %r", payload)
        storage.observe("observations", payload, report=False)

    def record_exception(self, exc, exc_info, stack=None, infos=None, at=None):
        """Record an exception."""
        if infos is None:
            infos = {}
        if at is None:
            at = datetime.utcnow()
        # Try to recover some infos from the exception if it's a
        # SqreenException.
        try:
            infos["exception"] = exc.exception_infos()
        except Exception:
            pass
        bt = raw_traceback_formatter(exc_info[2])
        if stack is not None:
            bt = traceback_formatter(stack) + bt
        payload = {
            "message": str(exc_info[1]),
            "klass": exc_info[0].__name__,
            "infos": infos,
            "rule_name": self.rule_name,
            "test": self.test,
            "time": at,
            "backtrace": bt,
        }
        LOGGER.debug("Observed exception %r", payload)
        self.storage.observe("sqreen_exceptions", payload, self.payload_sections)

    @property
    def lifecycle_methods(self):
        return [
            lifecycle
            for lifecycle in LIFECYCLE_METHODS.values()
            if hasattr(self, lifecycle)
        ]

    @property
    def whitelisted(self):
        """ Return True if the callback should be skipped (whitelisted
        request), False otherwise
        """
        if self.runner is None:
            return False
        return self.storage.get_whitelist_match(self.runner.settings) is not None

    def __repr__(self):
        return "%s(rule_name=%r)" % (self.__class__.__name__, self.rule_name)
