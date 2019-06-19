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
import re
import time
import os

from sympathy.api import importers
from sympathy.api import table
from sympathy.api.exceptions import SyDataError
from sylib.table_sources import ImporterCSV, TableSourceCSV


CHECK_NO_ROWS = 1
CHECK_FOOT_ROWS = 0
CHECK_OFFSET_ROW = 2
DIVA_TB_COLUMN = u'time'
DIVA_DELIMITER = '\t'
DIVA_ENCODING = 'utf_8'
HEADER_OFFSET_ROW = 7
UNIT_OFFSET_ROW = 8
DATA_NO_ROWS = -1
DATA_FOOT_ROWS = 0
DATA_OFFSET_ROW = 9


def print_timing(func):
    def wrapper(*arg):
        t1 = time.time()
        res = func(*arg)
        t2 = time.time()
        print('%s took %0.3f ms' % (func.func_name, (t2 - t1) * 1000.0))
        return res
    return wrapper


def check_file_header(importer):
    try:
        test_table = table.File()
        importer.import_csv(
            test_table, CHECK_NO_ROWS, CHECK_FOOT_ROWS, CHECK_OFFSET_ROW)
        testname_attr = test_table.get_column_to_array('X0')[0]
        if testname_attr != 'TESTNAME':
            raise
    except Exception:
        raise SyDataError('Not a valid DIVA file')


class DataSnifferEE(object):
    """ Sniff a file and determine the data format """
    ee_format_diva_export = 0
    ee_format_unknown = 0xff

    def __init__(self, filename):
        """  """
        self._sample_size = 256
        self.filename = filename
        self._sample = None
        with open(self.filename, 'rb') as f:
            self._sample = f.read(self._sample_size)

    def evaluate_format(self):
        """ Read a sample from file and determine the format """

        if self.is_diva_export():
            return self.ee_format_diva_export

        return self.ee_format_unknown

    def is_diva_export(self):
        """ Is the sample from a DIVA file """
        split_sample = re.split(b'[\\t\n\\r]+', self._sample)

        diva_id = b'DIVA ASCII-Export by Textfield Modul Version 2.0'
        return split_sample[0] == diva_id


class DataSnifferDIVA(importers.IDataSniffer):
    def __init__(self):
        super(DataSnifferDIVA, self).__init__()

    def sniff(self, path):
        ds = DataSnifferEE(path)
        return DataSnifferEE.ee_format_diva_export == ds.evaluate_format()


class DataImportDIVA(importers.ADAFDataImporterBase):
    """ Import exported DIVA data into h5 format """
    IMPORTER_NAME = "DIVA"

    def __init__(self, fq_infilename, parameters):
        super(DataImportDIVA, self).__init__(fq_infilename, parameters)

    def valid_for_file(self):
        if self._fq_infilename is None or not os.path.isfile(
                self._fq_infilename):
            return False
        return DataSnifferDIVA().sniff(self._fq_infilename)

    def import_data(self, out_datafile, parameters=None, progress=None):
        """ Import DIVA data from a file """

        table_source = TableSourceCSV(self._fq_infilename,
                                      delimiter=DIVA_DELIMITER,
                                      encoding=DIVA_ENCODING)
        importer = ImporterCSV(table_source)

        check_file_header(importer)

        data_table = table.File()
        importer.import_csv(
            data_table, DATA_NO_ROWS, DATA_FOOT_ROWS, DATA_OFFSET_ROW,
            headers_row_offset=HEADER_OFFSET_ROW,
            units_row_offset=UNIT_OFFSET_ROW)

        if progress:
            progress(60)

        system = out_datafile.sys.create(self.IMPORTER_NAME)
        raster = system.create('Group0')

        attributes = data_table.get_column_attributes(DIVA_TB_COLUMN)
        attributes.setdefault('unit', 's')
        attributes.setdefault('sampling_rate', 0.1)
        data_table.set_column_attributes(DIVA_TB_COLUMN, attributes)
        raster.from_table(data_table, DIVA_TB_COLUMN)
