#!/usr/bin/env python3

import unittest
from pathlib import Path
import argparse
import random

import sys
sys.path.append(str((Path(__file__).parent.resolve() / '..').resolve()))

from libcolgraph import *


# test_file = 'input/g1.in'
test_file = 'input/bipartite_test_graph0.in'


class TestBaseGraph(unittest.TestCase):

    def setUp(self):
        '''
        initialize
        '''
        self.rel = Path(__file__).parent


    def test_load_txt(self):
        '''
        tests loading graph representation from an adjacency matrix
        saved in a text file
        '''
        graph = Graph.BaseGraph()
        graph.load_txt(self.rel / test_file)
        with (self.rel / Path(test_file)).open() as f:
            n_init = int(f.readline())
            n_act = len(f.readlines())
        self.assertTrue(len(graph) == n_init)
        self.assertTrue(len([*graph.get_vertices()]) == n_act)


    def test_get_some_vertex(self):
        '''
        tests getting some vertex of the graph
        '''
        graph = Graph.BaseGraph()
        graph.load_txt(self.rel / test_file)
        v = graph.get_some_vertex()
        self.assertEqual(graph[v[ID]], v)


    def test_get_vertex(self):
        '''
        tests getting some vertex of the graph
        '''
        graph = Graph.BaseGraph()
        graph.load_txt(self.rel / test_file)
        v = graph.get_vertex(random.randint(0, len(graph)-1))
        self.assertEqual(graph[v[ID]], v)


    def test_build_coloring_graph(self):
        '''
        tests building of a ColoringGraph from a BaseGraph
        '''
        graph = Graph.BaseGraph()
        graph.load_txt(self.rel / test_file)
        colgraph = graph.build_coloring_graph(3, verbose=0)



class TestColoringGraph(unittest.TestCase):

    def setUp(self):
        '''
        initialize
        '''
        self.rel = Path(__file__).parent
        self.graph_ = Graph.BaseGraph()
        self.graph_.load_txt(self.rel / test_file)
        self.graph = self.graph_.build_coloring_graph(k=3, verbose=False)


    def test_get_some_vertex(self):
        '''
        tests getting some vertex of the graph
        '''
        graph = self.graph
        v = graph.get_some_vertex()
        self.assertEqual(graph[v[NAME]], v)


    def test_get_vertex(self):
        '''
        tests getting some vertex of the graph
        '''
        graph = self.graph
        keys = [*graph.vertices.keys()]
        v = graph.get_vertex(keys[random.randint(0, len(graph)-1)])
        self.assertEqual(graph[v[NAME]], v)


    def test_get_neighbors(self):
        '''
        tests getting some vertex of the graph
        '''
        graph = self.graph
        v = graph.get_some_vertex()
        nbrs = graph.get_neighbors(v)
        for nbr in nbrs:
            nbrs_ = set(graph.get_neighbors(nbr))
            self.assertIn(v, nbrs_)


if __name__ == '__main__':
    unittest.main(verbosity=2)
