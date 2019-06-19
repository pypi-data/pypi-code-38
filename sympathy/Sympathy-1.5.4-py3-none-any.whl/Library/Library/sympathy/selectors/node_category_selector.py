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
"""
A selector of categories in ADAFs can be used to drop of parts of ADAFs.
The main reason to do this is when the ADAFs contain data that is no longer
needed further along a workflow. Dropping the unnecessary data can then be used
as a way to try to optimize the workflow.
:ref:`ADAFs to Tables`.
"""
from sympathy.api import node as synode
from sympathy.api.nodeconfig import Port, Ports, Tag, Tags, adjust


def copy_group(source_group, target_group):
    """Copy a group from source to target."""
    target_group.from_table(source_group.to_table())


def copy_timeseries(in_tb, out_tb, raster_list=None):
    """Copy the timeseries group with all its systems/rasters."""
    if raster_list is None:
        # Copy all systems/rasters
        for system_name in in_tb.keys():
            out_system = out_tb.create(system_name)
            for raster_name in in_tb[system_name].keys():
                out_system.copy(raster_name, in_tb[system_name])
    else:
        # Copy only specified systems/rasters
        for r in raster_list:
            system_name, raster_name = r.split('/', 1)

            if (system_name in in_tb and
                    raster_name in in_tb[system_name]):
                if system_name not in out_tb:
                    out_tb.create(system_name)
                out_tb[system_name].copy(raster_name, in_tb[system_name])


def get_raster_names(adaflist):
    raster_names = set()
    for adaffile in adaflist:
        for system_name in adaffile.sys.keys():
            for raster_name in adaffile.sys[system_name].keys():
                raster_names.add('{}/{}'.format(system_name, raster_name))
    return sorted(raster_names)


def _set_category_fields(parameters):
    if 'select_rasters' not in parameters:
        multilist_editor = synode.Util.multilist_editor()
        parameters.set_list(
            'select_rasters', value=[], label='Select specific rasters:',
            description='Select specific rasters for inclusion in the output.',
            editor=multilist_editor)
    if 'select_meta' not in parameters:
        parameters.set_boolean(
            'select_meta', value=True, label='Select meta group',
            description='Select the meta group for inclusion in the output.')
    if 'select_res' not in parameters:
        parameters.set_boolean(
            'select_res', value=True, label='Select result group',
            description='Select the result group for inclusion in the output.')


class CategorySelectorMultiple(synode.Node):
    """Select categories in ADAFs."""

    name = 'Select category in ADAFs'
    description = 'Select what catgories to exist in the output ADAFs.'
    nodeid = 'org.sysess.sympathy.selectors.categoryselectormultiple'
    icon = 'select_category.svg'

    author = "Erik der Hagopian <erik.hagopian@combine.se>"
    copyright = "(C) 2013 Combine Control Systems AB"
    version = '1.0'
    tags = Tags(Tag.DataProcessing.Select)

    inputs = Ports([Port.ADAFs('Input ADAFs', name='port1')])
    outputs = Ports([Port.ADAFs(
        'ADAFs with selected categories', name='port3')])

    parameters = synode.parameters()
    _set_category_fields(parameters)

    def update_parameters(self, old_params):
        _set_category_fields(old_params)

        if 'select_ts' in old_params:
            if old_params['select_ts'].value:
                select_rasters = old_params['select_rasters']
                select_rasters._multiselect_mode = 'passthrough'
            del old_params['select_ts']

    def adjust_parameters(self, node_context):
        adjust(node_context.parameters['select_rasters'],
               node_context.input['port1'],
               kind='rasters')

    def execute(self, node_context):
        select_meta = node_context.parameters['select_meta'].value
        select_res = node_context.parameters['select_res'].value
        try:
            select_ts = node_context.parameters['select_ts'].value
        except KeyError:
            select_ts = False
        input_adafs = node_context.input['port1']
        output_adafs = node_context.output['port3']

        def select_category(input_adaf, output_adaf, set_progress):
            raster_list = (
                node_context.parameters['select_rasters'].selected_names(
                    input_adaf.names(kind='rasters')))

            if select_meta:
                copy_group(input_adaf.meta, output_adaf.meta)
            if select_res:
                copy_group(input_adaf.res, output_adaf.res)
            if select_ts:
                copy_timeseries(input_adaf.sys, output_adaf.sys)
            else:
                copy_timeseries(input_adaf.sys, output_adaf.sys, raster_list)

        synode.map_list_node(select_category, input_adafs, output_adafs,
                             self.set_progress)
