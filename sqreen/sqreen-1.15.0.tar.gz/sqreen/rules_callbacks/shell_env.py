# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, 2018, 2019 Sqreen. All rights reserved.
# Please refer to our terms for more information:
#
#     https://www.sqreen.io/terms.html
#
""" Look for injected shell vars
"""
import os
from collections import Mapping
from logging import getLogger

from ..utils import is_string
from .regexp_rule import RegexpRule

LOGGER = getLogger(__name__)


class ShellEnvCB(RegexpRule):
    def pre(self, original, *args, **kwargs):
        """
        Examine environment variables to find shellshock injections.
        Works if env is passed in positional or keyword argument.
        """

        environ = kwargs.get("env")
        if not environ:
            # position based on
            # https://docs.python.org/3.6/library/subprocess.html#popen-constructor
            if len(args) >= 11:
                environ = args[10]

        if not environ:
            environ = os.environ

        if not isinstance(environ, (dict, Mapping)):
            return

        found, var = None, None
        for var, val in environ.items():
            if is_string(val):
                found = self.match_regexp(val)
                if found:
                    break

        if not found:
            return

        infos = {"variable_name": var, "variable_value": val, "found": found}
        self.record_attack(infos)

        return {"status": "raise", "data": found, "rule_name": self.rule_name}
