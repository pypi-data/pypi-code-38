# -*- coding: utf-8 -*-
"""This module has functions to log into a custom logger called alluretestlogger in the testlogger variable"""
from __future__ import print_function
from __future__ import unicode_literals
from __future__ import division
from __future__ import absolute_import
from builtins import str
from builtins import range
from future import standard_library
standard_library.install_aliases()
import logging
from typhoon.utils import PY2


testlogger = logging.getLogger('alluretestlogger')
testlogger.propagate = False
testlogger.indentation = 0


class IndentationFilter(logging.Filter):
    def filter(self, record):
        record.indentation = "".join([" " for _ in range(testlogger.indentation)])
        return True


testlogger.addFilter(IndentationFilter())


def _format_argval(argval):
    """Remove newlines and limit max length"""
    max_arg_length = 100
    argval = argval.replace("\n", " ")
    if len(argval) > max_arg_length:
        argval = argval[:3]+" ... "+argval[-max_arg_length:]
    return argval


def log(msg):
    testlogger.info(msg)


def start_step(title, params):
    step_prefix = "> "
    title = "{}{}".format(step_prefix, title)

    testlogger.info(title)

    step_spacing = "".join([" " for _ in range(len(step_prefix))])  # whitespaces
    if params:
        param_list = list(params.items())
        for arg_name, arg_val in param_list:
            icon = "└" if arg_name == param_list[-1][0] else "├"  # Different icon if is last argument
            if PY2:
                # python 2 compat
                arg_val = str(arg_val, encoding='utf-8')
            testlogger.info("{}  {}- {} = {}".format(step_spacing, icon, arg_name, arg_val))

    testlogger.indentation += 4


def stop_step():
    testlogger.indentation -= 4


def start_fixture(fixture_name):
    testlogger.info("[Fixture] {}".format(fixture_name))
    testlogger.indentation += 4


def stop_fixture():
    testlogger.indentation -= 4
