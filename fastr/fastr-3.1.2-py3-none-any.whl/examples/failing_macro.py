import fastr
import failing_network


def create_network():
    # Create network to embed
    child_network = failing_network.create_network()

    # Create Network
    network = fastr.create_network('failing_macro_top_level')

    # create sources
    source_a = network.create_source('Int', id='source_a')
    source_b = network.create_source('Int', id='source_b')
    source_c = network.create_source('Int', id='source_c')

    # Create MacroNode
    failing_macro = network.create_macro(child_network, id='failing_macro')

    # Link sources to macro
    failing_macro.inputs['source_1'] = source_a.output
    failing_macro.inputs['source_2'] = source_b.output
    failing_macro.inputs['source_3'] = source_c.output

    # Addint
    add = network.create_node('fastr/math/AddInt:1.0', tool_version='1.0', id="add")

    # Create sink
    sink = network.create_sink('Int', id='sink')

    # Adjust constants(non required inputs) in macro network
    #  add_multiple_ints_node.inputs['const_addint1_value2__add_multiple_ints_1'] = 1234, #input.output
    # Link the network
    add.inputs['left_hand'] = failing_macro.outputs['sink_5']
    add.inputs['right_hand'] = (10,)

    sink.inputs['input'] = add.outputs['result']

    return network


def source_data(network):
    fastr.log.info('Creating source data for {}'.format(network.id))
    return {
        'source_a': {'sample_1': 'vfslist://example_data/add_ints/values'},
        'source_b': {'sample_1': 'vfslist://example_data/add_ints/values'},
        'source_c': {'sample_1': 'vfslist://example_data/add_ints/values'},
    }


def sink_data(network):
    return {'sink': 'vfs://tmp/results/{}/result_{{sample_id}}_{{cardinality}}{{ext}}'.format(network.id)}


def main():
    network = create_network()

    # Execute
    network.draw(network.id, draw_dimensions=True, expand_macros=True)
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
