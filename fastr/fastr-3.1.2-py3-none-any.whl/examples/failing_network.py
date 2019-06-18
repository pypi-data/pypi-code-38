#!/usr/bin/env python

# Copyright 2011-2014 Biomedical Imaging Group Rotterdam, Departments of
# Medical Informatics and Radiology, Erasmus MC, Rotterdam, The Netherlands
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import fastr
FAILS = True  # Indicate that this network is supposed to have failing jobs


def create_network():
    network = fastr.create_network('failing_network')
    # create sources
    source_1 = network.create_source('Int', id='source_1')
    source_2 = network.create_source('Int', id='source_2')
    source_3 = network.create_source('Int', id='source_3')
    # Create sinks
    sink_1 = network.create_sink('Int', id='sink_1')
    sink_2 = network.create_sink('Int', id='sink_2')
    sink_3 = network.create_sink('Int', id='sink_3')
    sink_4 = network.create_sink('Int', id='sink_4')
    sink_5 = network.create_sink('Int', id='sink_5')

    # create nodes
    step_1 = network.create_node('fastr/util/Fail:1.0', tool_version='1.0', id='step_1')
    step_2 = network.create_node('fastr/util/Fail:1.0', tool_version='1.0', id='step_2')
    step_3 = network.create_node('fastr/util/Fail:1.0', tool_version='1.0', id='step_3')

    range_node = network.create_node('fastr/util/Range:1.0', tool_version='1.0', id='range')
    sum_node = network.create_node('fastr/math/Sum:1.0', tool_version='1.0', id='sum')

    # create links
    step_1.inputs['in_1'] = source_1.output
    step_1.inputs['in_2'] = source_2.output
    step_1.inputs['fail_2'] = [False, True, False, True]

    step_2.inputs['in_1'] = source_3.output
    step_2.inputs['in_2'] = source_1.output
    step_2.inputs['fail_1'] = [False, False, True, True]

    step_3.inputs['in_1'] = step_1.outputs['out_2']
    step_3.inputs['in_2'] = step_2.outputs['out_1']

    range_node.inputs['value'] = step_3.outputs['out_1']

    sum_node.inputs['values'] = range_node.outputs['result']

    sink_1.input = step_1.outputs['out_1']
    sink_2.input = step_2.outputs['out_2']
    sink_3.input = step_3.outputs['out_1']
    sink_4.input = range_node.outputs['result']
    sink_5.input = sum_node.outputs['result']

    # Check/Draw/execute network
    return network


def source_data(network):
    fastr.log.info('Creating source data for {}'.format(network.id))
    return {
        'source_1': {'sample_1': 'vfslist://example_data/add_ints/values'},
        'source_2': {'sample_1': 'vfslist://example_data/add_ints/values'},
        'source_3': {'sample_1': 'vfslist://example_data/add_ints/values'},
    }


def sink_data(network):
    fastr.log.info('Creating sink data for {}'.format(network.id))
    return {
        'sink_1': 'vfs://tmp/results/{}/sink_1_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
        'sink_2': 'vfs://tmp/results/{}/sink_2_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
        'sink_3': 'vfs://tmp/results/{}/sink_3_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
        'sink_4': 'vfs://tmp/results/{}/sink_4_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
        'sink_5': 'vfs://tmp/results/{}/sink_5_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
    }


def main():
    network = create_network()
    network.draw(network.id, draw_dimensions=True)
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
