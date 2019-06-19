# -*- coding: utf-8 -*-
# Copyright (c) 2016, 2017, Combine Control Systems AB
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
import os
from sympathy.platform import gennode as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags
from sympathy.api import exporters
from sylib.export import base


class ExportFigures(base.ExportMultiple, synode.Node):
    """
    Export Figures to a selected data format.

    :Ref. nodes:
        :ref:`Figures`, :ref:`Figures from Tables with Table`
    """

    name = 'Export Figures'
    description = 'Export Figures to image files.'
    icon = 'export_figure.svg'
    tags = Tags(Tag.Output.Export)
    author = 'Benedikt Ziegler <benedikt.ziegler@combine.se>'
    copyright = '(c) 2016 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.export.exportfigures'
    version = '0.2'
    inputs = Ports([Port.Figures('Input figures', name='figures'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])
    plugins = (exporters.FigureDataExporterBase, )
    parameters = base.base_params()
    parameters.set_string(
        'active_exporter', label='Exporter',
        description=('Select data format exporter. Each data format has its '
                     'own exporter with its own special configuration, see '
                     'exporter information. The selection of exporter do also '
                     'suggest filename extension'))
    custom_exporter_group = parameters.create_group('custom_exporter_data')
    parameters.set_string(
        'directory', value='.', label='Output directory',
        description='Select the directory where to export the files.',
        editor=synode.Util.directory_editor().value())
    parameters.set_string(
        'filename', label='Filename',
        description=('Specify the common base for the filenames. If there are '
                     'several incoming Figures the node will add “_${index '
                     'number of corresponding Figure in the incoming list}” '
                     'after the base for each file. Do not specify extension'))

    def update_parameters(self, old_params):
        extension = old_params._parameter_dict.pop('extension', None)
        width = old_params._parameter_dict.pop('width', None)
        height = old_params._parameter_dict.pop('height', None)
        if 'custom_exporter_data' not in old_params:
            custom_exporter_data = old_params.create_group(
                'custom_exporter_data')
        else:
            custom_exporter_data = old_params['custom_exporter_data']
        if 'Image' not in custom_exporter_data:
            image = custom_exporter_data.create_group('Image')
        else:
            image = custom_exporter_data['Image']
        if extension is not None:
            image.set_list('extension',
                           label=extension['label'],
                           description=extension['description'],
                           value=extension['value'],
                           plist=extension['list'],
                           editor=extension['editor'])
        if width is not None:
            image.set_integer('width',
                              label=width['label'],
                              description=width['description'],
                              value=width['value'],
                              editor=width['editor'])
        if height is not None:
            image.set_integer('height',
                              label=height['label'],
                              description=height['description'],
                              value=height['value'],
                              editor=height['editor'])
        return old_params


class ExportFiguresWithDsrcs(base.ExportMultiple, synode.Node):
    """
    Export Figures to a selected data format with a list of datasources for
    output paths.
    """

    name = 'Export Figures with Datasources'
    description = 'Export Figures to image files.'
    icon = 'export_figure.svg'
    tags = Tags(Tag.Output.Export)
    author = 'Magnus Sandén <magnus.sanden@combine.se>'
    copyright = '(c) 2016 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.export.exportfigureswithdscrs'
    version = '0.1'

    inputs = Ports([
        Port.Figures('Input figures', name='figures'),
        Port.Datasources('Datasources', name='dsrcs')])
    plugins = (exporters.FigureDataExporterBase, )
    parameters = base.base_params()

    def _exporter_ext_filenames_portname(self):
        return 'dsrcs'

    def _exporter_ext_filename(self, custom_parameters, filename):
        if not os.path.splitext(filename)[1]:
            ext = custom_parameters['extension'].selected
            filename = '{}.{}'.format(filename, ext)
        return filename
