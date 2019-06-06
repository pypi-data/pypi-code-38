# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Abstract callback for checking regex against request fields
"""

from collections import Mapping
from logging import getLogger

from ..binding_accessor import BindingAccessor
from ..exceptions import InvalidArgument
from ..matcher import Matcher
from ..rules import RuleCallback
from ..utils import is_string

LOGGER = getLogger(__name__)


class BindingAccessorMatcherCallback(RuleCallback):
    MAX_LEN = 1024 * 128

    def __init__(self, *args, **kwargs):
        super(BindingAccessorMatcherCallback, self).__init__(*args, **kwargs)

        if not isinstance(self.data, Mapping):
            msg = "Invalid data type received: {}"
            raise InvalidArgument(msg.format(type(self.data)))

        try:
            self.values = self.data["values"]
        except KeyError:
            msg = "No key 'values' in data (had {})"
            raise InvalidArgument(msg.format(self.data.keys()))

        self.patterns = None

    def _prepare_patterns(self):
        """ Prepare patterns if not ready
        """
        patterns = []

        ba_cache = {}

        def cached_binding_accessor(expression):
            if expression in ba_cache:
                return ba_cache[expression]
            else:
                binding_accessor = BindingAccessor(expression)
                ba_cache[expression] = binding_accessor
                return binding_accessor

        try:
            for value in self.values:

                bindings = [
                    cached_binding_accessor(ba)
                    for ba in value["binding_accessor"]
                ]

                patterns.append(
                    {
                        "id": value["id"],
                        "binding_accessor": bindings,
                        "matcher": Matcher([value["matcher"]]),
                    }
                )
        finally:
            self.patterns = patterns

    def pre(self, original, *args, **kwargs):
        request = self.storage.get_current_request()

        if not request:
            LOGGER.warning("No request was recorded abort")
            return

        # Only compile patterns if we need them
        if self.patterns is None:
            self._prepare_patterns()

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

        cache = {}
        for pattern in self.patterns:
            for binding_accessor in pattern["binding_accessor"]:
                expression = binding_accessor.expression

                if expression in cache:
                    data = cache[expression]
                else:
                    data = binding_accessor.resolve(**binding_eval_args)

                    # Convert string to list
                    if data is None or is_string(data):
                        data = [data]

                    # Ignore not string values as we use a string matcher
                    # that only match strings
                    data = [elem for elem in data if is_string(elem)]

                    cache[expression] = data

                if not data:
                    continue

                for elem in data:
                    if len(elem) > self.MAX_LEN:
                        continue

                    if pattern["matcher"].match(elem):
                        infos = {
                            "id": pattern["id"],
                            "binding_accessor": expression,
                            "matcher": pattern["matcher"].patterns,
                            "found": elem,
                        }
                        self.record_attack(infos)

                        # Potentially raise an attack
                        return {
                            "status": "raise",
                            "data": elem,
                            "rule_name": self.rule_name,
                        }
