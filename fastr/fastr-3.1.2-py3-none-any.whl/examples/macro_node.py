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
    input_ = network.create_source('Int', id='input')

    # Create calculation nodes
    addint1 = network.create_node('fastr/math/AddInt:1.0', tool_version='1.0', id='addint1', step_id='add')
    addint2 = network.create_node('fastr/math/AddInt:1.0', tool_version='1.0', id='addint2', step_id='add')

    # Link network
    addint1.inputs['left_hand'] = input_.output
    addint1.inputs['right_hand'] = 10,
    addint2.inputs['left_hand'] = addint1.outputs['result']
    addint2.inputs['right_hand'] = 100,

    # Create a sink to save the data
    sink = network.create_sink('Int', id='macro_sink')

    # Link the addint node to the sink
    sink.inputs['input'] = addint2.outputs['result']

    return network


def create_super_macro_node():
    network = fastr.create_network('macro_container')
    # Create Outputs

    input_value = network.create_source('Int', id='input_value')
    # Create Macro Networks

    macro_network_1 = create_macro_network()
    macro_network_2 = create_macro_network()
    add_multiple_ints_node_1 = network.create_macro(macro_network_1, id='node_add_multiple_ints_1')
    add_multiple_ints_node_2 = network.create_macro(macro_network_2, id='node_add_multiple_ints_2')
    # Create Sink

    output_value = network.create_sink('Int', id='output_value')
    # Create Links

    add_multiple_ints_node_1.inputs['input'] = input_value.output
    add_multiple_ints_node_2.inputs['input'] = add_multiple_ints_node_1.outputs['macro_sink']
    output_value.inputs['input'] = add_multiple_ints_node_2.outputs['macro_sink']

    return network


def create_network():
    macro_network = create_super_macro_node()

    # Create Network
    test_network = fastr.create_network('macro_top_level')

    # Create data source
    input_ = test_network.create_source('Int', id='source', step_id='source')

    # Create MacroNode
    add_multiple_ints_node = test_network.create_macro(macro_network, id='node_add_ints')

    # Create sink
    sink = test_network.create_sink('Int', id='sink')

    # Adjust constants(non required inputs) in macro network
    #  add_multiple_ints_node.inputs['const_addint1_value2__add_multiple_ints_1'] = 1234, #input.output
    # Link the network
    add_multiple_ints_node.inputs['input_value'] = input_.output
    sink.inputs['input'] = add_multiple_ints_node.outputs['output_value']

    return test_network


def source_data(network):
    return {'source': [1, 'vfslist://example_data/add_ints/values']}


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Validate and execute network
    if network.is_valid():
        network.draw(network.id, expand_macros=True, draw_dimensions=True)
        network.execute(source_data(network), sink_data(network))
    else:
        print("Network was not valid")


if __name__ == '__main__':
    main()
