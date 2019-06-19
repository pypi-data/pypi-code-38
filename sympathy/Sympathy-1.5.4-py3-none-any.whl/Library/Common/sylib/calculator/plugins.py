# -*- coding:utf-8 -*-
# Copyright (c) 2017, Combine Control Systems AB
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Combine Control Systems AB nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.
# IN NO EVENT SHALL COMBINE CONTROL SYSTEMS AB BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
from sympathy.utils.components import get_components


class ICalcPlugin(object):
    """Interface for calculator plugins."""

    WEIGHT = 10000

    @staticmethod
    def gui_dict(generic):
        """
        Return a dictionary with functions that will be shown in the
        configuration gui for the calculator node.
        """
        return {}

    @staticmethod
    def globals_dict():
        """
        Return a dictionary that will be added to the globals dictionary
        when executing calculations.
        """
        return {}

    @staticmethod
    def imports():
        """
        Return a dictionary with extra imports that will be available in
        the calculator.
        For example, add the imports::

            import math
            import scipy.integrate
            import scipy.signal as sig

        to your plugin, and return a dictionary like this::

            return {'math': math,
                    'spint': scipy.integrate,
                    'sig': sig}

        and math, spint and sig will be available as modules in the calculator.
        """
        return {}

    @staticmethod
    def signals_dict():
        """
        Define signals that are needed to run the functions as written in
        eval texts, when running the tests.
        Must have the same length.
        """
        return {}

    @staticmethod
    def variables_dict():
        """
        Define variables that are needed to run the functions as written in
        eval texts, when running the tests.
        """
        return {}

    @staticmethod
    def hidden_items():
        """
        Reimplement this to hide some elements from other plugins.

        The hidden functions will still be available, but won't show up in the
        list of common functions in the calculator gui.

        The returned value should be a list of tuples with the "paths" in the
        gui_dict that should be hidden. E.g. ``[("Event detection",)]`` will
        hide the entire event detection subtree, while ``[("Event detection",
        "Changed")]`` will hide the function called "Changed" under "Event
        detection".
        """
        return []


class MatlabCalcPlugin(object):
    """Interface for calculator plugins."""

    WEIGHT = 10000

    @staticmethod
    def gui_dict(generic):
        """
        Return a dictionary with functions that will be shown in the
        configuration gui for the calculator node.
        """
        return {}

    @staticmethod
    def globals_dict():
        """
        Return a dictionary that will be added to the globals dictionary
        when executing calculations.
        """
        return {}


def available_plugins(backend='python'):
    """Return all available plugins derived for a specific backend."""
    plugin_classes = {'python': ICalcPlugin,
                      'matlab': MatlabCalcPlugin}
    return get_components('plugin_*.py', plugin_classes[backend])


class PluginWrapper(object):
    """
    Merge two or more module-like objects into one.

    getattr calls on PluginWrapper objects are passed on to the module-like
    objects and the first one which doesn't raise AttributeError gets to return
    its result.
    """

    def __init__(self, *namespaces):
        self._namespaces = list(namespaces)

    def __getattr__(self, attr):
        for ns in self._namespaces:
            try:
                return getattr(ns, attr)
            except AttributeError:
                pass

        raise AttributeError(attr)
