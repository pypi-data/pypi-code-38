import os
import networkx as nx
from magine.data.storage import network_data_dir
from magine.networks.utils import delete_disconnected_network, \
    add_attribute_to_network, compose

aba_kegg = nx.read_gpickle(
    os.path.join(network_data_dir, '{}_all_of_kegg.p.gz'.format('abal'))
)

human_kegg = nx.read_gpickle(
    os.path.join(network_data_dir, '{}_all_of_kegg.p.gz'.format('hsa'))
)
background_human = nx.read_gpickle('background_network.p.gz')


delete_disconnected_network(aba_kegg)
delete_disconnected_network(human_kegg)
delete_disconnected_network(background_human)

nx.write_gml(aba_kegg, 'aba1.gml')
nx.write_gml(human_kegg, 'hsa.gml')
nx.write_gml(background_human, 'background_hsa.gml')

quit()




h_nodes = set(human_kegg.nodes())
h_edges = set(human_kegg.edges())

a_nodes = set(aba_kegg.nodes())
a_edges = set(aba_kegg.edges())


print("Human")
print(len(h_nodes))
print(len(human_kegg.edges()))
print("ABA")
print(len(a_nodes))
print(len(aba_kegg.edges()))

print("intersection")
n_intersection = h_nodes.intersection(a_nodes)
e_intersection = h_edges.intersection(a_edges)
print(len(n_intersection))
print(len(e_intersection))

aba_kegg = add_attribute_to_network(aba_kegg, a_nodes, 'species', 'aba1')
human_kegg = add_attribute_to_network(human_kegg, h_nodes, 'species', 'hsa')

entire_network = compose(aba_kegg, human_kegg)
delete_disconnected_network(entire_network)
print(len(entire_network.nodes()))
print(len(entire_network.edges()))

nx.write_gml(entire_network, 'combined_network.gml')