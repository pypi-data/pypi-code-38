# This file is part of Sympathy for Data.
# Copyright (c) 2015-2016, 2017 Combine Control Systems AB
#
# Sympathy for Data is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Sympathy for Data is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Sympathy for Data.  If not, see <http://www.gnu.org/licenses/>.
import unittest
from Gui import graph


class TestGraph(unittest.TestCase):

    def setUp(self):
        pass

    def test_simple_graph(self):
        g = graph.DocumentGraph()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        g.add_edge(v1, v2)
        # + 2 vertices (entry and exit)
        self.assertEqual(len(g.vertices()), 2 + 2)
        self.assertEqual(len(v1.outputs()), 1)
        self.assertEqual(len(v2.inputs()), 1)

    def test_cycle_detection(self):
        g = graph.DocumentGraph()
        v1 = g.add_vertex()
        v2 = g.add_vertex()
        g.add_edge(v1, v2)

        cycle_detector = graph.CycleDetectionAlgorithm()
        self.assertFalse(cycle_detector.find_cycle(v1, v2, g))

        v3 = g.add_vertex()
        g.add_edge(v2, v3)
        g.add_edge(v3, v1)
        self.assertTrue(cycle_detector.find_cycle(v1, v2, g))

    def test_depth_first_search(self):
        # We test for crash only
        g = graph.DocumentGraph()
        v = [g.add_vertex() for i in range(6)]
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (3, 5), (4, 5)]
        [g.add_edge(v[i], v[j]) for i, j in edges]
        dfs_context = graph.DepthFirstSearchContext(g)

        dfs = graph.DepthFirstSearch()
        dfs.search(v[0], dfs_context)
        print(dfs_context)

    def test_topological_sort(self):
        # We test for crash only
        g = graph.DocumentGraph()
        v = [g.add_vertex() for i in range(6)]
        edges = [(0, 1), (0, 2), (1, 3), (1, 4), (2, 4), (3, 5), (4, 5)]
        [g.add_edge(v[i], v[j]) for i, j in edges]
        ts_context = graph.TopologicalSortContext(g)
        ts = graph.TopologicalSort()
        ts.sort_from_vertex(v[0], ts_context)

        for v1, v2 in zip(v[:-1], v[1:]):
            self.assertTrue(
                ts_context.dependency_group[v2] >=
                ts_context.dependency_group[v1])

if __name__ == '__main__':
    unittest.main()
