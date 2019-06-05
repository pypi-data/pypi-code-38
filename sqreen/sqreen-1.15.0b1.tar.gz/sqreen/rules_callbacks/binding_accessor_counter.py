# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Count things according to a list of binding accessors expression
"""
import json
import logging
from collections import Mapping

from ..binding_accessor import BindingAccessor
from ..exceptions import InvalidArgument
from ..rules import RuleCallback

LOGGER = logging.getLogger(__name__)


class BindingAccessorCounter(RuleCallback):
    def __init__(self, *args, **kwargs):
        super(BindingAccessorCounter, self).__init__(*args, **kwargs)

        if not isinstance(self.data, Mapping):
            msg = "Invalid data type received: {}"
            raise InvalidArgument(msg.format(type(self.data)))

        self.patterns = [BindingAccessor(exp) for exp in self.data["values"]]
        self.metric_name = self.metrics[0]["name"]

    def post(self, original, response, *args, **kwargs):
        """ Resolve binding expressions with the HTTP Response and send
        an observation for the rule metric.
        """
        request = self.storage.get_current_request()

        binding_eval_args = {
            "binding": locals(),
            "global_binding": globals(),
            "framework": request,
            "instance": original,
            "arguments": self.storage.get_current_args(args),
            "kwarguments": kwargs,
            "cbdata": self.data,
            "return_value": response,
        }

        key = [
            binding.resolve(**binding_eval_args) for binding in self.patterns
        ]
        formatted_key = json.dumps(key, separators=(",", ":"))
        self.record_observation(self.metric_name, formatted_key, 1)

        return {}

    def failing(self, original, *args, **kwargs):
        """ Resolve binding expressions with the exception, replace the status
        code with 500 and send an observation for the rule metric.
        """
        request = self.storage.get_current_request()

        binding_eval_args = {
            "binding": locals(),
            "global_binding": globals(),
            "framework": request,
            "instance": original,
            "arguments": self.storage.get_current_args(args),
            "kwarguments": kwargs,
            "cbdata": self.data,
            "return_value": None,
        }

        key = []
        for binding in self.patterns:

            # Replace status code replacement by 500 as we don't have a response
            if binding.expression.endswith(
                ".status_code"
            ) or binding.expression.endswith(".status"):
                key.append(500)
                continue

            key.append(binding.resolve(**binding_eval_args))
        formatted_key = json.dumps(key, separators=(",", ":"))

        self.record_observation(self.metric_name, formatted_key, 1)

        return {}
