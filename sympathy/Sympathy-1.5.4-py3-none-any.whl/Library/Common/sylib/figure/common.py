# Copyright (c) 2016, Combine Control Systems AB
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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)

import six
from matplotlib import colors as mpl_colors

from sylib.figure import colors
from sylib.util import base_eval


REPLACE_AXIS_TYPE = {'x': 'bottom',
                     'x1': 'bottom',
                     'x2': 'top',
                     'y': 'left',
                     'y1': 'left',
                     'y2': 'right'}


def parsing_context(data_table):
    context = {'table': data_table, 'arg': data_table}
    return context

def parse_value(text, data_table, extra_vars=None):
    """
    Evaluate expression in a limited python environment.

    If evaluation fails, the input text will be returned as
    ``unicode``.

    Parameters
    ----------
    text : unicode or str
    data_table : sympathy.api.table.File
    extra_vars : dict, optional

    Returns
    -------
    Returns the evaluated text.
    """
    context = parsing_context(data_table)
    if extra_vars:
        context.update(extra_vars)
    try:
        parsed_value = base_eval(six.text_type(text), context)
    except (NameError, SyntaxError):
        parsed_value = six.text_type(text)
    return parsed_value


def verify_options(value, options):
    """Check if value is within the options."""
    if value in options:
        return value
    return None


def parse_type(value, t, options=None):
    if t == 'colortype':
        if (colors.get_color_dev(value) in ['rgb', 'rgba', 'rgbF', 'rgbaF'] or
                mpl_colors.is_color_like(value)):
            return value
        else:
            # TODO: add some validation for python expressions
            return value
    elif t == 'options':
        return verify_options(six.text_type(value), options)
    elif t == 'axesposition':
        if value in REPLACE_AXIS_TYPE.keys():
            value = REPLACE_AXIS_TYPE[value]
        return verify_options(value, options)
    else:
        return t(value)
