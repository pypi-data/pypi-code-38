from itertools import product

import networkx as nx

from magine.networks.exporters import nx_to_igraph


def calc(i):
    i, j = i
    if i in nodes:
        n1 = g.vs.select('vertex_label' == i).indices[0]
        n2 = g.vs.select('vertex_label' == j).indices[0]
        return g.maxflow(n1, n2).value
    else:
        return 0


if __name__ == '__main__':
    dna = reactome_only.sig.term_to_genes('dna repair')
    apoptosis = reactome_only.sig.term_to_genes('apoptosis')
    cc = reactome_only.sig.term_to_genes('cell cycle')
    key_nodes = set(dna).union(apoptosis).union(cc)
    nodes = set(network.nodes)
    sub_g = network.subgraph(key_nodes.intersection(nodes))
    g = nx_to_igraph(sub_g)
    nx.set_node_attributes(sub_g, 1, 'capacity')
    nx.set_node_attributes(sub_g, 1, 'flow')

    print(sum(map(calc, product(dna, cc))))
    print(sum(map(calc, product(dna, apoptosis))))
    print(sum(map(calc, product(cc, apoptosis))))

    print(sum(map(calc, product(cc, dna))))
    print(sum(map(calc, product(apoptosis, dna))))
    print(sum(map(calc, product(apoptosis, cc))))
