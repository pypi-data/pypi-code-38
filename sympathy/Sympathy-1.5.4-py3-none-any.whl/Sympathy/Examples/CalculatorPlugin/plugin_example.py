# Copyright (c) 2018, Combine Control Systems AB
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
"""
A short example of how to make a calculator plugin. Put a copy of this file
in your library's package folder in Common, and it will be imported
automatically. The file name must start with 'plugin_'.
"""
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
from sylib.calculator import plugins
import collections
import inspect
import numpy as np

PLUGIN_ID = 'custom_plugin'   # Will be used as a namespace for the functions.
PLUGIN_NAME = 'CustomPlugin'  # The displayed name in the Calculator node.


class Section1(object):

    @staticmethod
    def example_function1(signal1, signal2):
        """Add two signals element by element.

        **Parameters**
            signal1: np.array
                The first signal.
            signal2: np.array
                The second signal

        **Returns**
            np.array
                The sum of the signals
        """
        return signal1 + signal2

    @staticmethod
    def example_function2(signal1, signal2):
        """Subtract two signals element by element.

        **Parameters**
            signal1: np.array
                The first signal.
            signal2: np.array
                The second signal

        **Returns**
            np.array
                The difference of the signals
        """
        return signal1 - signal2


class Section2(object):

    @staticmethod
    def example_function3(signal1, constant):
        """Add a constant to each element.

        **Parameters**
            signal1: np.array
                The first signal.
            signal2: np.array
                The second signal

        **Returns**
            np.array
                The sum of the signals
        """
        return signal1 + constant


SECTION1 = [
    (
        # Set a display name for the function
        "Example Function 1",
        # This is what will be put in the calculator window
        # if signal1 and signal 2 are defined in the class CustomPlugin,
        # this line can be run as a test
        PLUGIN_ID + ".example_function1(arg['signal1'], arg['signal2'])",
        # This fetches the documentation so that it can be shown on mouse over
        inspect.getdoc(Section1.example_function1)
    ),
    (
        "Example Function 2",
        PLUGIN_ID + ".example_function2(arg['signal1'], arg['signal2'])",
        inspect.getdoc(Section1.example_function2)
    )
]

SECTION2 = [
    (
        "Example Function 3",
        PLUGIN_ID + ".example_function3(arg['signal1'], value)",
        inspect.getdoc(Section2.example_function3)
    )
]

# CustomPlugin is the name that will be displayed in the Calculator.
# An ordered dict is used so that the sections are displayed in given order
GUI_DICT = {
    PLUGIN_NAME: collections.OrderedDict([
        ("Section1", SECTION1),
        ("Section2", SECTION2)])
}


class CustomPlugin(plugins.ICalcPlugin):
    """Custom plugin for calculator node. Wraps the above into something
    the Calculator can import.
    """

    # Can be used to set the position of the plugin in the Calculator GUI.
    # A higher value indicates a higher position.
    WEIGHT = 0

    @staticmethod
    def gui_dict():
        """This method does not require any user changes by default"""
        gui_dict = collections.OrderedDict()
        gui_dict.update(GUI_DICT)
        return gui_dict

    @staticmethod
    def globals_dict():
        """Add your classes here"""
        return {PLUGIN_ID: plugins.PluginWrapper(Section1, Section2)}

    @staticmethod
    def signals_dict():
        """Define signals that are needed to run the functions as written in
        eval texts, when running the tests.
        Must have the same length.
        """
        return {
            'signal1': np.array([1, 2, 3, 4, 5]),
            'signal2': np.array([1, 2, 3, 4, 5])}

    @staticmethod
    def variables_dict():
        """Define variables that are needed to run the functions as written in
        eval texts, when running the tests.
        """
        return {
            'value': 0}
