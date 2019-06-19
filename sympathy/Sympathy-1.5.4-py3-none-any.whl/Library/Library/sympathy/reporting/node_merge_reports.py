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
import copy
import collections
import re
import six
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Ports, Tag, Tags
from sympathy.api import report
from sylib.report import models


prefix_pattern = re.compile(r'\d+\s.+')


class MergeReports(synode.Node):
    """Merge pages of report by appending the second input to the first."""

    name = 'Merge Reports'
    nodeid = 'org.sysess.sympathy.report.merge'
    author = 'Stefan Larsson <stefan.larsson@combine.se>'
    copyright = '(C) 2015 Combine Control Systems AB'
    version = '1.0'
    icon = 'report-merge.svg'
    tags = Tags(Tag.Visual.Report)

    inputs = Ports([
        report.Report('First Report Template', name='first_input_template'),
        report.Report('Second Report Template', name='second_input_template')
    ])
    outputs = Ports([report.Report('Merged Template',
                                   name='output_template')])

    def execute(self, node_context):
        self.set_progress(0)

        document_1 = json.loads(node_context.input[0].get())
        model_1 = models.Root(document_1)
        self.set_progress(5)
        document_2 = json.loads(node_context.input[1].get())
        model_2 = models.Root(document_2)
        self.set_progress(10)

        page_uuids = []
        for m in (model_1, model_2):
            for p in m.find_all_nodes_with_class(models.Page):
                page_uuids.append(p.uuid)
        second_page_uuids = []
        for p in model_1.find_all_nodes_with_class(models.Page):
            second_page_uuids.append(p.uuid)

        # Remove all UUIDs from the first model since those are added by
        # default.
        for p in model_1.find_all_nodes_with_class(models.Page):
            page_uuids.remove(p.uuid)

        # Copy first model to become output model.
        output_model = copy.deepcopy(model_1)

        output_model.data['signals'] = self.merge_signals(model_1, model_2)

        self.set_progress(40)

        # Merge pages.
        pages_2 = model_2.find_all_nodes_with_class(models.Page)
        page_root = output_model.find_all_nodes_with_class(models.Pages)[0]
        for page in pages_2:
            if page.uuid in page_uuids:
                models.insert_node(page, page_root)
                page_uuids.remove(page.uuid)
            if page.uuid in second_page_uuids:
                # If pages from the same report are merged, update uuid
                # to avoid duplicates.
                page.update_uuid()

        self.set_progress(70)

        output_model.data['signals'] = models.compress_signals(
            output_model.data)
        output_model.data['scales'] = self.merge_scales(model_1, model_2,
                                                        page_root)

        self.set_progress(100)

        # Write result.
        node_context.output[0].set(json.dumps(output_model.data))

    @staticmethod
    def merge_signals(model_1, model_2):
        """
        Merge list of signals used.
        :param model_1: first model
        :param model_2: second model
        :return: union of signals
        """
        # Merge signal list of both documents.
        signals_1 = set(model_1.data['signals'])
        signals_2 = set(model_2.data['signals'])
        return list(signals_1.union(signals_2))

    def merge_scales(self, model_1, model_2, page_root):
        """
        Merge scales into a single list of scales while modifying names in
        the second model by appending _ if the scale id occurs in the first
        model.
        :param model_1: first model
        :param model_2: second model
        :param page_root: page root container
        :return: list of merged scales
        """
        # Find all scales of both documents.
        scales_1 = model_1.data['scales']
        scale_ids_1 = [x['id'] for x in scales_1]
        scales_2 = model_2.data['scales']
        scale_ids_2 = [x['id'] for x in scales_2]
        # Ensure unique scale id:s by appending extra _ to duplicate names.
        continue_search = True
        while continue_search:
            continue_search = False
            for scale_id in scale_ids_1:
                if scale_id in scale_ids_2:
                    index = scale_ids_2.index(scale_id)
                    new_id = scale_id + '_'
                    scales_2[index]['id'] = new_id
                    scale_ids_2[index] = new_id
                    # side-effect
                    self.update_scale_names_in_pages(scale_id, new_id,
                                                     page_root)
                    continue_search = True
                    break
        return scales_1 + scales_2

    @staticmethod
    def update_scale_names_in_pages(old_scale_id, new_scale_id, page_root):
        """
        Replace all instances of old scale name with new name.
        :param old_scale_id: old scale id
        :param new_scale_id: new scale id
        :param page_root: root page collection
        """
        def search_and_update(node):
            if isinstance(node, six.string_types):
                return node == old_scale_id
            elif isinstance(node, collections.Sequence):
                for i, v in enumerate(node):
                    if search_and_update(v):
                        node[i] = new_scale_id
            elif isinstance(node, collections.Mapping):
                for k, v in six.iteritems(node):
                    if search_and_update(v):
                        node[k] = new_scale_id
            return False
        search_and_update(page_root.data)
