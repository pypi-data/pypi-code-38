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
    network = fastr.create_network(id='advanced_linking')

    # Create a source node in the network
    source1 = network.create_source('Int', id='source',
                                    resources=fastr.api.ResourceLimit(cores=1,
                                                                      memory='2G'))

    constant1 = network.create_constant('Int', data=[1, 2, 3, 4, 5], id='constant',
                                        resources=fastr.api.ResourceLimit(cores=1,
                                                                          memory='2G'))

    # Create a new node in the network using tools
    node1 = network.create_node('fastr/math/AddInt:1.0', tool_version="1.0", id="add1")
    node2 = network.create_node('fastr/math/AddInt:1.0', tool_version="1.0", id="add2")

    # Create a link between the source output and an input of the addint node
    # Link multiple outputs to one input
    link1, link2 = (source1.output, constant1.output) >> node1.inputs['left_hand']

    # Test mixed link
    links = (source1.output, 10, 11, constant1.output, 6, 7, 8) >> node2.inputs['left_hand']

    # Create a constant node and link it to the value2 input of the addint node
    node1.inputs['right_hand'] = (10, 11)
    node2.inputs['right_hand'] = (25, 26, 27, 28, 29, 30, 31)

    # Create a sink to save the data
    sink1 = network.create_sink('Int', id='sink1')
    sink2 = network.create_sink('Int', id='sink2')

    # Link the addint node to the sink
    sink1.input << node1.outputs['result']
    sink2.input << node2.outputs['result']

    return network


def source_data(network):
    return {'source': [1, 'vfslist://example_data/add_ints/values']}


def sink_data(network):
    return {
        'sink1': 'vfs://tmp/results/{}/result1_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
        'sink2': 'vfs://tmp/results/{}/result2_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id),
    }


def main():
    network = create_network()

    # Execute
    network.draw(network.id, draw_dimensions=True)
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
