from csirtg_indicator import Indicator

import networkx as nx
import os
from pprint import pprint

PATH = os.getenv('GEXF_PATH', 'indicators.gexf')


def get_lines(data, path=PATH, **kwargs):
    g = nx.Graph()

    if not isinstance(data, list):
        data = [data]

    for i in data:
        g.add_node(i['indicator'], itype=i['itype'])
        for a in ['cc']:
            if not i.get(a):
                continue

            g.add_node(i[a])
            g.add_edge(i['indicator'], i[a])

    nx.write_gexf(g, path, prettyprint=True)
    return ['Graph generated successfully: %s' % path]
