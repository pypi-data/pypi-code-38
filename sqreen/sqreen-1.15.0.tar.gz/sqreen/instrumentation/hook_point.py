# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Contains the hook_point, the code actually executed in place of
application code
"""
import logging
import sys
import time
from collections import Iterable, Mapping
from traceback import extract_stack

from ..constants import ACTIONS, LIFECYCLE_METHODS, VALID_ACTIONS_PER_LIFECYCLE
from ..exceptions import (
    ActionBlock,
    ActionRedirect,
    AttackBlocked,
    MissingDataException,
)
from ..remote_exception import RemoteException
from ..runtime_storage import runtime
from ..utils import update_wrapper
from .helpers import guard_call

LOGGER = logging.getLogger(__name__)


def _compute_result_action(current_result, next_result, valid_actions):
    """ Compute the next result_action based on current one and the callback
    result
    """
    current_status = current_result.get("status")
    next_status = next_result.get("status")
    # Check the validity of action per method
    if next_status not in valid_actions:
        # Ignore it
        return current_result

    if current_status not in valid_actions:
        return next_result

    current_result_order = valid_actions.index(current_result.get("status"))
    next_result_order = valid_actions.index(next_result.get("status"))

    # Return the old one only if it has more priority
    if current_result_order < next_result_order:
        return current_result
    else:
        return next_result


def valid_args(new_args):
    """ Check that new_args match the format ([], {}), else returns None
    """
    try:
        args, kwargs = new_args
    except (TypeError, ValueError):
        msg = "Invalid number of args or type, %s"
        LOGGER.debug(msg, new_args)
        return False

    # Check that new_args[0] is a valid type for passing to *
    if not isinstance(args, Iterable) or isinstance(args, Mapping):
        msg = "Invalid type for args[0]: %s"
        LOGGER.debug(msg, args)
        return False

    # Check that new_args[1] is a valid type for passing to **
    if not isinstance(kwargs, Mapping):
        msg = "Invalid type for args[1]: %s"
        LOGGER.debug(msg, kwargs)
        return False

    return True


def execute_callback(
    queue, callback, method, original, result_action, args, kwargs,
    storage=runtime, budget_in_ms=None
):
    """ Execute a callback protected inside a broad try except.

    The queue argument is used to push a RemoteException when an exception is raised by the callback.
    The result_action argument is a dict where each callback pushes its results.
    """

    callback_method = getattr(callback, method)
    callback_rule_name = callback.rule_name
    LOGGER.debug(
        "Running %s callback %s of module '%s'",
        method,
        callback_method,
        callback_method.__module__,
    )

    if args is None:
        args = tuple()

    if kwargs is None:
        kwargs = {}

    try:
        if callback.supports_budget:
            result = callback_method(original, __sqreen_budget=budget_in_ms, *args, **kwargs)
        else:
            result = callback_method(original, *args, **kwargs)

        # First process of result

        if not result:
            return result_action, args, kwargs

        if not callback.block:
            LOGGER.debug("%s cannot block, ignoring return value", callback)
            return result_action, args, kwargs

        if not isinstance(result, dict):
            msg = "%s returns %s during %s method"
            LOGGER.warning(msg, callback, type(result), method)
            return result_action, args, kwargs

        # Set rule_name if not set
        if result.get("rule_name") is None:
            result["rule_name"] = callback_rule_name

        valid_actions = VALID_ACTIONS_PER_LIFECYCLE[method]
        result_action = _compute_result_action(
            result_action, result, valid_actions
        )

        # We need to process MODIFY_ARGS for next callbacks
        if result_action.get("status") == ACTIONS["MODIFY_ARGS"]:
            if valid_args(result_action["args"]):
                args, kwargs = result_action["args"]

        return result_action, args, kwargs

    except MissingDataException:
        raise

    except Exception as exception:
        LOGGER.exception(
            "An exception occured while trying to execute %s", callback
        )

        exc_info = sys.exc_info()
        current_request = storage.get_current_request()
        stack = extract_stack()

        if current_request:
            callback.record_exception(exception, exc_info, stack)
        else:
            callback_exception_payload = callback.exception_infos()

            # Try to recover some infos from the exception if it's a SqreenException
            try:
                exception_infos = exception.exception_infos()
            except Exception:
                exception_infos = {}

            remote_exception = RemoteException(
                exc_info,
                callback_exception_payload,
                exception_infos,
                None,
                stack,
            )
            queue.put(remote_exception)

        return result_action, args, kwargs


def execute_callbacks(
    queue, callbacks, method, original, args=None, kwargs=None, storage=runtime, budget=None,
):
    """ Execute a list of callbacks method (pre/post/fail), catch any exception
    that could happens.

    Aggregate the callbacks result (format {"status": COMMAND}), compute the
    final ACTION to execute and return it.
    For every ACTION, each callback is executed even if the first callback
    detected an attack.
    """
    result_action = {}

    # Execute the callbacks
    for callback in callbacks:
        if callback.whitelisted:
            continue

        if budget == 0:
            break

        if budget is not None:
            start = int(time.time() * 1000)

        result = execute_callback(
            queue, callback, method, original, result_action, args, kwargs,
            storage=storage, budget_in_ms=budget
        )

        if budget is not None:
            end = int(time.time() * 1000)
            budget -= (end - start)
            if budget < 0:
                budget = 0

        result_action, args, kwargs = result

    # It is either empty dict if no override or the last one
    return result_action


def execute_pre_callbacks(key, strategy, original, args=None, kwargs=None, storage=runtime, budget=None):
    """ Execute pre_callbacks. Pre callbacks will receive these arguments:
    (original, *args, **kwargs)
    """
    pre_callbacks = strategy.get_pre_callbacks(key)

    if len(pre_callbacks) > 0:
        return guard_call(
            key,
            execute_callbacks,
            strategy.queue,
            pre_callbacks,
            LIFECYCLE_METHODS["PRE"],
            original,
            args,
            kwargs,
            storage=storage,
            budget=budget,
        )
    else:
        return {}


def execute_failing_callbacks(
    key, strategy, original, exc_infos, args=None, kwargs=None, storage=runtime, budget=None
):
    """ Execute failing_callbacks. Failing callbacks will receive these arguments:
    (original, exc_infos, *args, **kwargs)
    """
    failing_callbacks = strategy.get_failing_callbacks(key)

    if len(failing_callbacks) > 0:
        if args is None:
            args = tuple()

        new_args = [exc_infos] + list(args)

        return guard_call(
            key,
            execute_callbacks,
            strategy.queue,
            reversed(failing_callbacks),
            LIFECYCLE_METHODS["FAILING"],
            original,
            new_args,
            kwargs,
            storage=storage,
            budget=budget,
        )
    else:
        return {}


def execute_post_callbacks(
    key, strategy, original, result, args=None, kwargs=None, storage=runtime, budget=None
):
    """ Execute post_callbacks. Post callbacks will receive these arguments:
    (original, result, *args, **kwargs)
    """
    post_callbacks = strategy.get_post_callbacks(key)

    if len(post_callbacks) > 0:
        if args is None:
            args = tuple()

        new_args = [result] + list(args)

        return guard_call(
            key,
            execute_callbacks,
            strategy.queue,
            reversed(post_callbacks),
            LIFECYCLE_METHODS["POST"],
            original,
            new_args,
            kwargs,
            storage=storage,
            budget=budget
        )
    else:
        return {}


def hook_point(strategy, hook_name, hook_method, original, storage=runtime):
    """ Execute the original method and pre/post/failing callbacks
    If an exception happens, create a RemoteException, call
    callback.exception_infos for more debugging infos and send it via
    the provided queue.
    """

    def wrapper(*args, **kwargs):
        LOGGER.info(
            "Checking before hook point of %s for %s/%s",
            strategy,
            hook_name,
            hook_method,
        )
        strategy.before_hook_point()
        key = (hook_name, hook_method)

        # Call pre callbacks
        action = execute_pre_callbacks(
            key,
            strategy,
            original,
            args,
            kwargs,
            storage=storage
        )

        if action.get("status") == ACTIONS["RAISE"]:
            LOGGER.debug(
                "Callback %s detected an attack", action.get("rule_name")
            )
            raise AttackBlocked(action.get("rule_name"))
        elif action.get("status") == ACTIONS["ACTION_BLOCK"]:
            LOGGER.debug(
                "Action %s blocked the request", action.get("action_id")
            )
            raise ActionBlock(action.get("action_id"))
        elif action.get("status") == ACTIONS["ACTION_REDIRECT"]:
            LOGGER.debug(
                "Action %s redirected the request to %r",
                action.get("action_id"),
                action["target_url"],
            )
            raise ActionRedirect(action.get("action_id"), action["target_url"])
        elif action.get("status") == ACTIONS["OVERRIDE"]:
            return action.get("new_return_value")
        elif action.get("status") == ACTIONS["MODIFY_ARGS"]:
            if valid_args(action["args"]):
                args, kwargs = action["args"]

        # Call original method
        retry = True
        while retry is True:
            try:
                retry = False
                # Try to call original function
                result = original(*args, **kwargs)
            except Exception:
                # In case of error, call fail callbacks with exception infos
                exc_infos = sys.exc_info()

                # Either raise an exception, set a return value or retry
                action = execute_failing_callbacks(
                    key, strategy, original, exc_infos, args, kwargs,
                    storage=storage
                )

                if action.get("status") == ACTIONS["RAISE"]:
                    LOGGER.debug(
                        "Callback %s detected an attack",
                        action.get("rule_name"),
                    )
                    raise AttackBlocked(action.get("rule_name"))
                elif action.get("status") == ACTIONS["RETRY"]:
                    retry = True
                elif action.get("status") == ACTIONS["OVERRIDE"]:
                    return action.get("new_return_value")

                # Be sure to raise if no retry or override
                if retry is False:
                    raise

        # Then call post callback in reverse order to simulate decorator
        # behavior
        action = execute_post_callbacks(
            key, strategy, original, result, args, kwargs, storage=storage,
        )

        if action.get("status") == ACTIONS["RAISE"]:
            LOGGER.debug(
                "Callback %s detected an attack", action.get("rule_name")
            )
            raise AttackBlocked(action.get("rule_name"))
        elif action.get("status") == ACTIONS["OVERRIDE"]:
            return action.get("new_return_value")

        # And return the original value
        return result

    # Update wrapper name, module and doc
    update_wrapper(wrapper, original)

    return wrapper
