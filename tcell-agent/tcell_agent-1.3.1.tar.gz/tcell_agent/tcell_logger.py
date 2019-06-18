# Copyright (C) 2015 tCell.io, Inc. - All Rights Reserved

from __future__ import unicode_literals


_NATIVE_AGENT = None


# Note: have an external class (TCellAgent) set the native
#       agent here instead of this module creating the
#       native agent to avoid cyclical dependencies.
def set_native_agent(native_agent):
    global _NATIVE_AGENT  # pylint: disable=global-statement
    _NATIVE_AGENT = native_agent


def get_module_logger(module_name):
    return _NATIVE_AGENT.get_module_logger(module_name)
