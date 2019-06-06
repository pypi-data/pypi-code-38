import pandas
import pickle
import itertools
import networkx as nx

from urllib.request import urlopen


def add_term_to_node(node, l):
    fs = l.split(':', 1)
    if fs[0] not in node:
        node[fs[0]] = fs[1].strip()
    else:
        node[fs[0]] += "|" + fs[1].strip()
    return node


def read_go_node(fin):
    node = {}
    for line in fin:
        line = line.strip()
        if not line:
            break
        else:
            node = add_term_to_node(node, line)
    return node['id'], node


def create_edges(node):
    if 'is_a' in node:
        for a in node['is_a'].split('|'):
            yield (a.split(' ')[0].strip(), node['id'])
    if 'relationship' in node:
        for b in node['relationship'].split('|'):
            if 'part_of' in b:
                yield (b.split(' ')[1].strip(), node['id'])


def parse_go_obo(go_obo_file):
    """
    Parse GO obo file
    :param go_obo_file: GO obo file. Exmaple: http://current.geneontology.org/ontology/go.obo
    :return: An array with GO, GO name and GO space
    """
    with open(go_obo_file, 'r') as fin:
        for line in fin:
            line = line.strip()
            if line == '[Term]':
                id, node = read_go_node(fin)
                if 'is_obsolete' not in node:
                    edges = create_edges(node)
                    yield (id, node), edges


def create_go_graph(go_obo_file):
    """
    Creat the GODB data structure from the GO obo file
    :param go_obo_file: GO obo file. Exmaple: http://current.geneontology.org/ontology/go.obo
    :return: GODB data structure
    """
    go = nx.DiGraph()
    entries = parse_go_obo(go_obo_file)
    nodes, edges = zip(*entries)
    go.add_nodes_from(nodes)
    go.add_edges_from(itertools.chain.from_iterable(edges))

    # Creating graph roots from namespace
    go.graph['roots'] = {data['name']: n for n, data in go.node.items()
                         if data['name'] == data['namespace']}

    # Adding depth to the nodes
    for root in go.graph['roots'].values():
        for n, depth in nx.shortest_path_length(go, root).items():
            node = go.node[n]
            node['depth'] = min(depth, node.get('depth', float('inf')))

    alt_id = []
    for n in go.node:
        if 'alt_id' in go.node[n]:
            for a in go.node[n]['alt_id'].split('|'):
                alt_id.append([n, a])
    alt_id = pandas.DataFrame(alt_id, columns=['term', 'alt_id'])

    return {
        'graph': go.reverse(),
        'alt_id': alt_id,
        'M': 0
    }


def update_go_graph(godb, values, attribute):
    """
    Up date the node attribute with the values
    :param godb: GODB data structure
    :param values: defaultdict(set) with GO terms as key and set of genes names as values
    :param attribute: node attribute name
    :return: GODB data structure
    """
    for n in nx.topological_sort(godb['graph']):
        current = godb['graph'].node[n].setdefault(attribute, set())
        current.update(values.get(n, set()))
        for p in godb['graph'][n]:
            godb['graph'].node[p].setdefault(attribute, set()).update(current)
    terms, nodes = zip(*godb['graph'].nodes(data=True))
    godb['M'] = len({x for n in nodes for x in n['genes']})
    return godb


def load_goenrichdb(source):
    """
    Load the goenrichment database from a local file or from an URL
    :param source: Local file path or URL
    :return: GODB data structure
    """
    print('Loading go enrichment DB from: ' + source)
    if source.startswith('http') or source.startswith('ftp'):
        return pickle.load(urlopen(source))
    else:
        return pickle.load(open(source, "rb"))
