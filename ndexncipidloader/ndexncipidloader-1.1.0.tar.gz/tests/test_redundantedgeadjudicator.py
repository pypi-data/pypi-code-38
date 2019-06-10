#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `RedundantEdgeAdjudicator` class."""

import os
import tempfile
import shutil

import unittest
import mock
from mock import MagicMock

from ndexncipidloader.loadndexncipidloader import RedundantEdgeAdjudicator
from ndex2.nice_cx_network import NiceCXNetwork

class TestRedundantEdgeAdjudicator(unittest.TestCase):
    """Tests for `RedundantEdgeAdjudicator` class."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_get_description(self):
        adjud = RedundantEdgeAdjudicator()
        self.assertTrue('Removes' in adjud.get_description())

    def test_remove_nonexistant_edge(self):
        adjud = RedundantEdgeAdjudicator()
        self.assertTrue('Removes' in adjud.get_description())
        net = NiceCXNetwork()
        adjud._remove_edge(net, 1)

    def test_remove_edge_no_attributes(self):
        adjud = RedundantEdgeAdjudicator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        self.assertEqual('foo', net.get_edge(edgeid)['i'])
        adjud._remove_edge(net, edgeid)
        self.assertEqual(None, net.get_edge(edgeid))

    def test_remove_edge_with_attributes(self):
        adjud = RedundantEdgeAdjudicator()
        net = NiceCXNetwork()
        edgeid = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='foo')
        net.set_edge_attribute(edgeid, 'attr1', 'someval')
        self.assertEqual('someval', net.get_edge_attribute(edgeid,
                                                           'attr1')['v'])
        self.assertEqual('foo', net.get_edge(edgeid)['i'])
        adjud._remove_edge(net, edgeid)
        self.assertEqual(None, net.get_edge(edgeid))
        self.assertEqual((None, None),
                         net.get_edge_attribute(edgeid, 'attr1'))

    def test_add_to_edge_map(self):
        adjud = RedundantEdgeAdjudicator()
        edgemap = {}
        adjud._add_to_edge_map(edgemap, 0, 1, 2)
        self.assertEqual({0}, edgemap[1][2])
        self.assertEqual({0}, edgemap[2][1])
        adjud._add_to_edge_map(edgemap, 0, 1, 2)
        self.assertEqual({0}, edgemap[1][2])
        self.assertEqual({0}, edgemap[2][1])
        adjud._add_to_edge_map(edgemap, 1, 1, 2)
        self.assertEqual({0, 1}, edgemap[1][2])
        self.assertEqual({0, 1}, edgemap[2][1])

    def test_build_edge_map_single_edge_of_each_type(self):
        adjud = RedundantEdgeAdjudicator()
        net = NiceCXNetwork()

        # try empty network
        neighbor, controls, other = adjud._build_edge_map(net)
        self.assertEqual({}, neighbor)
        self.assertEqual({}, controls)
        self.assertEqual({}, other)

        # try network with single neighbor, controls, and an another edge
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')
        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')
        oid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='somethingelse')
        neighbor, controls, other = adjud._build_edge_map(net)
        self.assertEqual(nid, neighbor[0][1])
        self.assertEqual(nid, neighbor[1][0])
        self.assertEqual({cid}, controls[0][1])
        self.assertEqual({oid}, other[0][1])

    def test_build_edge_map_multiple_edges_of_each_type(self):
        # try network with multiple neighbor, controls, and an another edge
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')
        nidtwo = net.create_edge(edge_source=2, edge_target=3,
                                 edge_interaction='neighbor-of')
        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')
        cidtwo = net.create_edge(edge_source=3, edge_target=4,
                                 edge_interaction='controls-state-change-of')

        oid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='somethingelse')
        oidtwo = net.create_edge(edge_source=5, edge_target=6,
                                 edge_interaction='anotherthingy')
        neighbor, controls, other = adjud._build_edge_map(net)
        self.assertEqual(nid, neighbor[0][1])
        self.assertEqual(nid, neighbor[1][0])
        self.assertEqual(nidtwo, neighbor[2][3])
        self.assertEqual(nidtwo, neighbor[3][2])
        self.assertEqual({cid}, controls[0][1])
        self.assertEqual({cidtwo}, controls[3][4])
        self.assertEqual({oid}, other[0][1])
        self.assertEqual({oidtwo}, other[5][6])

    def test_remove_if_redundant_with_no_citation_on_edge(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')
        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        adjud._remove_if_redundant(net, nid, [cid])

        self.assertEqual(None, net.get_edge(nid))

    def test_remove_if_redundant_with_citation_and_other_lacks_citation(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:123'], type='list_of_string')

        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        adjud._remove_if_redundant(net, nid, [cid])
        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])

    def test_remove_if_redundant_with_different_citations(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:123'], type='list_of_string')

        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        net.set_edge_attribute(cid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:444'], type='list_of_string')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        adjud._remove_if_redundant(net, nid, [cid])
        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])

    def test_remove_if_redundant_with_same_citations(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:4','pubmed:123'],
                               type='list_of_string')

        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        net.set_edge_attribute(cid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:123', 'pubmed:4'],
                               type='list_of_string')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        adjud._remove_if_redundant(net, nid, [cid])
        self.assertEqual(None, net.get_edge(nid))

    def test_remove_if_redundant_mergecitations_true(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:4', 'pubmed:123'],
                               type='list_of_string')

        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        adjud._remove_if_redundant(net, nid, [cid], mergecitations=True)
        self.assertEqual(None, net.get_edge(nid))
        res = net.get_edge_attribute(cid,
                                     RedundantEdgeAdjudicator.CITATION)
        res['v'].sort()
        self.assertEqual(['pubmed:123','pubmed:4'], res['v'])

    def test_remove_if_redundant_with_multiple_edges_same_citations(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:4', 'pubmed:123'],
                               type='list_of_string')

        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        net.set_edge_attribute(cid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:555', 'pubmed:4'],
                               type='list_of_string')

        cidtwo = net.create_edge(edge_source=0, edge_target=1,
                                 edge_interaction='controls-state-change-of')

        net.set_edge_attribute(cidtwo,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:4', 'pubmed:123'],
                               type='list_of_string')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        adjud._remove_if_redundant(net, nid, [cid, cidtwo])
        self.assertEqual(None, net.get_edge(nid))

    def test_update_none_passed_in(self):
        adjud = RedundantEdgeAdjudicator()
        self.assertEqual(['Network passed in is None'], adjud.update(None))

    def test_basic_network(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        net.set_edge_attribute(cid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:123'], type='list_of_string')

        oid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='someother')
        net.set_edge_attribute(oid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:123'], type='list_of_string')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        self.assertEqual('controls-state-change-of', net.get_edge(cid)['i'])
        self.assertEqual('someother', net.get_edge(oid)['i'])

        self.assertEqual([], adjud.update(net))
        self.assertEqual(None, net.get_edge(nid))
        self.assertEqual(None, net.get_edge(cid))
        self.assertEqual('someother', net.get_edge(oid)['i'])

    def test_basic_network_where_neighbor_of_citations_merges(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator()
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:5'], type='list_of_string')
        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        oid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='someother')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        self.assertEqual('controls-state-change-of', net.get_edge(cid)['i'])
        self.assertEqual('someother', net.get_edge(oid)['i'])

        self.assertEqual([], adjud.update(net))
        self.assertEqual(None, net.get_edge(nid))
        self.assertEqual(None, net.get_edge(cid))
        self.assertEqual('someother', net.get_edge(oid)['i'])
        res = net.get_edge_attribute(oid,
                                     RedundantEdgeAdjudicator.CITATION)
        res['v'].sort()
        self.assertEqual(['pubmed:5'], res['v'])

    def test_basic_network_where_neighbor_of_citations_merges_disabled(self):
        net = NiceCXNetwork()
        adjud = RedundantEdgeAdjudicator(disablcitededgemerge=True)
        nid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='neighbor-of')

        net.set_edge_attribute(nid,
                               RedundantEdgeAdjudicator.CITATION,
                               ['pubmed:5'], type='list_of_string')
        cid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='controls-state-change-of')

        oid = net.create_edge(edge_source=0, edge_target=1,
                              edge_interaction='someother')

        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        self.assertEqual('controls-state-change-of', net.get_edge(cid)['i'])
        self.assertEqual('someother', net.get_edge(oid)['i'])

        self.assertEqual([], adjud.update(net))
        self.assertEqual('neighbor-of', net.get_edge(nid)['i'])
        self.assertEqual(None, net.get_edge(cid))
        self.assertEqual('someother', net.get_edge(oid)['i'])
        res = net.get_edge_attribute(nid,
                                     RedundantEdgeAdjudicator.CITATION)
        res['v'].sort()
        self.assertEqual(['pubmed:5'], res['v'])
        res = net.get_edge_attribute(oid,
                                     RedundantEdgeAdjudicator.CITATION)

        self.assertEqual((None, None), res)

