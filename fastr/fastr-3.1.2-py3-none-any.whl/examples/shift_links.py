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


def create_network():
    # Import the faster environment and set it up
    import fastr
    # Create a new network
    network = fastr.create_network(id='shift_links')

    # Create a source node in the network
    source1 = network.create_source('Int', id='source')

    # Create a new node in the network using tools
    node = network.create_node('fastr/math/AddInt:1.0', tool_version='1.0', id="add")

    # Create a link between the source output and an input of the addint node
    node.inputs['left_hand'] << source1.output
    node.inputs['left_hand'].append([6, 7, 8, 9, 10])

    # Create a constant node and link it to the value2 input of the addint node
    node.inputs['right_hand'] << (10, 20)

    # Create a sink to save the data
    sink = network.create_sink('Int', id='sink')

    # Link the addint node to the sink
    node.outputs['result'] >> sink.input

    return network


def source_data(network):
    return {'source': [1, 'vfslist://example_data/add_ints/values']}


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Execute
    network.draw()
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
