#!/usr/bin/env python3

# stdlib and other necessary imports
import unittest
from pathlib import Path
import argparse
import random
import sys
from matplotlib import pyplot as plt
import networkx as nx

# figure out the path of this module and import the library to work with
import sys
sys.path.append(str((Path(__file__).parent.resolve() / '..').resolve()))
from libcolgraph.libpy import *

# set default test file or try to infer testfile from commandline args
try:
    k = int(sys.argv[1])
except IndexError:
    k = 3
try:
    test_file = str(Path(*Path(sys.argv[2]).parts[1:]))
except IndexError:
    # test_file = 'input/g1.in'
    test_file = 'input/bipartite_test_graph0.in'

# execute if file called directly
if __name__ == '__main__':
    rel = Path(__file__).parent

    # construct a base graph
    graph = BaseGraph()
    graph.load_txt(rel / test_file)

    # construct a coloring graph from the base graph
    colgraph = graph.build_coloring_graph(k)

    # do some drawing
    draw_fn = nx.draw
    kwargs = dict(with_labels=1, node_size=1024, font_size=10)

    plt.subplot(1, 2, 1)
    graph.draw(draw_fn, **kwargs)
    plt.title(test_file + '\n' + str(graph))

    plt.subplot(1, 2, 2)
    colgraph.draw(draw_fn, **kwargs)
    plt.title(str(colgraph))

    # if non-interactive, explicitly show the plot
    plt.show()
