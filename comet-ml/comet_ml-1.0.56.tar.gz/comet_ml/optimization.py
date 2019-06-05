# -*- coding: utf-8 -*-
# *******************************************************
#   ____                     _               _
#  / ___|___  _ __ ___   ___| |_   _ __ ___ | |
# | |   / _ \| '_ ` _ \ / _ \ __| | '_ ` _ \| |
# | |__| (_) | | | | | |  __/ |_ _| | | | | | |
#  \____\___/|_| |_| |_|\___|\__(_)_| |_| |_|_|
#
#  Sign up for free at http://www.comet.ml
#  Copyright (C) 2015-2019 Comet ML INC
#  This file can not be copied and/or distributed without the express
#  permission of Comet ML Inc.
# *******************************************************
#
"""
Author: Boris Feld

This module contains the various helpers for the Optimization API
"""
import logging
import string

from comet_ml.config import get_global_experiment

from ._logging import CASTING_ERROR_MESSAGE
from .exceptions import OptimizationMissingExperiment, PCSCastingError, PCSParsingError

LOGGER = logging.getLogger(__name__)


class Suggestion(object):
    """ A suggestion is a single proposition of hyper-parameters values.

    You can use it like a dict:

    ```python
    suggestion["x"] # Returns the value for hyper-parameter x
    ```

    Suggestion is automatically casting values for hyper-parameter declared as
    `integer` or `real`. It will returns `int` for `integer` and `float` for
    `real`. For `categorical` and `ordinal`, it will returns `str`.

    In case casting is failing, it will print a warning message and return a `str`.

    For accessing the raw value without casting, you can use the `raw` method:

    ```python
    suggestion.raw("x") # Always returns a str
    ```
    """

    def __init__(self, suggestion, optimizer, types):
        """ You shouldn't directly instantiate Suggestion objects, use
        [Optimizer.get_suggestion](../Optimizer/#optimizerget_suggestion)
        instead.
        """
        self.suggestion = suggestion
        self.run_id = suggestion["run_id"]
        self.params = suggestion["params"]
        self.optimizer = optimizer
        self.types = types

    def __iter__(self):
        return iter(self.params)

    def __getitem__(self, name):
        """ Return the casted value for this hyper-parameter.
        Args:
            name: The hyper-parameter name
        """
        raw_value = self.params[name]
        try:
            return cast_parameter(raw_value, self.types[name])
        except (KeyError, PCSCastingError):
            LOGGER.warning(CASTING_ERROR_MESSAGE, name, name, name)
            return self.raw(name)

    def raw(self, name):
        """ Return the raw not-casted value for this hyper-parameter.
        Args:
            name: The hyper-parameter name
        """
        return self.params[name]

    def report_score(self, name, score):
        """ Send back the score for this suggestion.
        Args:
            score: A float representing the score
        """
        self._report_params_to_experiment(self.params, name, score)

        self.optimizer._report_score(self.run_id, score)

    def _report_params_to_experiment(self, suggestion, name, score):
        if get_global_experiment() is None:
            raise OptimizationMissingExperiment

        exp = get_global_experiment()

        exp.log_parameters(suggestion)
        exp.log_metric(name, score)


PCS_TYPES = {"integer", "real", "ordinal", "categorical"}


def parse_pcs(pcs_content):
    parsed = {}
    for line in pcs_content.splitlines():
        # Clean line
        line = line.strip()

        # Ignore empty lines
        if line == "":
            continue

        # Ignore commented lines
        if line.startswith("#"):
            continue

        # Ignore conditions as they doesn't influence parameters type
        if "|" in line:
            continue

        # Ignore forbidden parameter syntax
        if line.startswith("{") and line.endswith("}"):
            continue

        # Check that the line looks valid
        if "}" not in line and "]" not in line:
            raise PCSParsingError("missing ending bracket: " + line)

        splitted = parse_pcs_line(line)

        param_name = splitted[0]
        param_type = splitted[1]

        parsed[param_name] = param_type

    return parsed


def parse_pcs_line(line):
    """
    Parse a single PCS line, and check syntax.

    Can be one of the following:

    1. parameter_name categorical {value_1, ..., value_N} [default value]
    2. parameter_name ordinal {value_1, ..., value_N} [default value]
    3. parameter_name integer [min_value, max_value] [default value]
    4. parameter_name integer [min_value, max_value] [default value] log
    5. parameter_name real [min_value, max_value] [default value]
    6. parameter_name real [min_value, max_value] [default value] log
    """
    parts = []
    state = "in value"
    stack = []
    current = ""
    for i in range(len(line)):
        ch = line[i]
        ## whitespace
        if ch in [" ", "\t"]:
            if current != "":
                if state == "in stack":
                    stack.append(current)
                elif state == "in value":
                    parts.append(current)
                current = ""
            else:
                ## skip whitespace
                continue
        elif ch == ",":
            if state == "in stack":
                if current == "":
                    raise PCSParsingError("comma without item: " + line)
                else:
                    stack.append(current)
                    current = ""
            else:
                raise PCSParsingError("comma outside of list: " + line)
        elif ch in "[{":
            if state == "in stack":
                raise PCSParsingError("nested lists: " + line)
            elif current:
                parts.append(current)
                current = ""
            state = "in stack"
        elif ch in "]}":
            if state == "in stack":
                if current:
                    stack.append(current)
                    current = ""
                if stack != []:
                    parts.append(stack)
            else:
                raise PCSParsingError("invalid closing bracket: " + line)
            state = "in value"
            stack = []
        elif ch in string.ascii_letters + "_-.()@:" + string.digits:
            current += ch
        else:
            raise PCSParsingError(("invalid character '%s': " % (ch,)) + line)
    if state == "in stack":
        raise PCSParsingError("missing ending bracket: " + line)
    if current != "":
        parts.append(current)
    if stack != []:
        parts.append(stack)
    ## name, type, range[, default, log]
    if len(parts) < 2:
        raise PCSParsingError("invalid pcs format: " + line)
    if not isinstance(parts[1], str) or parts[1] not in PCS_TYPES:
        raise PCSParsingError(("invalid type '%s': " % (parts[1],)) + line)
    # parameter_name real [min_value, max_value] [default value] log
    if len(parts) >= 3:
        ## try casting each value, result is ignored. Just used
        ## for it's side effect of raising errors:
        _ = [cast_parameter(value, parts[1]) for value in parts[2]]
    if len(parts) >= 4:
        ## try casting default:
        default = cast_parameter(parts[3][0], parts[1])
        ## make sure default is in range
        ## can be categorical/ordinal or integer/real
        if parts[1] in ["categorical", "ordinal"]:
            if parts[3][0] not in parts[2]:
                raise PCSParsingError("categorical default not in categories: " + line)
        elif not (
            cast_parameter(parts[2][0], parts[1])
            <= default
            <= cast_parameter(parts[2][1], parts[1])
        ):
            # real or integer
            raise PCSParsingError("default is not in range: " + line)
    if len(parts) == 5:
        if parts[4] != "log":
            raise PCSParsingError("optional fifth item must be 'log': " + line)
    if len(parts) > 5:
        raise PCSParsingError("too many items on line: " + line)
    ## return parts as string:
    return [str(part) for part in parts]


def cast_parameter(value, pcs_type):
    if pcs_type not in PCS_TYPES:
        raise PCSCastingError(value, pcs_type)

    if pcs_type == "integer":
        try:
            return int(value)
        except ValueError:
            raise PCSCastingError(value, pcs_type)
    elif pcs_type == "real":
        try:
            return float(value)
        except ValueError:
            raise PCSCastingError(value, pcs_type)
    elif pcs_type == "categorical":
        try:
            return int(value)
        except ValueError:
            pass

        try:
            return float(value)
        except ValueError:
            pass

        try:
            return _str_to_bool(value)
        except ValueError:
            pass

    return value


def _str_to_bool(s):
    s = s.lower()
    if s == "true":
        return True
    elif s == "false":
        return False
    else:
        raise ValueError()
