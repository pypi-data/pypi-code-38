# Copyright (c) 2013, Combine Control Systems AB
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
import collections

from sylib.calculator import plugins
from sylib.calculator.std_plugin import (
    basics, logics, event_detection, plugin_matlab)
import numpy as np


class StdPlugin(plugins.ICalcPlugin):
    """Standard plugin for calculator node."""

    # This plugin should be listed first:
    WEIGHT = -1

    @staticmethod
    def gui_dict():
        gui_dict = collections.OrderedDict()
        gui_dict.update(basics.GUI_DICT)
        gui_dict.update(logics.GUI_DICT)
        gui_dict.update(event_detection.GUI_DICT)
        return gui_dict

    @staticmethod
    def globals_dict():
        return {'ca': plugins.PluginWrapper(basics.LogicOperator,
                                            basics.Statistics,
                                            logics.Logics,
                                            event_detection.EventDetection)}

    @staticmethod
    def signals_dict():
        return {
            'signal0': np.array([1, 1, 1, 0, 0]),
            'signal1': np.array([1, 1, 1, 2, 2]),
            'time': np.array([0, 1, 2, 3, 4])}

    @staticmethod
    def variables_dict():
        return {
            'value': 1,
            'shift_value': 1,
            'start_shift': 1,
            'end_shift': 1,
            'length': 10,
            'signal_mask': np.array([[0, 2], [5, 9]])}


class MatlabPlugin(plugins.MatlabCalcPlugin):
    """Standard plugin for calculator node."""

    # This plugin should be listed first:
    WEIGHT = -1

    @staticmethod
    def gui_dict():
        gui_dict = collections.OrderedDict()
        gui_dict.update(plugin_matlab.GUI_DICT)

        return gui_dict

    @staticmethod
    def globals_dict():
        return {'ca': plugins.PluginWrapper(plugin_matlab.GUI_DICT)}
