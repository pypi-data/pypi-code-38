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
from __future__ import (print_function, division, unicode_literals,
                        absolute_import)
import warnings

# Ignore a warning from numpy>=1.14 when importing h5py<=2.7.1:
with warnings.catch_warnings():
    warnings.simplefilter('ignore')
    import h5py

from sympathy.api import importers
from sympathy.api import table


def all_equal(iterator):
    try:
        iterator = iter(iterator)
        first = next(iterator)
        return all(first == rest for rest in iterator)
    except StopIteration:
        return True


class DataImportTable(importers.TableDataImporterBase):
    """Importer for Table files."""
    IMPORTER_NAME = "Table"
    DISPLAY_NAME = 'SyData'

    def __init__(self, fq_infilename, parameters):
        super(DataImportTable, self).__init__(fq_infilename, parameters)

    def name(self):
        return self.IMPORTER_NAME

    def valid_for_file(self):
        """Is fq_filename a valid Table."""
        try:
            can_open_hdf5 = h5py.is_hdf5(self._fq_infilename)
        except Exception:
            can_open_hdf5 = False

        if can_open_hdf5:
            if self.is_type():
                return True
            valid = True
            # Fallback method of determining if the data can be considered a
            # table by data inspection. Can be useful for reading data from
            # other programs that have the right form.
            with h5py.File(self._fq_infilename, 'r') as infile:
                # Filter reserved items
                items = [infile[name] for name in infile
                         if not name.startswith('__sy_')]
                # All remaining items must be datasets.
                valid &= all([isinstance(ds, h5py.Dataset) for ds in items])

                # All datasets must have the same length.
                valid &= all_equal([len(ds) for ds in items])
            return valid
        return False

    def is_type(self):
        if not table.is_table('hdf5', self._fq_infilename):
            return False
        return True
