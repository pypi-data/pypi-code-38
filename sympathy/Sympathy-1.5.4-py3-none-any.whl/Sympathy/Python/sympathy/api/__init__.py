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
"""The Sympathy for Data API."""

# Node API, for implementing library modules.
from .. platform import gennode as node

# Node parameter API, for accessing fields and building the structure.
# Also available from node.parameters
from .. utils.parameter_helper import ParameterRoot as parameters
from .. utils.parameter_helper_gui import ParameterView

# Data type utility modules.
from .. typeutils import adaf
from .. typeutils import datasource
from .. typeutils import table
from .. typeutils import text
from .. typeutils import report
from .. typeutils import figure
from .. typeutils import json

# Data type utility wrapper modules.
from .. common import adaf_wrapper
from .. common import table_wrapper
from .. common import fx_wrapper

# For defining Data type utility modules.
from .. import types

# For using QT (to create GUI:s, etc.). Use this to ensure compatibility
from .. platform import qt_compat as qt

# Node generator functions
from .. utils import node_helper

# Helper functions for working with numpy dtypes
from .. utils import dtypes


__all__ = ['node', 'parameters', 'ParameterView', 'adaf', 'datasource',
           'table', 'text', 'report', 'figure', 'json', 'adaf_wrapper',
           'table_wrapper', 'fx_wrapper', 'types',
           'qt', 'node_helper', 'dtypes']
