import networkx as nx
import pandas as pd


g = nx.read_gpickle('background_network.p.gz')

all_nodes = [None] * len(g.nodes)
counter = 0
for i, d in g.nodes(data=True):
    d['node'] = i
    all_nodes[counter] = d
    counter += 1
df = pd.DataFrame(all_nodes[:counter])
df.to_csv('nodes.csv.gz', compression='gzip', encoding='utf8')


all_edges = [None] * len(g.edges)
counter = 0
for i, j,  d in g.edges(data=True):
    d['source'] = i
    d['target'] = j
    all_edges[counter] = d
    counter += 1
df = pd.DataFrame(all_edges[:counter])
df.to_csv('edges.csv.gz', compression='gzip', encoding='utf8')




edge_types = set()
all_edge_types = set()
count = 0
for i, j, data in g.edges(data=True):
    e_type = data['interactionType']
    edge_types.add(e_type)
    for j in e_type.split('|'):
        all_edge_types.add(j)

for i in sorted(edge_types):
    print(i)

for i in sorted(all_edge_types):
    print(i)

def count_edge(edge_type):
    count = 0
    for i, j, data in g.edges(data=True):
        if edge_type == data['interactionType']:
            count += 1
    print("{}  = {}".format(edge_type, count))
    return edge_type, count
    # print(g.number_of_edges())


print("Total number of edges = {}".format(g.number_of_edges()))
print("# edge labels = {}".format(len(edge_types)))
print("Unique edge labels = {}".format(len(all_edge_types)))
# get_catalyze_genes()
count_edge('chemical')
count_edge('binding')
count_edge('indirect')

out = [count_edge(i) for i in sorted(edge_types)]
import pandas as pd
df = pd.DataFrame(out, columns=['edge', 'count' ])
df.sort_values('count', inplace=True)
print(df)
