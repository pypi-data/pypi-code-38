import fastr


def create_network():
    network = fastr.create_network('auto_prefix_test')

    const = network.create_constant(fastr.datatypes.Int, [1, 2, 3], id='const')
    source = network.create_source(fastr.datatypes.Int, id='source')

    node_m_p = network.create_node('fastr/util/AutoPrefixTest:1.0', tool_version='1.0', id='m_p')
    node_a_p = network.create_node('fastr/util/AutoPrefixTest:1.0', tool_version='1.0', id='a_p')
    node_m_n = network.create_node('fastr/util/AutoPrefixNegateTest:1.0', tool_version='1.0', id='m_n')
    node_a_n = network.create_node('fastr/util/AutoPrefixNegateTest:1.0', tool_version='1.0', id='a_n')

    sink_m_p = network.create_sink('Int', id='sink_m_p')
    sink_a_p = network.create_sink('Int', id='sink_a_p')
    sink_m_n = network.create_sink('Int', id='sink_m_n')
    sink_a_n = network.create_sink('Int', id='sink_a_n')

    for node in [node_m_p, node_a_p, node_m_n, node_a_n]:
        node.inputs['left_hand'] = source.output
        node.inputs['right_hand'] = const.output

    sink_m_p.input = node_m_p.outputs['multiplied']
    sink_m_n.input = node_m_n.outputs['multiplied']
    sink_a_n.input = node_a_n.outputs['added']
    sink_a_p.input = node_a_p.outputs['added']

    return network


def source_data(network):
    return {'source': [5]}


def sink_data(network):
    return {
        'sink_a_n': 'vfs://tmp/results/{network}/{{node}}_{{sample_id}}'.format(network=network.id),
        'sink_a_p': 'vfs://tmp/results/{network}/{{node}}_{{sample_id}}'.format(network=network.id),
        'sink_m_p': 'vfs://tmp/results/{network}/{{node}}_{{sample_id}}'.format(network=network.id),
        'sink_m_n': 'vfs://tmp/results/{network}/{{node}}_{{sample_id}}'.format(network=network.id),
    }


def main():
    network = create_network()
    network.save('auto_prefix_test.json')

    # Execute
    network.draw(network.id, draw_dimensions=True)
    network.execute(source_data(network), sink_data(network))


if __name__ == '__main__':
    main()
