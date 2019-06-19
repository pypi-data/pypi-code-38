# Copyright (c) 2013, 2017, Combine Control Systems AB
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

from sympathy.api import node as synode
from sylib.plot import backend as plot_backends
from sylib.plot import model as plot_models
from sylib.export import common
from sylib.export import table as exporttable
from sylib.export import base
from sympathy.api.nodeconfig import Port, Ports


class ExportTables(base.ExportMultiple, synode.Node):
    __doc__ = common.COMMON_DOC + """

If the input Table(s) has a plot attribute (as created by e.g.,
:ref:`Plot Tables`) it can be exported to a separate file by selecting one
of the extensions in the output section.

:Opposite node: :ref:`Tables`
:Ref. nodes: :ref:`Export ADAFs`
    """
    name = 'Export Tables'
    description = 'Export Tables'
    icon = 'export_table.svg'
    inputs = Ports([Port.Tables('Tables to be exported', name='port0'),
                    Port.Datasources(
                        'External filenames',
                        name='port1', n=(0, 1, 0))])

    plugins = (exporttable.TableDataExporterBase, )
    author = 'Alexander Busck <alexander.busck@combine.se>'
    copyright = '(c) 2013 Combine Control Systems AB'
    nodeid = 'org.sysess.sympathy.export.exporttables'
    version = '0.1'
    parameters = base.base_params()
    parameters.set_list(
        'plot',
        label='Output separate plot file with the following extension:',
        description='If there is a plot attribute in the input tables(s), '
        'create a separate file with the plot.',
        value=[0],
        plist=['-', 'eps', 'pdf', 'svg', 'png'],
        editor=synode.Util.combo_editor())

    def _exporter_input_item_filename_hook(self, input_item, fq_filename):

        if self._plot is not None:
            plots_model = plot_models.get_plots_model(
                input_item)
            plot_exporter = plot_backends.ExporterBackend(
                plots_model, self._plot)

            plot_exporter.render(
                os.path.splitext(fq_filename)[0])

    def execute(self, node_context):
        plot = None
        if 'plot' in node_context.parameters:
            plot = node_context.parameters['plot'].selected
            plot = None if plot == '-' else plot

        self._plot = plot
        super(ExportTables, self).execute(node_context)
        self._plot = None
