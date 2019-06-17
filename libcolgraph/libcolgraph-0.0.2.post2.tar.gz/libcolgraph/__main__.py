#!/usr/bin/env python3

# stdlib
import argparse
from collections import defaultdict
from pathlib import Path
# installed packages
from tqdm import tqdm
import networkx as nx
from pyvis.network import Network
from matplotlib import pyplot as plt
# this package
from libcolgraph import *



def sep(infostr=''):
    '''
    a visual separator printer
    '''
    print()
    print('='*80)
    print(infostr, '\n')


def make_nx(g):
    '''
    returns a NetworkX graph from g
    '''
    G = nx.Graph()
    # G.add_nodes_from(self.vertices.keys())
    for v in g.get_vertices():
        G.add_node(v.get_name())
        for nbr in v.get_neighbors():
            G.add_edge(v.get_name(), nbr)
            # G.add_edge(nbr, v.get_name())
    return G


def nxdraw(g, draw_fn=nx.draw, **kwargs):
    '''
    helper method to draw graph using networkx
    '''
    G = make_nx(g)
    draw_fn(G, **kwargs)


def pyvisdraw(g, title='', **kwargs):
    '''
    use pyvis to draw graph
    '''
    net = Network(height='100%', width='100%', bgcolor='#222222',
                  font_color='white', **kwargs)
    # net = Network(**kwargs)
    net.barnes_hut()
    net.from_nx(make_nx(g))
    # net.show_buttons(filter_=['physics'])
    # net.toggle_physics(1)
    Path('~/libcolgraph').expanduser().mkdir(parents=True, exist_ok=True)
    path = Path('~/libcolgraph/{}_{}.html'.format(title, len(g))).expanduser()
    net.show(str(path))



def plotfromfile():
    '''
    main method
    '''
    parser = argparse.ArgumentParser()
    parser.add_argument('INPUT_GRAPH', type=str,
                        help='read in BaseGraph from adjacency matrix file')
    parser.add_argument('-k', '--colors', type=int, default=3,
                        help='number of colors to use to create ColoringGraph')
    parser.add_argument('-v', '--verbosity', action='count', default=0,
                        help='set output verbosity')
    parser.add_argument('--no-bg', help='hide BaseGraph?',
                        action='store_true')
    parser.add_argument('--no-cg', help='hide ColoringGraph?',
                        action='store_true')
    parser.add_argument('--no-mbg', help='hide meta BaseGraph?',
                        action='store_true')
    parser.add_argument('--no-mcg', help='hide meta ColoringGraph?',
                        action='store_true')
    args = parser.parse_args()

    # kwargs = dict(with_labels=1, node_size=1024, font_size=10)

    bg = BaseGraph()
    # bg.load_txt('in/hexmod.in')
    bg.load_txt(args.INPUT_GRAPH)
    if args.verbosity:
        print('loaded {} to base graph {}'.format(args.INPUT_GRAPH, bg))
    if not args.no_bg:
        pyvisdraw(bg, 'bg')

    k = args.colors
    cg = bg.build_coloring_graph(k)
    if args.verbosity:
        print('{} leads to coloring graph {} with k={}'.format(bg, cg, k))
    if not args.no_cg:
        pyvisdraw(cg, 'cg')

    mbg = bg.tarjans()
    if args.verbosity:
        print('{} leads to meta base graph {}'.format(bg, mbg))
    if not args.no_mbg:
        pyvisdraw(mbg, 'mbg')

    mcg = cg.tarjans()
    if args.verbosity:
        print('{} leads to meta coloring graph {}'.format(bg, mcg))
    if not args.no_mcg:
        pyvisdraw(mcg, 'testmcg')


def main():
    '''
    '''
    pass


if __name__ == '__main__':
    pass
    # main()
    # plotfromfile()
