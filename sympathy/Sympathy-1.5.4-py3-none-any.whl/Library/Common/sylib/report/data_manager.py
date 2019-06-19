# Copyright (c) 2015, Combine Control Systems AB
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
from __future__ import (
    print_function, division, unicode_literals, absolute_import)
import itertools
import six
import numpy as np

from sympathy.platform.exceptions import SyDataError

from . import patterns

# Single instance for module, created by init_data_source below.
data_source = None


def unique_names(name_list):
    names = [name if name else str(i) for i, name in enumerate(name_list)]
    unique_names = set(names)
    for unique in unique_names:
        duplicates = [i for i, name in enumerate(names) if name == unique]
        if len(duplicates) > 1:
            for i, index in enumerate(duplicates):
                names[index] = names[index] + '_' + str(i)
    return names


class AbstractDataSource(object):
    def __init__(self, input_data):
        self.signal_mapping = {}
        self._table_name_lengths = {}
        self.input_data = input_data
        self._signal_list = None

    def set_signal_mapping(self, source_to_target_dict):
        """
        Set mapping between source signal name to target signal name.
        :param source_to_target_dict: Mapping between source signal and
                                      target signal.
        """
        self.signal_mapping = source_to_target_dict

    def data(self, name):
        raise NotImplementedError()

    def row_count(self, name):
        raise NotImplementedError()

    def signal_list(self):
        """
        Return signal list.
        :return: List of signals.
        """
        return self._signal_list


class TablesSource(AbstractDataSource):
    def __init__(self, input_data):
        super(TablesSource, self).__init__(input_data)
        self.tables = {}

        table_name_list = unique_names([x.get_name() for x in input_data])
        for x, name in zip(input_data, table_name_list):
            x.set_name(name)

        ds_list = set()
        for table_name, table in six.moves.zip(table_name_list, input_data):
            column_names = table.column_names()
            for column_name in column_names:
                name = '{}.{}'.format(table_name, column_name)
                ds_list.add(name)
                self.tables[table_name] = table
                self._table_name_lengths[name] = len(table_name)
        self._signal_list = sorted(list(ds_list))

    def data(self, name):
        """
        Get data from table source given its name <table>.<column>.
        :param name: Name of data
        :return: Column.
        """
        # Return the name itself if it is not in the signal mapping.
        name = self.signal_mapping.get(name, name)
        try:
            table_name = name[:self._table_name_lengths[name]]
            column_name = name[len(table_name) + 1:]
        except ValueError:
            return np.array([])
        try:
            return self.tables[table_name].get_column_to_array(column_name)
        except KeyError:
            return np.array([])

    def row_count(self, name):
        """
        Get row count for the given table name.
        :param name: Name of signal.
        :return: Row count of table where signal is located.
        """
        table_name, _ = name.split('.')
        return self.tables[table_name].number_of_rows()


class ADAFsSource(AbstractDataSource):
    def __init__(self, input_data):
        super(ADAFsSource, self).__init__(input_data)
        data_count = len(input_data)
        adaf_name_list = ['_adaf{}'.format(str(i).zfill(len(str(data_count))))
                          if x.source_id() is None else x.source_id()
                          for i, x in enumerate(input_data)]

        # Check if there are any empty names.
        error_message = 'Source ID must not be empty for an ADAF.'
        try:
            any_empty_name = any([len(x) == 0 for x in adaf_name_list])
        except TypeError:
            raise SyDataError(error_message)
        if any_empty_name:
            for i in range(data_count):
                if not len(adaf_name_list[i]):
                    adaf_name_list[i] = str(i)

        # Check if there are duplicate names.
        duplicates = set([x for x in adaf_name_list
                          if adaf_name_list.count(x) > 1])
        if len(duplicates) > 0:
            raise SyDataError('ADAF Source IDs must be unique.')

        ds_list = set()
        for adaf_name, adaf in six.moves.zip(adaf_name_list, input_data):
            # start with meta
            for meta_column_name in list(adaf.meta.keys()):
                ds_list.add('{}.meta.{}'.format(adaf_name, meta_column_name))
            # now results
            for res_name in list(adaf.res.keys()):
                ds_list.add('{}.res.{}'.format(adaf_name, res_name))
            # and now systems
            for system_name, system in list(adaf.sys.items()):
                for raster_name, raster in list(system.items()):
                    ds_list.add('{}.sys.{}.{}'.format(adaf_name, system_name,
                                                      raster_name))
                    for signal_name in list(raster.keys()):
                        ds_list.add('{}.sys.{}.{}.{}'.format(adaf_name,
                                                             system_name,
                                                             raster_name,
                                                             signal_name))
        self._signal_list = sorted(list(ds_list))

    def data(self, name):
        if len(name) == 0:
            return np.array([])

        name = self.signal_mapping.get(name, name)

        name_components = name.split('.')
        adaf_name = name_components[0]
        result = patterns.re_autogen_adaf_name.match(adaf_name)
        if result is None:
            adaf = self.input_data[0]
        else:
            adaf = self.input_data[int(result.group(1))]

        part_name = name_components[1]
        if part_name == 'meta':
            return adaf.meta[name_components[2]].value()
        elif part_name == 'res':
            return adaf.res[name_components[2]].value()
        elif part_name == 'sys':
            remainder = name_components[2:]
            system = adaf.sys[remainder[0]]
            raster = system[remainder[1]]
            if len(remainder) == 2:
                # Only system name and raster has been specified, return raster
                return raster.basis_column().value()
            else:
                signal = raster[remainder[2]]
                return signal.y
        else:
            raise SyDataError(
                'Unknown part of ADAF: {}.{}'.format(adaf_name, part_name))

    def row_count(self, name):
        return len(self.data(name))


def init_data_source(input_data, data_type):
    """
    Data source factory.
    Stores data source instance in module to achieve singleton effect.
    :param input_data: Input data from port.
    :param data_type: Type of data.
    """
    global data_source

    type_to_class = {
        'tables': TablesSource,
        'adafs': ADAFsSource
    }

    data_source = type_to_class[data_type](input_data)
