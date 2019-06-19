# Copyright (c) 2015, 2017, Combine Control Systems AB
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
import json

from sympathy.api import node as synode
from sympathy.api.nodeconfig import Ports, Tag, Tags
from sympathy.api import report
from sylib.report import models
from sylib.report import gui_select_report_pages


class SelectReportPages(synode.Node):
    """
    Selects a set of pages from an existing report template and
    exports a new template with only those pages left.
    """

    name = 'Select Report Pages'
    nodeid = 'org.sysess.sympathy.report.select.pages'
    author = 'Stefan Larsson <stefan.larsson@combine.se>'
    copyright = '(C) 2015 Combine Control Systems AB'
    version = '1.0'
    icon = 'report-select.svg'
    tags = Tags(Tag.Visual.Report)

    inputs = Ports([report.Report('Input Report Template',
                                  name='input_template')])
    outputs = Ports([report.Report('Output Report Template',
                                   name='output_template')])

    parameters = synode.parameters()
    parameters.set_list(
        'selected_pages',
        value=[],
        plist=[],
        label='Selected Pages',
        description='Selected pages of report.')

    def execute(self, node_context):
        self.set_progress(0)

        p = synode.parameters(node_context.parameters)
        selected_page_uuids = [x[0] for x in p['selected_pages'].list]

        if len(selected_page_uuids) == 0:
            raise ValueError('At least one page has to be selected')

        document = json.loads(node_context.input[0].get())
        model = models.Root(document)
        self.set_progress(5)

        # Remove pages which have not been selected.
        page_list = model.find_all_nodes_with_class(models.Page)
        for i, page in enumerate(page_list):
            if page.data['uuid'] not in selected_page_uuids:
                models.remove_node(page)
            self.set_progress(
                float(i) / float(len(selected_page_uuids)) * 95 + 5)

        # Compress signal list.
        compressed_signal_list = models.compress_signals(model.data)
        output_document = model.data
        output_document['signals'] = compressed_signal_list

        output_template_port = node_context.output[0]
        output_template_port.set(json.dumps(output_document))

    def exec_parameter_view(self, node_context):
        inport = node_context.input[0]
        model = None
        if inport.is_valid():
            document = json.loads(inport.get())
            model = models.Root(document)
        return gui_select_report_pages.SelectReportPages(
            model, node_context.parameters)
