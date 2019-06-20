from visualise_spacy_pattern import util
import pydot


DEFAULT_NODE_ATTRS = {
    'color': 'cyan',
    'shape': 'box',
    'style': 'rounded',
    'fontname': 'palatino',
    'fontsize': 10,
    'penwidth': 2
}


def get_node_text(pattern_element):
    feature_dict = util.get_feature_dict(pattern_element)
    feature_text = ['{0} - {1}'.format(k, v) for k, v in feature_dict.items()]
    feature_text = '\n'.join(feature_text)
    node_text = feature_text
    return node_text


def get_node_texts(pattern):
    node_texts = [get_node_text(element) for element in pattern]
    # Count the occurrences of each node text
    unique_texts = set(node_texts)
    text2count = {text: node_texts.count(text) for text in unique_texts}
    # Iterate through, appending the duplicate indicator where appropriate
    new_node_texts = []
    texts_added = []
    for text in node_texts:
        has_duplicates = text2count[text] > 1
        new_node_text = text
        if has_duplicates:
            n_already = texts_added.count(text)
            duplicate_number = n_already + 1
            new_node_text = text + '\n({})'.format(duplicate_number)
        new_node_texts.append(new_node_text)
        texts_added.append(text)
    return new_node_texts


def to_pydot(pattern, edge_labels=['DEP']):
    graph = pydot.Dot(graph_type='graph')
    # Create and add nodes
    node_objects = {}
    for pattern_element in pattern:
        node_name = util.get_node_name(pattern_element)
        node_text = get_node_text(pattern_element)
        plot_attrs = {
            **DEFAULT_NODE_ATTRS,
            'name': node_name,
            'label': node_text,
        }
        node = pydot.Node(**plot_attrs)
        node_objects[node_name] = node
        graph.add_node(node)

    # Add edges
    for pattern_element in pattern:
        nbor_name = util.get_nbor_name(pattern_element)
        if not nbor_name:
            continue
        node_name = util.get_node_name(pattern_element)
        node = node_objects[node_name]
        nbor = node_objects[nbor_name]
        rel = util.get_rel(pattern_element)
        if not rel:
            continue
        if rel == '>':
            edge = pydot.Edge(nbor, node)
        elif rel == '<':
            edge = pydot.Edge(node, nbor)
        else:
            print('Warning: rel type {} unhandled. Results maybe be incorrect.'.format(rel))
            edge = pydot.Edge(node, nbor)
        graph.add_edge(edge)

    return graph
