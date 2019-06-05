# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Execute and sanitize remote commands
"""
import json
import logging
from copy import copy

from sqreen.performance_metrics import PerformanceMetricsSettings

from . import config
from .actions import ACTION_STORE
from .rules_callbacks import cb_from_rule
from .runtime_storage import runtime
from .sdk.events import STACKTRACE_EVENTS
from .signature import RSAVerifier

LOGGER = logging.getLogger(__name__)


class Command(object):
    """ Abstract command
    """

    pass


class InvalidCommand(Exception):
    """ An exception raised if a command is invalid.
    It can either doesn't contains a name attribute or no callback
    has been registered for this command.
    """

    pass


class RemoteCommand(object):
    """ Class responsible for dispatching and executing remote commands
    """

    def __init__(self):
        self.commands = {}

    def process_list(self, commands, *args, **kwargs):
        """ Process a list of command and assemble the result
        """
        res = {}

        if commands is None:
            return res

        if isinstance(commands, dict):
            LOGGER.debug(
                "Wrong commands type %s: %r", type(commands), commands
            )
            return res

        for command in commands:
            try:
                command_uuid = command["uuid"]
            except KeyError:
                LOGGER.debug("Command without uuid: %s", command)
                continue

            res[command_uuid] = self.process(command, *args, **kwargs)
        return res

    def process(self, command, *args, **kwargs):
        """ Process a single command

        Check that the command is registered first then try
        to call it with *args and **kwargs parameters
        """
        # Validate the command
        try:
            self._validate_command(command)
        except InvalidCommand as exception:
            return {"status": False, "msg": str(exception)}

        LOGGER.debug("Processing command %s", command["name"])

        # Command params
        command_params = command.get("params", [])

        # Then execute the command
        result = self.commands[command["name"]](
            *args, params=command_params, **kwargs
        )
        return self._format_result(result)

    def _validate_command(self, command):
        """ Check if the command name has been registered
        """
        command_name = command.get("name")
        if command_name not in self.commands:
            msg = "unknown command name '{}'".format(command_name)
            raise InvalidCommand(msg)

    @staticmethod
    def _format_result(result):
        """ Format the command result for the backend
        """
        if result is None:
            return {"status": False, "output": "None returned"}
        elif result is True:
            return {"status": True}
        else:
            return {"status": True, "output": result}

    def register_command(self, command_name, command):
        """ Register a command callback for command name
        """
        self.commands[command_name] = command

    @classmethod
    def with_production_commands(cls):
        """ Returns a RemoteCommand with all production commands
        already registered
        """
        remote_command = cls()

        for command_name, command in ALL_COMMANDS.items():
            remote_command.register_command(command_name, command)

        return remote_command


###
# COMMANDS DEFINITION
###


def _load_local_rules():
    config_value = config.CONFIG["RULES"]
    if not config_value:
        return []
    with open(config_value) as rules_file:
        local_rules = json.load(rules_file)
    if not isinstance(local_rules, list):  # Single rule.
        local_rules = [local_rules]
    for rule_dict in local_rules:
        rule_dict["rulespack_id"] = "local"
    return local_rules


def _load_rules(runner, params=None, check_signature=True, storage=runtime):
    """ Retrieve the rulespack and instantiate the callbacks, returns
    a list of callbacks
    """
    rulespack_id, rules = None, None
    # Try to load rules and rulespack from params
    if params:
        try:
            rulespack_id, rules = params
        except ValueError:
            pass

    if rulespack_id is None or rules is None:
        rulespack = runner.session.get_rulespack()
        if rulespack is not None:
            rulespack_id = rulespack.get("pack_id")
            rules = rulespack.get("rules", [])

    if rules is None or len(rules) == 0 or rulespack_id is None:
        return None, []

    # Set the pack id on each rule
    for rule_dict in rules:
        rule_dict["rulespack_id"] = rulespack_id

    rules.extend(_load_local_rules())

    LOGGER.info("Retrieved rulespack id: %s", rulespack_id)
    rules_name = ", ".join(rule["name"] for rule in rules)
    LOGGER.debug("Retrieved %d rules: %s", len(rules), rules_name)

    # Check the rule signature only if the config say so
    if check_signature and config.CONFIG["RULES_SIGNATURE"] is True:
        verifier = RSAVerifier()
    else:
        verifier = None

    # Create the callbacks
    callbacks = []
    for rule_dict in rules:
        # Instantiate the rule callback
        callback = cb_from_rule(rule_dict, runner, verifier, storage=storage)

        # Check if the rule has some metrics to register
        for metric in rule_dict.get("metrics", []):
            runner.metrics_store.register_metric(**metric)

        if callback:
            LOGGER.debug(
                'Rule "%s" will hook on "%s %s" with callback %s with strategy %s',
                callback.rule_name,
                callback.hook_module,
                callback.hook_name,
                callback,
                callback.strategy,
            )

            callbacks.append(callback)

    return rulespack_id, callbacks


def _instrument_callbacks(runner, callbacks):
    """ For a given list of callbacks, hook them
    """
    LOGGER.info("Setup instrumentation")
    for callback in callbacks:
        runner.instrumentation.add_callback(callback)
    runner.instrumentation.hook_all()


def instrumentation_enable(runner, params=None):
    """ Retrieve a rulespack, instantiate RuleCallback from the rules
    and instrument them.
    """
    # Load rules
    pack_id, rules = _load_rules(runner, params)

    if pack_id is None:
        LOGGER.debug("Couldn't get a valid rulespack, instrumentation is disabled")
        return None

    LOGGER.debug("Start instrumentation with rulespack_id %s", pack_id)

    # Clean existing callbacks to avoid double-instrumentation
    instrumentation_remove(runner)

    # Instrument retrieved rules
    _instrument_callbacks(runner, rules)

    return pack_id


def instrumentation_remove(runner, params=None):
    """ Remove all callbacks from instrumentation, return True
    """
    LOGGER.debug("Remove instrumentation")
    runner.instrumentation.deinstrument_all()
    ACTION_STORE.clear()
    return True


def get_bundle(runner, params=None):
    """ Returns the list of installed Python dependencies
    """

    return {"status": runner.session.post_bundle(runner.runtime_infos) is not None}


def rules_reload(runner, params=None):
    """ Load the rules, deinstrument the old ones and instrument
    the new loaded rules. Returns the new rulespack_id
    """
    LOGGER.debug("Reloading rules")
    pack_id, rules = _load_rules(runner)
    if pack_id is None:
        return ""

    # Deinstrument
    instrumentation_remove(runner)

    # Reinstrument new ones
    _instrument_callbacks(runner, rules)

    LOGGER.debug("Rules reloaded")
    return pack_id


def actions_reload(runner, params=None):
    """Remove old security actions and load the new ones."""
    LOGGER.debug("Reloading actions")
    data = runner.session.get_actionspack()
    if data["status"] is not True:
        LOGGER.debug("Cannot reload actions")
        return ""

    actions = data["actions"]
    LOGGER.debug("Reloading actions %s", actions)

    unsupported = ACTION_STORE.reload_from_dicts(actions or [])
    if unsupported:
        return {
            "status": False,
            "output": {"unsupported_actions": unsupported},
        }
    else:
        return {"status": True}


def record_stacktrace(runner, params=None):
    """Collect stacktraces for the given events."""
    STACKTRACE_EVENTS.clear()
    if params:
        LOGGER.debug("Collect stacktraces for events %r", params)
        STACKTRACE_EVENTS.update(params)
    else:
        LOGGER.debug("Don't collect any stacktrace event")
    return {"status": True}


def features_get(runner, params=None):
    return runner.features_get()


def features_change(runner, params):

    old_features = copy(runner.features_get())

    if len(params) != 1:
        raise ValueError("Invalid params list %s" % params)
    params = params[0]

    runner.set_performance_metrics_settings(
        PerformanceMetricsSettings.from_features(params))

    # Heartbeat delay only if we have a new value for it > 0
    heartbeat_delay = params.get("heartbeat_delay", 0)
    if heartbeat_delay > 0:
        runner.set_heartbeat_delay(heartbeat_delay)

    # Always set the new value of call_counts_metrics_period
    runner.set_call_counts_metrics_period(
        params.get("call_counts_metrics_period", 60)
    )

    # Always set the new value of whitelisted_metric
    runner.set_whitelisted_metric(params.get("whitelisted_metric", True))

    # Alter the deliverer if the batch_size is set
    if params.get("batch_size") is not None:
        runner.set_deliverer(
            params["batch_size"], params.get("max_staleness", 0)
        )

    new_features = copy(runner.features_get())

    return {"old": old_features, "now": new_features}


def performance_budget(runner, params):
    old_value = runner.budget_in_ms

    if len(params) == 0:
        params = [0]
    elif len(params) > 1:
        raise ValueError("Expected 1 or 0 items in list %s" % params)

    param = params[0]

    if param == 0 or param is None:
        runner.budget_in_ms = None
    else:
        runner.budget_in_ms = param + 0

    return {
        "status": True,
        "output": {"was": old_value}
    }


def ips_whitelist(runner, params):
    """ Replace current list of whitelisted IP networks
    """
    params = params[0]
    runner.set_ips_whitelist(params)
    return {"status": True}


def paths_whitelist(runner, params):
    """ Replace current list of whitelisted paths
    """
    params = params[0]

    runner.set_paths_whitelist(params)
    return {"status": True}


def force_logout(runner, params=None):
    instrumentation_remove(runner)
    runner.logout()
    return {"status": True}


ALL_COMMANDS = {
    "instrumentation_enable": instrumentation_enable,
    "instrumentation_remove": instrumentation_remove,
    "get_bundle": get_bundle,
    "rules_reload": rules_reload,
    "features_get": features_get,
    "features_change": features_change,
    "ips_whitelist": ips_whitelist,
    "paths_whitelist": paths_whitelist,
    "force_logout": force_logout,
    "actions_reload": actions_reload,
    "record_stacktrace": record_stacktrace,
}
