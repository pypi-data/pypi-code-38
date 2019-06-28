import networkx as nx
from magine.networks.utils import subtract_network_from_network
import matplotlib.pyplot as plt


ecn = nx.read_gml('canonical_kegg_hmdb_biogrid_reactome_signor.gml')
ddn = nx.read_gpickle('BaseData/cisplatin_based_network.p')


subtracted_net = subtract_network_from_network(ddn, ecn)

nx.write_gml(subtracted_net, 'subtracted_network.gml')


tmp_g = subtracted_net.to_undirected()
sorted_graphs = sorted(nx.connected_component_subgraphs(tmp_g), key=len,
                       reverse=True)
node_list = []
for i in sorted_graphs:
    node_list.append(len(i.nodes))


plt.hist(node_list)