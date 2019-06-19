# Copyright (c) 2013, 2017-2018 Combine Control Systems AB
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
from collections import OrderedDict
import inspect
import sys
from sympathy.api import node as synode
from sympathy.api import datasource as dsrc
from sympathy.api import importers
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exceptions


def hasarg(func, arg):
    return arg in inspect.getargspec(func).args


FAILURE_STRATEGIES = OrderedDict(
    [('Exception', 0), ('Create Empty Entry', 1)])

LIST_FAILURE_STRATEGIES = OrderedDict(
    [('Exception', 0), ('Create Empty Entry', 1), ('Skip File', 2)])


def import_data(item_factory, importer_cls, datasource,
                parameters, manage_input, progress):

    def import_native(importer, dspath, manage_input):
        """
        Special case where the file is native sydata of the right type and
        should be copied into the platform.
        """
        try:
            # Got plugin adaf importer.
            import_links = importer.import_links
        except AttributeError:
            import_links = False

        ds_infile = item_factory(
            filename=dspath, mode='r', import_links=import_links)
        if manage_input is not None:
            manage_input(dspath, ds_infile)
        return ds_infile

    def import_external(importer, parameters, progress, manage_input):

        output = item_factory()
        if hasarg(importer.import_data, 'manage_input'):
            importer.import_data(
                output, parameters, progress=progress,
                manage_input=manage_input)
        else:
            importer.import_data(
                output, parameters, progress=progress)
        return output

    dspath = datasource.decode_path()
    importer = importer_cls(dspath, parameters)

    if importer.is_type():
        return import_native(importer, dspath, manage_input)
    return import_external(importer, parameters, progress, manage_input)


class SuperNode(object):
    tags = Tags(Tag.Input.Import)
    plugins = (importers.IDataImporter, )

    @staticmethod
    def parameters_base():
        parameters = synode.parameters()
        parameters.set_string(
            'active_importer', label='Importer', value='Auto',
            description=('Select data format importer'))
        custom_importer_group = parameters.create_group(
            'custom_importer_data')
        custom_importer_group.create_group('Auto')
        return parameters

    def _available_plugins(self, name=None):
        return importers.available_plugins(self.plugins[0])

    def _output_item_filename_hook(self, output_item, filename):
        pass


class ImportSingle(SuperNode):
    inputs = Ports([Port.Datasource('Datasource')])

    parameters = SuperNode.parameters_base()
    parameters.set_list(
        'fail_strategy', label='Action on import failure',
        list=list(FAILURE_STRATEGIES.keys()), value=[0],
        description='Decide how failure to import a file should be handled.',
        editor=synode.Util.combo_editor())

    def exec_parameter_view(self, node_context):
        dspath = None
        try:
            datasource = node_context.input.first
            dspath = datasource.decode_path()
        except exceptions.NoDataError:
            # This is if no input is connected.
            pass
        return importers.configuration_widget(
            self._available_plugins(),
            node_context.parameters, dspath)

    def execute(self, node_context):
        params = synode.parameters(node_context.parameters)
        importer_type = params['active_importer'].value
        if 'fail_strategy' in params:
            fail_strategy = params['fail_strategy'].value[0]
        else:
            fail_strategy = 0

        try:
            importer_cls = self._available_plugins().get(importer_type)
            datasource = node_context.input.first
            ds_dict = datasource.decode()

            if importer_cls is None:
                raise exceptions.SyDataError(
                    "No importer could automatically be found for this file.")

            item_factory = type(node_context.output.first)

            with import_data(
                    item_factory,
                    importer_cls, datasource,
                    params["custom_importer_data"][importer_type],
                    None,
                    progress=self.set_progress) as output:

                if ds_dict['type'] == 'FILE':
                    self._output_item_filename_hook(output, ds_dict['path'])

                node_context.output.first.source(output)
        except Exception:
            if fail_strategy == FAILURE_STRATEGIES['Create Empty Entry']:
                pass
            else:
                raise

        self.set_progress(70)


class ImportMulti(SuperNode):
    inputs = Ports([
        Port.Datasources('Datasources', name='input', requiresdata=True)])

    parameters = SuperNode.parameters_base()
    parameters.set_list(
        'fail_strategy', label='Action on import failure',
        list=list(LIST_FAILURE_STRATEGIES.keys()), value=[0],
        description='Decide how failure to import a file should be handled.',
        editor=synode.Util.combo_editor())

    def exec_parameter_view(self, node_context):
        dspath = None
        try:
            try:
                datasource = node_context.input.first[0]
            except IndexError:
                datasource = dsrc.File()
            dspath = datasource.decode_path()
        except exceptions.NoDataError:
            # This is if no input is connected.
            pass

        return importers.configuration_widget(
            self._available_plugins(),
            node_context.parameters, dspath)

    def execute(self, node_context):
        params = node_context.parameters
        importer_type = params['active_importer'].value
        if 'fail_strategy' in params:
            fail_strategy = params['fail_strategy'].value[0]
        else:
            fail_strategy = 0

        input_list = node_context.input.first
        len_input_list = len(input_list)
        output_list = node_context.output.first
        item_factory = type(output_list.create())
        for i, datasource in enumerate(input_list):
            try:
                importer_cls = self._available_plugins().get(importer_type)
                ds_dict = datasource.decode()
                if importer_cls is None:
                    raise exceptions.SyDataError(
                        "No importer could automatically be found for "
                        "this file.")

                output_item = import_data(
                    item_factory,
                    importer_cls,
                    datasource,
                    params['custom_importer_data'][importer_type],
                    node_context.manage_input,
                    lambda x: self.set_progress(
                        (100 * i + x) / len_input_list))

                if ds_dict['type'] == 'FILE':
                    self._output_item_filename_hook(
                        output_item, ds_dict['path'])

                output_list.append(output_item)
            except Exception:
                if fail_strategy == LIST_FAILURE_STRATEGIES['Exception']:
                    raise exceptions.SyListIndexError(i, sys.exc_info())
                elif fail_strategy == LIST_FAILURE_STRATEGIES[
                        'Create Empty Entry']:
                    print('Creating empty output file (index {}).'.format(i))
                    output_item = item_factory()
                    output_list.append(output_item)
                else:
                    print('Skipping file (index {}).'.format(i))

            self.set_progress(100 * (1 + i) / len_input_list)
