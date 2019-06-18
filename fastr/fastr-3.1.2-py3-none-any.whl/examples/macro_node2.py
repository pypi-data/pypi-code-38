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


def create_macro_network():
    # Create Network
    network = fastr.create_network('add_ints_macro')
    # Create first source
    input_1 = network.create_source('Int', id='macro_input_1')
    input_2 = network.create_source('Int', id='macro_input_2')

    # Create calculation nodes
    addint1 = network.create_node('fastr/math/AddInt:1.0', tool_version='1.0', id='addint1')

    # Link network
    addint1.inputs['left_hand'] = input_1.output
    addint1.inputs['right_hand'] = input_2.output
    addint1.inputs['right_hand'].input_group = 'other'

    # Create a sink to save the data
    sink = network.create_sink('Int', id='macro_sink')

    # Link the addint node to the sink
    sink.inputs['input'] = addint1.outputs['result']

    return network


def create_network():
    macro_network = create_macro_network()

    # Create Network
    network = fastr.create_network('macro_node_2')

    # Extra Node
    add = network.create_node('fastr/math/AddInt:1.0', tool_version='1.0', id='addint')

    # Create data source
    input_1 = network.create_source('Int', id='source_1')
    input_2 = network.create_source('Int', id='source_2')
    input_3 = network.create_source('Int', id='source_3')

    # Create MacroNode
    add_multiple_ints_node = network.create_macro(macro_network, id='node_add_multiple_ints_1')

    # Sum some stuff
    sum = network.create_node('fastr/math/Sum:1.0', tool_version='1.0', id='sum')

    # Create sink
    sink = network.create_sink('Int', id='sink')

    # Adjust constants(non required inputs) in macro network
    #  add_multiple_ints_node.inputs['const_addint1_value2__add_multiple_ints_1'] = 1234, #input.output
    # Link the network
    add.inputs['left_hand'] = input_1.output
    add.inputs['right_hand'] = input_2.output
    add.inputs['right_hand'].input_group = 'right'

    add_multiple_ints_node.inputs['macro_input_1'] = add.outputs['result']
    add_multiple_ints_node.inputs['macro_input_2'] = input_3.output

    link = sum.inputs['values'] << add_multiple_ints_node.outputs['macro_sink']
    link.collapse = 1

    sink.inputs['input'] = sum.outputs['result']

    return network


def source_data(network):
    return {
        'source_1': [1, 2],
        'source_2': [4, 5, 6],
        'source_3': [7, 8, 9, 10],
    }


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Validate and execute network
    if network.is_valid():
        network.draw(network.id, draw_dimensions=True)
        network.execute(source_data(network), sink_data(network))
    else:
        print("Network was not valid")


if __name__ == '__main__':
    main()
