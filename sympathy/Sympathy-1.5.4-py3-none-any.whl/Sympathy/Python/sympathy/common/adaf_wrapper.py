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
"""
This module contains classes that wrap ADAFs or lists of ADAFs for use in
various function selector, F(x), nodes in Sympathy for Data.
"""
import numpy as np

from sympathy.platform import exceptions as syexceptions
from sympathy.api import adaf  # NOQA
from .. utils.context import deprecated_method
from . import fx_wrapper


class ADAFWrapper(fx_wrapper.FxWrapper):
    """
    ADAFWrapper should be used as the parent class for classes to be used
    in the ADAF F(x) nodes.
    """
    arg_types = ['adaf']
    list_wrapper = False

    def __init__(self, in_adaf, out_adaf, extra_table=None):
        self.required_signals = []
        self.in_adaf = in_adaf
        self.out_adaf = out_adaf
        self.extra_table = extra_table

    def execute(self):
        """Execute is called from the F(x) node."""
        raise syexceptions.SyConfigurationError(
            "This f(x) script doesn't implement an execute method.")

    @deprecated_method('1.5.0', "self.out_adaf.meta.create_column")
    def write_meta(self, name, data, description='', unit='', **kwargs):
        """Write meta data."""
        attributes = {'description': description, 'unit': unit}
        attributes.update(kwargs)
        self.out_adaf.meta.create_column(name, np.array(data), attributes)

    @deprecated_method('1.5.0', "self.out_adaf.res.create_column")
    def write_results(self, name, data, description='', unit='', **kwargs):
        """Results meta data."""
        attributes = {'description': description, 'unit': unit}
        attributes.update(kwargs)
        self.out_adaf.res.create_column(name, np.array(data), attributes)

    @deprecated_method('1.5.0',)
    def update_results(self, name, indexes, data):
        """Update existing result using index array."""
        self.out_adaf.res[name][indexes] = np.array(data)

    @deprecated_method('1.5.0', "self.in_adaf.meta['...']")
    def meta(self, name):
        """Return the meta data column 'name'."""
        return self.in_adaf.meta[name]

    @deprecated_method('1.5.0', "self.in_adaf.res['...']")
    def results(self, name):
        """Return the results column 'name'"""
        return self.in_adaf.res[name]

    @deprecated_method('1.5.0', "self.in_adaf.meta")
    def meta_datagroup(self):
        """Return the complete meta data table"""
        return self.in_adaf.meta

    @deprecated_method('1.5.0', "self.in_adaf.res")
    def result_datagroup(self):
        """Return the complete result data table"""
        return self.in_adaf.res

    @deprecated_method('1.5.0', "self.in_adaf.ts['...']")
    def signals(self, name):
        """Return the signal 'name'"""
        signals = []
        try:
            signal = self.in_adaf.ts[name]
            signals.append(signal)
        except:
            signals.append(None)
        return signals

    @deprecated_method('1.5.0', "self.in_adaf.package_id()")
    def package_id(self):
        "Get the package identifier string."
        return self.in_adaf.package_id()

    @deprecated_method('1.5.0', "self.in_adaf.source_id()")
    def source_id(self):
        "Get the source identifier string."
        return self.in_adaf.source_id()

    @deprecated_method('1.5.0', "self.in_adaf.timestamp()")
    def timestamp(self):
        "Get the time string."
        return self.in_adaf.timestamp()

    @deprecated_method('1.5.0', "self.in_adaf.user_id()")
    def user_id(self):
        """Get the user identifier string."""
        return self.in_adaf.user_id()

    @deprecated_method('1.5.0')
    def _required_signals_exist(self):
        """
        Check that the input file contains all signals in self.required_signals
        """
        if set(self.required_signals) - set(self.in_adaf.ts.keys()):
            return False
        else:
            return True


class ADAFsWrapper(ADAFWrapper):
    """ADAFsWrapper should be used as the parent class for classes to be used
    in the ADAFs F(x) nodes.

    Interact with the tables through in_table_list and out_table_list.
    """
    arg_types = ['[adaf]']
    list_wrapper = True

    def __init__(self, in_adaf, out_adaf, extra_table=None):
        super(ADAFsWrapper, self).__init__(in_adaf, out_adaf, extra_table)
        self.in_adaf_list = in_adaf
        self.out_adaf_list = out_adaf


class ADAFToTableWrapper(ADAFWrapper):
    """ADAFsToTablesWrapper should be used as the parent class for classes to
    be used in the ADAFs to Tables F(x) nodes.

    Interact with the files through in_adaf_list and out_table_list.
    """

    def __init__(self, in_adaf, out_table, extra_table=None):
        super(ADAFToTableWrapper, self).__init__(in_adaf, out_table,
                                                 extra_table)
        self.out_table = out_table


class ADAFsToTablesWrapper(ADAFToTableWrapper):
    """ADAFsToTablesWrapper should be used as the parent class for classes to
    be used in the ADAFs to Tables F(x) nodes.

    Interact with the files through in_adaf_list and out_table_list.
    """
    list_wrapper = True

    def __init__(self, in_adaf, out_table, extra_table=None):
        super(ADAFsToTablesWrapper, self).__init__(in_adaf, out_table,
                                                   extra_table)
        self.in_adaf_list = in_adaf
        self.out_table_list = out_table
